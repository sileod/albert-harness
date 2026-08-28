# Albert Harness

Use one `ALBERT_API_KEY` with coding harnesses:

```sh
export ALBERT_API_KEY=...
albert opencode
albert codex
albert claude   # experimental
```

The goal is the same ergonomics as OpenRouter's Ori harness launcher, but for the French government's [Albert API](https://albert.api.etalab.gouv.fr/).

## Install

```sh
curl -fsSL https://raw.githubusercontent.com/sileod/albert-harness/main/install.sh | sh
```

This installs `albert` to `~/.local/bin` by default. Override with `ALBERT_INSTALL_DIR`.

`albert` itself only needs Python 3. OpenCode talks to Albert directly. Codex and Claude Code currently need a local protocol bridge because Albert exposes OpenAI Chat Completions while current Codex speaks Responses and Claude Code speaks Anthropic Messages:

```sh
python -m pip install 'litellm[proxy]'
```

Your Albert key is never written to the generated OpenCode or LiteLLM configuration. The runtime references `ALBERT_API_KEY` from the environment.

## Usage

```sh
albert models
albert opencode --model deepseek-v4-flash
albert codex --model deepseek-v4-flash --full-auto
albert claude --model deepseek-v4-flash -p "review this diff"
```

Arguments after the harness options are passed through unchanged. `ALBERT_MODEL` changes the default model. `ALBERT_BASE_URL` can override the API endpoint for development.

The default is the canonical Albert model ID `deepseek-v4-flash`, with a 131072-token context window and 65536-token output limit, matching the current DINUM `albert-code` configuration.

### OpenCode

`albert opencode` injects an inline `provider.albert` configuration via `OPENCODE_CONFIG_CONTENT`. Existing inline configuration is merged rather than discarded. It uses `@ai-sdk/openai-compatible` against:

```text
https://albert.api.etalab.gouv.fr/v1
```

No proxy is involved.

### Codex

Recent Codex versions no longer support Chat Completions providers. `albert codex` therefore starts a loopback-only LiteLLM process that translates Codex's `/v1/responses` traffic to Albert's `/v1/chat/completions`, then launches the installed `codex` binary with temporary CLI config overrides. Nothing is written to `~/.codex/config.toml`.

### Claude Code

`albert claude` uses the same loopback bridge and points Claude Code's Anthropic Messages traffic at it. This path is **experimental** because third-party Messages-to-Chat translation is less mature than the Codex Responses bridge.

## Why not fork Ori?

OpenRouter publishes Ori binaries under Apache-2.0, but its public `ori-releases` repository explicitly says it is a distribution mirror and contains no source. Until the actual source tree is published, this project can reuse the launcher idea and documented behavior, but cannot honestly reuse Ori's harness implementation.

If that source becomes available, the preferred direction is to replace these adapters with a small Albert provider implementation on top of Ori's harness layer.

## Development

```sh
python -m unittest discover -s tests -v
```
