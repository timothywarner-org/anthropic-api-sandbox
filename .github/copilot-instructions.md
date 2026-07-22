# Copilot Instructions

## Commands

All commands use [uv](https://docs.astral.sh/uv/). The package is installed as an editable CLI entry point named `sandbox`.

```bash
uv sync --all-extras          # Install all dependencies (including dev)
uv run sandbox basic "prompt"           # Run basic example
uv run sandbox stream "prompt"          # Run streaming example
uv run sandbox system --persona "role" "prompt"  # Run system prompt example

uv run pytest -v                        # Full test suite
uv run pytest tests/test_config.py -v  # Single test file
uv run pytest -k "test_config_has_sensible_defaults"  # Single test

uv run ruff check src tests            # Lint
uv run ruff format src tests           # Format
uv run ruff format --check src tests   # Format check (CI mode)
```

Tests do **not** require an API key — the smoke tests mock via subprocess and config tests use `monkeypatch`.

## Architecture

```
src/anthropic_api_sandbox/
  config.py       # load_config() → frozen Config dataclass; validates ANTHROPIC_API_KEY
  client.py       # create_client(config) → anthropic.Anthropic instance
  cli.py          # argparse entry point; wires config → client → examples
  examples/
    basic.py        # client.messages.create() → message.content[0].text
    stream.py       # client.messages.stream() → Generator[str]
    system_prompt.py # messages.create() with system= param → text
```

The flow is always: `load_config()` → `create_client(config)` → `examples/<pattern>.run(client, config, ...)`. The CLI is the only consumer; examples are pure functions that accept `(client, config, prompt, ...)` and return text or generators.

## Key Conventions

- **Config is a frozen dataclass** — never mutate it; override `model` at `.env` level via `ANTHROPIC_MODEL`.
- **Default model**: `claude-sonnet-4-20250514`; `max_tokens` defaults to `1024`.
- **Placeholder key guard**: `load_config()` rejects `"your-api-key-here"` explicitly — tests exploit this with `monkeypatch`.
- **Streaming returns a `Generator[str, None, None]`**, not a string. The CLI flushes each chunk with `print(chunk, end="", flush=True)`.
- **Response text extraction**: always `message.content[0].text` (content is a list of blocks).
- **New example pattern**: add a module under `src/anthropic_api_sandbox/examples/`, expose a `run(client, config, prompt, ...)` function, wire it into `cli.py` as a new subparser + `elif` branch.
- **Ruff** is the sole linter/formatter (line length 88, Python 3.11 target). No Black, no Flake8.
- **No mocking of the Anthropic SDK** in tests — the test suite avoids live API calls entirely by testing config validation and CLI argument parsing only.
