# Albert Harness

Ori-like launchers for coding agents, initially built for the French government's Albert API and now also supporting NVIDIA NIM.

Configure a provider once, then launch the harness you already use:

```sh
export ALBERT_API_KEY=...
albert opencode
albert codex

export NVIDIA_API_KEY=...
nim opencode
nim codex
```

## Install

```sh
curl -fsSL https://raw.githubusercontent.com/sileod/albert-harness/main/install.sh | sh
```

This installs the `albert` and `nim` launchers to `~/.local/bin` by default. Override with `HARNESS_INSTALL_DIR` (`ALBERT_INSTALL_DIR` is still accepted for compatibility).

## Albert API

The default Albert model is `deepseek-v4-flash`.

```sh
export ALBERT_API_KEY=...

albert models
albert opencode
albert codex --full-auto
albert claude -p "review this diff"
```

OpenCode talks directly to Albert through `@ai-sdk/openai-compatible`, with no proxy in the request path.

Codex and Claude Code use a loopback-only LiteLLM compatibility bridge because Albert exposes Chat Completions while these harnesses use Responses or Anthropic Messages semantics.

```sh
python -m pip install 'litellm[proxy]'
```

Configuration:

```sh
export ALBERT_MODEL=deepseek-v4-flash
export ALBERT_BASE_URL=https://albert.api.etalab.gouv.fr/v1
```

## NVIDIA NIM

NVIDIA provides hosted NIM endpoints at `https://integrate.api.nvidia.com/v1`. The default model here is `openai/gpt-oss-120b`.

```sh
export NVIDIA_API_KEY=...

nim models
nim opencode
nim codex --full-auto
nim claude -p "review this diff"
```

OpenCode talks directly to the NVIDIA hosted API through `@ai-sdk/openai-compatible`.

For compatibility with the hosted API surface, Codex and Claude Code use the same loopback LiteLLM bridge pattern as Albert. The bridge sends Chat Completions upstream through LiteLLM's `custom_openai` provider.

Configuration:

```sh
export NIM_MODEL=openai/gpt-oss-120b
export NIM_BASE_URL=https://integrate.api.nvidia.com/v1
```

This also makes it possible to point `nim` at a compatible self-hosted NIM deployment by changing `NIM_BASE_URL` and `NIM_MODEL`.

## Isolated execution

Spawn support is optional. It provides disposable local Docker sandboxes and remote execution while keeping the same provider configuration.

Protected local sessions persist work in the current directory:

```sh
cd my-project
albert spawn opencode sandbox
# or
nim spawn opencode sandbox
```

The current directory is mounted read-write at `/workspace`. The rest of the container is disposable.

Use a different workspace explicitly:

```sh
albert spawn hermes sandbox --workspace ~/work/experiment
nim spawn hermes sandbox --workspace ~/work/experiment
```

Remote execution uses the same shape:

```sh
albert spawn opencode gcp
nim spawn opencode gcp

albert spawn hermes hetzner --fast
nim spawn hermes hetzner --fast
```

Spawn integration is strongest for OpenCode and Hermes. Codex and Claude use a LiteLLM bridge inside the spawned machine. Spawn support requires `git` and Bun and caches a pinned upstream Spawn build under `~/.cache/albert-harness/`.

## Security

Provider API keys stay in environment variables. Generated OpenCode and LiteLLM configuration references those environment variables rather than embedding the keys.

## Development

```sh
python -m unittest discover -s tests -v
python -m py_compile bin/albert bin/albert-spawn bin/nim bin/nim-spawn
bash -n install.sh
```
