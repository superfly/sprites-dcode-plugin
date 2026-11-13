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

### `sprites`

Two skills that teach the agent when and how to use a Sprite:

- **`/sprites:sandbox`**: run risky, experimental, or untrusted work in an isolated Sprite instead of the local machine.
- **`/sprites:checkpoint`**: snapshot a Sprite before destructive operations and roll back when needed.

The skills drive Sprites through the `sprites-tools` tools below when that plugin is installed, and through the [Sprites CLI](https://docs.sprites.dev) (`sprite`) otherwise. Install one of the two.

<details>
<summary>Where did the MCP server go?</summary>

Earlier versions of this plugin (0.2.0 and before) also connected the hosted Sprites MCP server at `https://sprites.dev/mcp`, using a `SPRITES_TOKEN` bearer token. That endpoint is being retired; Sprites MCP tools now live in the Fly MCP at `https://mcp.fly.io`, which signs in with browser OAuth only. dcode cannot complete that flow today: its MCP client omits `token_endpoint_auth_method` during dynamic client registration, and the authorization server accepts only `none`. This plugin will ship the Fly MCP once dcode (or its MCP SDK) registers with an accepted method.

After updating, `/mcp` no longer lists a `sprites` server. Install `sprites-tools` or the Sprites CLI so the skills have a way to reach Sprites; `sprites-tools` reads the same `SPRITES_TOKEN`.

</details>

### `sprites-tools` (experimental)

A [Python extension](https://docs.langchain.com/oss/deepagents/code/extensions) that registers three model tools backed by the [sprites-py](https://github.com/superfly/sprites-py) SDK:

- `run_in_sprite(command, sprite_name)`: run a shell command in a persistent Sprite.
- `sprite_checkpoint(comment, sprite_name)`: snapshot the Sprite's full machine state.
- `sprite_restore(checkpoint_id, sprite_name)`: roll the Sprite back.

It authenticates with a plain API token, so it also works in headless and CI sessions.

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
- `sprite destroy` permanently deletes a Sprite and its data.
- Checkpoint restore rewinds the entire Sprite; work after the checkpoint is lost.
- `sprites-tools` reads `SPRITES_TOKEN` from the environment and does not write the token anywhere.
- An API token is not restricted by an OAuth consent screen: the tools and the CLI can act on any Sprite the token's organization allows. Prefer a dedicated organization or token for agent use.

## Related

- [Sprites documentation](https://docs.sprites.dev)
- [Deep Agents Code plugins](https://docs.langchain.com/oss/deepagents/code/plugins)

## License

MIT
