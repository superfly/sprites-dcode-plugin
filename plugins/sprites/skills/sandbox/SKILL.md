---
name: sandbox
description: Run commands, experiments, or untrusted code in an isolated Fly.io Sprite instead of the local machine. Use when the user asks to sandbox work, try something risky (unknown scripts, destructive commands, dependency experiments), reproduce a bug in a clean environment, or get a persistent remote Linux environment that survives between sessions.
---

# Run work in a Sprite sandbox

A Sprite is a persistent, named Linux VM on Fly.io. It boots in milliseconds, suspends automatically when idle (a suspended Sprite costs nothing), and keeps its filesystem and installed packages between uses. Use a Sprite instead of the local machine when work is risky, experimental, or needs to persist.

## Prerequisites

This plugin ships the hosted Sprites MCP server (`https://sprites.dev/mcp`), authenticated with the `SPRITES_TOKEN` environment variable. Run `/mcp` to confirm the `sprites` server is connected. If it is not, the variable is probably unset; ask the user to export it and restart, and do not paste tokens into the conversation.

If the MCP server is not available, the [Sprites CLI](https://docs.sprites.dev) is an alternative: `sprite create <name>`, `sprite exec <cmd>`, `sprite destroy <name>`.

## Workflow

1. **Pick a name.** Reuse one Sprite per project when possible, for example `dcode-<project>`. List existing Sprites first (`list_sprites`) and reuse a matching one; its state is still there.
2. **Create if needed.** Create the Sprite with `create_sprite`. Creation takes 1-2 seconds; there is no image to build.
3. **Run commands.** Use the Sprite exec tool to run shell commands. Commands run as a normal Linux user with common toolchains (git, curl, Node.js, Python) available. Long installs are fine; they persist.
4. **Move files.** To seed the sandbox, write files with shell heredocs or `git clone` inside the Sprite. To retrieve results, `cat` files back out through exec output.
5. **Clean up deliberately.** Do NOT destroy the Sprite by default; suspension is free and the state is usually worth keeping. Destroy (`destroy_sprite`) only when the user asks, or for one-off scratch Sprites you created for a single risky command.

## Safety rules

- Never run a command the user wanted sandboxed on the local machine as a fallback. If the Sprite path fails, stop and report.
- `destroy_sprite` permanently deletes the Sprite and its data. Confirm with the user before destroying anything you did not create in this session.
- Before a risky or destructive step inside the Sprite, create a checkpoint first (see the `checkpoint` skill).
- Network access inside the Sprite follows its network policy. If an outbound request is blocked, report it rather than trying to bypass the policy.

## When the current session already runs inside a Sprite

If the environment has a `sprite-env` binary, dcode itself is running inside a Sprite. Local commands are already sandboxed; use `sprite-env checkpoints create --comment "..."` for snapshots instead of creating a second Sprite.
