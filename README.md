# Albert Harness

Use the French government's Albert API with coding agents through one small CLI.

The goal is close to OpenRouter's Ori ergonomics: configure one provider once, then launch the harness you already use.

```sh
export ALBERT_API_KEY=...

albert opencode
albert codex
albert claude
```

The default model is `deepseek-v4-flash`.

## Install

```sh
curl -fsSL https://raw.githubusercontent.com/sileod/albert-harness/main/install.sh | sh
```

This installs `albert` to `~/.local/bin` by default. Override with `ALBERT_INSTALL_DIR`.

## Harnesses

```sh
albert models
albert opencode --model deepseek-v4-flash
albert codex --model deepseek-v4-flash --full-auto
albert claude --model deepseek-v4-flash -p "review this diff"
```

OpenCode talks directly to Albert through `@ai-sdk/openai-compatible`, with no proxy in the request path.

Codex speaks the OpenAI Responses API while Albert currently exposes Chat Completions. `albert codex` therefore starts a loopback-only LiteLLM compatibility bridge that translates Responses requests to Albert's `/v1/chat/completions` endpoint.

Claude Code uses the same local bridge for Anthropic Messages and is still experimental.

For Codex and Claude Code:

```sh
python -m pip install 'litellm[proxy]'
```

Arguments not consumed by `albert` are passed through to the harness.

## Isolated execution with Spawn

`albert spawn` is optional. It reuses OpenRouterLabs Spawn for isolated local containers and remote machines while configuring supported agents for Albert.

For a protected local session:

```sh
cd my-project
albert spawn opencode sandbox
```

The current directory is mounted read-write at `/workspace` inside the disposable container, so edits and generated files persist in `my-project` while the rest of the container is thrown away when the session ends.

Use another directory explicitly with:

```sh
albert spawn hermes sandbox --workspace ~/work/experiment
```

Remote execution uses the same command shape:

```sh
albert spawn opencode gcp
albert spawn hermes hetzner --fast
albert spawn codex sprite
```

Albert integration is currently strongest for OpenCode and Hermes. Codex uses a LiteLLM bridge inside the spawned machine. Claude Code uses the same bridge and remains experimental.

Spawn support requires `git` and Bun. The first `albert spawn` invocation downloads and compiles a pinned Spawn revision into `~/.cache/albert-harness/spawn`; later runs reuse the cached binary.

## Configuration

```sh
export ALBERT_API_KEY=...
export ALBERT_MODEL=deepseek-v4-flash
export ALBERT_BASE_URL=https://albert.api.etalab.gouv.fr/v1
```

The Albert key stays in the environment. Generated OpenCode and LiteLLM configuration references the environment variable rather than embedding the key.

## Development

```sh
python -m unittest discover -s tests -v
python -m py_compile bin/albert bin/albert-spawn
bash -n install.sh
```
