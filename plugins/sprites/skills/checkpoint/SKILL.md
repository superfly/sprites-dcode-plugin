---
name: checkpoint
description: Snapshot and roll back the full machine state of a Fly.io Sprite. Use before risky or destructive operations in a Sprite sandbox (schema migrations, mass refactors, dependency upgrades, running unknown code), or when the user asks to undo, roll back, or restore a sandbox to an earlier state.
---

# Checkpoint and restore a Sprite

A Sprite checkpoint captures the entire filesystem and process state of the VM and completes in under a second. Restoring rewinds the Sprite to that state. Checkpoints make risky agent work reversible.

## When to checkpoint

Create a checkpoint BEFORE:

- Running code or scripts you have not reviewed
- Destructive shell commands (`rm -rf`, database drops, `git reset --hard`)
- Large dependency or system upgrades
- Any step the user calls an experiment

Use a short, specific comment, for example `before dependency upgrade` or `before running user script`.

## Workflow

1. **Create.** Use the `sprite_checkpoint` tool (from the `sprites-tools` plugin) with a descriptive comment, or `sprite checkpoint create -s <name> --comment "..."` with the Sprites CLI. When running inside a Sprite, use `sprite-env checkpoints create --comment "..."` instead.
2. **Note the id.** `sprite_checkpoint` returns the newest id; with the CLI, run `sprite checkpoint list -s <name>` (ids look like `v12`). Report it to the user so they can restore later.
3. **Do the risky work.**
4. **Restore only when needed.** If the work went wrong or the user asks to roll back, restore the checkpoint by id with `sprite_restore` or `sprite restore <id> -s <name>`. Restore rewinds EVERYTHING in the Sprite since that checkpoint, including unrelated files and running processes. Warn the user about what will be lost before restoring if any wanted work happened after the checkpoint.

## Safety rules

- Restore is not selective. If the user only wants some changes undone, prefer targeted fixes (git revert, file edits) over a checkpoint restore.
- Never restore a checkpoint you did not create in this session without confirming with the user first.
- After a restore, re-verify the environment (working directory, running services) before continuing; processes from after the checkpoint no longer exist.
