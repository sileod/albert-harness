# Albert Harness

Use one `ALBERT_API_KEY` with local coding harnesses and cloud agents.

```sh
export ALBERT_API_KEY=...

albert opencode
albert codex
albert claude

albert spawn opencode gcp
albert spawn hermes hetzner
albert spawn codex sprite
```

The default model is `deepseek-v4-flash`.

## Install

```sh
curl -fsSL https://raw.githubusercontent.com/sileod/albert-harness/main/install.sh | sh
```

This installs `albert` and its Spawn adapter to `~/.local/bin` by default. Override with `ALBERT_INSTALL_DIR`.

## Local harnesses

```sh
albert models
albert opencode --model deepseek-v4-flash
albert codex --model deepseek-v4-flash --full-auto
albert claude --model deepseek-v4-flash -p "review this diff"
```

OpenCode talks to Albert directly through its OpenAI-compatible provider interface.

Codex uses a loopback-only LiteLLM bridge because current Codex speaks the Responses API while Albert exposes Chat Completions. Claude Code uses the same bridge for Anthropic Messages and is experimental.

For Codex and Claude Code:

```sh
python -m pip install 'litellm[proxy]'
```

Arguments not consumed by `albert` are passed through to the harness.

## Spawn

`albert spawn` reuses [OpenRouterLabs/spawn](https://github.com/OpenRouterLabs/spawn) for provisioning and lifecycle management while configuring the remote agent for Albert.

```sh
albert spawn opencode gcp
albert spawn hermes hetzner --fast
albert spawn codex sprite -p "fix the tests"
albert spawn claude digitalocean

albert spawn matrix
albert spawn list
albert spawn status
albert spawn delete
```

The existing Spawn cloud options are passed through, including GCP, Hetzner, DigitalOcean, AWS, Sprite, Daytona, local, and sandbox.

Albert support is strongest for:

| Agent | Albert connection |
|---|---|
| OpenCode | direct OpenAI-compatible API |
| Hermes | direct OpenAI-compatible API |
| Codex | LiteLLM bridge inside the spawned machine |
| Claude Code | LiteLLM bridge inside the spawned machine, experimental |

Other Spawn agents are still available as best-effort passthroughs, but some have OpenRouter-specific provider integrations and may not work with Albert yet.

Spawn support requires `git` and [Bun](https://bun.sh/). On first use, `albert spawn` downloads a pinned Spawn source revision into `~/.cache/albert-harness/spawn`, applies the Albert adapter, and compiles it. Subsequent runs use the cached binary.

To try another Spawn revision:

```sh
ALBERT_SPAWN_REF=main albert spawn matrix
```

## Configuration

```sh
export ALBERT_API_KEY=...
export ALBERT_MODEL=deepseek-v4-flash
export ALBERT_BASE_URL=https://albert.api.etalab.gouv.fr/v1
```

The Albert key stays in the environment. Generated OpenCode and LiteLLM configuration references the environment variable rather than embedding the key.

The default model limits used for OpenCode are a 131072-token context window and 65536-token output limit.

## Development

```sh
python -m unittest discover -s tests -v
python -m py_compile bin/albert bin/albert-spawn
bash -n install.sh
```
