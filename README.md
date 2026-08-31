# Sprites plugins for Deep Agents Code

Plugins that connect [Deep Agents Code](https://docs.langchain.com/oss/deepagents/code/overview) (`dcode`) to [Fly.io Sprites](https://fly.io/sprites): persistent, named Linux sandboxes that boot in milliseconds, suspend at no cost when idle, and support sub-second checkpoint and restore of the full machine state.

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

The MCP server authenticates with a Sprites API token read from the `SPRITES_TOKEN` environment variable:

```bash
export SPRITES_TOKEN=your_token   # create one with the Sprites CLI (https://docs.sprites.dev)
```

Start dcode with the variable set; `/mcp` shows the `sprites` server and its tools.

<details>
<summary>Why not OAuth?</summary>

The hosted server also supports a browser OAuth flow with restricted, consent-scoped tokens, and this plugin used it originally. dcode cannot complete that flow today: its MCP client omits `token_endpoint_auth_method` during dynamic client registration, and the Sprites authorization server accepts only `none` or `client_secret_post`, so registration fails with `invalid_client_metadata` before the browser opens. The plugin returns to OAuth once dcode (or its MCP SDK) registers with an accepted method.

</details>

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
- Both plugins read `SPRITES_TOKEN` from the environment; neither writes the token anywhere.
- An API token is not restricted by an OAuth consent screen: the MCP tools can act on any Sprite the token's organization allows, including `destroy_sprite`. Prefer a dedicated organization or token for agent use.

## Related

- [Sprites documentation](https://docs.sprites.dev)
- [Deep Agents Code plugins](https://docs.langchain.com/oss/deepagents/code/plugins)

## License

MIT
