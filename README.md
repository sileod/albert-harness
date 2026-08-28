# Harness Link

Thin provider adapters for coding harnesses.

Harness Link aims for OpenRouter Ori-like ergonomics: configure a provider once, then launch the coding agent you already use. The agent keeps its normal tools, permissions, sessions, skills, and UI. Harness Link only adapts provider configuration and protocol where necessary.

```sh
export ALBERT_API_KEY=...
albert opencode
albert codex

export NVIDIA_API_KEY=...
nim opencode
nim codex
```

Native provider configuration is preferred. A loopback compatibility bridge is used only when the harness requires a protocol the provider does not expose directly.

## Install

```sh
curl -fsSL https://raw.githubusercontent.com/sileod/albert-harness/main/install.sh | sh
```

This installs the user-facing `albert` and `nim` commands plus their small shared Harness Link runtime to `~/.local/bin` by default. Override with `HARNESS_LINK_INSTALL_DIR` or the legacy `ALBERT_INSTALL_DIR`.

## Albert

The French government's Albert API uses `ALBERT_API_KEY` and defaults to `deepseek-v4-flash`.

```sh
export ALBERT_API_KEY=...

albert models
albert opencode
albert codex --full-auto
albert claude -p "review this diff"
```

OpenCode talks directly to Albert through `@ai-sdk/openai-compatible`.

Codex speaks the OpenAI Responses API while Albert currently exposes Chat Completions. `albert codex` therefore starts a loopback-only LiteLLM bridge. Claude Code uses the same bridge for Anthropic Messages and remains experimental.

For Codex and Claude Code:

```sh
python -m pip install 'litellm[proxy]'
```

Configuration:

```sh
export ALBERT_MODEL=deepseek-v4-flash
export ALBERT_BASE_URL=https://albert.api.etalab.gouv.fr/v1
```

## NVIDIA NIM

NVIDIA's hosted API uses `NVIDIA_API_KEY` and defaults to `openai/gpt-oss-120b`.

```sh
export NVIDIA_API_KEY=...

nim models
nim opencode
nim codex --full-auto
nim claude -p "review this diff"
```

OpenCode talks directly to `https://integrate.api.nvidia.com/v1`. For the hosted API, Codex and Claude use the same loopback compatibility bridge rather than assuming `/v1/responses` or `/v1/messages` is available for every hosted model.

Configuration:

```sh
export NIM_MODEL=openai/gpt-oss-120b
export NIM_BASE_URL=https://integrate.api.nvidia.com/v1
```

## Isolated execution

Spawn integration is optional. It provides disposable local Docker sandboxes and remote machines while keeping the same provider commands.

```sh
cd my-project
albert spawn opencode sandbox
nim spawn opencode sandbox
```

For `sandbox`, the current directory is mounted read-write at `/workspace`. Edits and generated files persist on the host while the rest of the container is disposable.

Use another workspace explicitly:

```sh
albert spawn hermes sandbox --workspace ~/work/experiment
nim spawn opencode sandbox --workspace ~/work/experiment
```

Remote execution keeps Spawn's normal command shape:

```sh
albert spawn opencode gcp
nim spawn hermes hetzner --fast
```

Spawn support requires `git` and Bun. The first invocation downloads and compiles a pinned Spawn revision into the Harness Link cache; later runs reuse it.

## Design

Harness Link stays deliberately small:

1. Native harness configuration when possible.
2. A tiny provider adapter when configuration differs.
3. A loopback bridge only when protocol translation is required.
4. No hidden provider fallback.

Arguments not consumed by Harness Link are passed through to the selected harness.

## Development

```sh
python -m unittest discover -s tests -v
python -m py_compile bin/harness-link bin/harness-link-spawn bin/albert bin/nim bin/albert-spawn bin/nim-spawn
bash -n install.sh
```
