"""Deep Agents Code extension: run commands in a Fly.io Sprite.

Registers `run_in_sprite`, `sprite_checkpoint`, and `sprite_restore` tools
that operate on a persistent, named Sprite sandbox through the
`sprites-py` SDK.

Requirements:
- DEEPAGENTS_CODE_EXPERIMENTAL=1 (Python extensions are experimental)
- SPRITES_TOKEN environment variable (Sprites API token)
- pip install sprites-py

Unlike the hosted Sprites MCP server, this extension authenticates with a
plain API token, which suits headless and CI sessions where an OAuth
browser flow is not available.
"""

from __future__ import annotations

import os

from deepagents_code.extensions import ExtensionAPI

_DEFAULT_SPRITE = "dcode-sandbox"
_COMMAND_TIMEOUT_SECONDS = 300


def _drain(stream) -> None:
    """Consume a checkpoint or restore message stream to completion.

    The operation only completes when the stream is fully read. Raises on
    error messages so tool callers see the failure.
    """
    errors = [m.error or m.data for m in stream if m.type == "error"]
    if errors:
        msg = f"Sprite operation failed: {'; '.join(str(e) for e in errors)}"
        raise RuntimeError(msg)


async def extension(d: ExtensionAPI) -> None:
    # Lazy state: no client or Sprite is created until a tool runs.
    state: dict = {"client": None, "sprites": {}}

    def _sprite(sprite_name: str):
        from sprites import SpritesClient
        from sprites.exceptions import SpriteError

        if state["client"] is None:
            token = os.environ.get("SPRITES_TOKEN")
            if not token:
                msg = (
                    "SPRITES_TOKEN is not set. Create a token with the "
                    "Sprites CLI (https://docs.sprites.dev) and export it."
                )
                raise RuntimeError(msg)
            state["client"] = SpritesClient(token)

        if sprite_name not in state["sprites"]:
            client = state["client"]
            try:
                sprite = client.create_sprite(sprite_name)
            except SpriteError:
                # The Sprite may already exist; reuse it by name.
                sprite = client.get_sprite(sprite_name)
            state["sprites"][sprite_name] = sprite
        return state["sprites"][sprite_name]

    def run_in_sprite(command: str, sprite_name: str = _DEFAULT_SPRITE) -> str:
        """Run a shell command in an isolated, persistent Fly.io Sprite sandbox.

        Use this instead of the local shell for risky, experimental, or
        untrusted commands. The Sprite keeps its filesystem and installed
        packages between calls and between sessions, and suspends at no cost
        when idle.

        Args:
            command: Shell command to run (bash; pipes and globs work).
            sprite_name: Sprite to run in. The default is shared across
                sessions; pass a different name for a separate environment.

        Returns:
            Combined command output followed by the exit code.
        """
        from sprites.exceptions import TimeoutError as SpritesTimeoutError

        sprite = _sprite(sprite_name)
        try:
            result = sprite.run(
                "bash",
                "-lc",
                command,
                capture_output=True,
                timeout=_COMMAND_TIMEOUT_SECONDS,
            )
        except SpritesTimeoutError:
            return f"Command timed out after {_COMMAND_TIMEOUT_SECONDS} seconds"

        output = result.stdout.decode("utf-8", errors="replace")
        stderr = result.stderr.decode("utf-8", errors="replace")
        if stderr.strip():
            output += f"\n<stderr>{stderr.strip()}</stderr>"
        return f"{output}\n[exit code: {result.returncode}]"

    def sprite_checkpoint(comment: str = "", sprite_name: str = _DEFAULT_SPRITE) -> str:
        """Create a checkpoint of a Sprite's full machine state.

        Call this before running risky or destructive commands with
        run_in_sprite so the Sprite can be rolled back.

        Args:
            comment: Short description of the state, for example
                "before dependency upgrade".
            sprite_name: Sprite to checkpoint.

        Returns:
            The id of the newest checkpoint after creation.
        """
        sprite = _sprite(sprite_name)
        _drain(sprite.create_checkpoint(comment))
        checkpoints = sprite.list_checkpoints()
        newest = max(
            (c for c in checkpoints if c.id != "Current"),
            key=lambda c: c.create_time,
        )
        return f"Created checkpoint {newest.id}"

    def sprite_restore(checkpoint_id: str, sprite_name: str = _DEFAULT_SPRITE) -> str:
        """Restore a Sprite to a previous checkpoint.

        This rewinds the ENTIRE Sprite (filesystem and processes) to the
        checkpointed state. Work done after the checkpoint is lost. Confirm
        with the user before restoring.

        Args:
            checkpoint_id: Checkpoint id from sprite_checkpoint, for
                example "v3".
            sprite_name: Sprite to restore.

        Returns:
            A confirmation message.
        """
        import time

        sprite = _sprite(sprite_name)
        # A restore issued immediately after a checkpoint can hit a transient
        # server-side collision while the previous operation finalizes; retry
        # once after a short delay.
        try:
            _drain(sprite.restore_checkpoint(checkpoint_id))
        except RuntimeError:
            time.sleep(5)
            _drain(sprite.restore_checkpoint(checkpoint_id))
        return f"Restored {sprite_name} to checkpoint {checkpoint_id}"

    d.register_tool(run_in_sprite)
    d.register_tool(sprite_checkpoint)
    d.register_tool(sprite_restore)

    def _close() -> None:
        client = state["client"]
        if client is not None:
            client.close()

    d.on_shutdown(_close)
