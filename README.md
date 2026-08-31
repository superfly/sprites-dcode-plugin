# Sprites plugins for Deep Agents Code

Plugins that connect [Deep Agents Code](https://docs.langchain.com/oss/deepagents/code/overview) (`dcode`) to [Fly.io Sprites](https://fly.io/sprites): persistent, named Linux sandboxes that boot in 1-2 seconds, suspend at no cost when idle, and support sub-second checkpoint and restore of the full machine state.

The plugin manifests use the Claude plugin format, so the `sprites` plugin also works with other agents that read `.claude-plugin` manifests.

## Install

```bash
dcode plugin marketplace add superfly/sprites-dcode-plugin
dcode plugin install sprites@sprites
```

Then run `/reload` in an active session, or start a new one.

## Plugins

### `sprites` (recommended)

Connects the hosted [Sprites remote MCP server](https://docs.sprites.dev/integrations/remote-mcp/) (`https://sprites.dev/mcp`) and adds two skills:

- **`/sprites:sandbox`**: run risky, experimental, or untrusted work in an isolated Sprite instead of the local machine.
- **`/sprites:checkpoint`**: snapshot a Sprite before destructive operations and roll back when needed.

The MCP server authenticates with a Fly.io OAuth flow on first use. The default token is restricted: it can only create a limited number of Sprites named `mcp-*`. No API keys go into config files.

### `sprites-tools` (experimental)

A [Python extension](https://docs.langchain.com/oss/deepagents/code/extensions) that registers three model tools backed by the [sprites-py](https://github.com/superfly/sprites-py) SDK:

- `run_in_sprite(command, sprite_name)`: run a shell command in a persistent Sprite.
- `sprite_checkpoint(comment, sprite_name)`: snapshot the Sprite's full machine state.
- `sprite_restore(checkpoint_id, sprite_name)`: roll the Sprite back.

Use this instead of the MCP server for headless or CI sessions where a browser OAuth flow is not available. It authenticates with a plain API token.

Requirements:

```bash
pip install sprites-py
export SPRITES_TOKEN=your_token        # create one with the Sprites CLI
export DEEPAGENTS_CODE_EXPERIMENTAL=1  # Python extensions are experimental
dcode plugin install sprites-tools@sprites
```

Python extensions require `/restart` (not `/reload`) after install.

## Security notes

- An enabled plugin can add instructions and run tools with your user permissions. Review the skills and the extension source before enabling.
- `destroy_sprite` (MCP) permanently deletes a Sprite and its data.
- Checkpoint restore rewinds the entire Sprite; work after the checkpoint is lost.
- The `sprites-tools` extension reads `SPRITES_TOKEN` from the environment; it never writes the token anywhere.

## Related

- [Sprites documentation](https://docs.sprites.dev)
- [`@langchain/sprites`](https://github.com/langchain-ai/deepagentsjs/pull/807) and [`langchain-sprites`](https://github.com/langchain-ai/deepagents/pull/6001): Sprites sandbox backends for the deepagents SDKs
- [Deep Agents Code plugins](https://docs.langchain.com/oss/deepagents/code/plugins)

## License

MIT
