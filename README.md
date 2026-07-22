# Anthropic API Sandbox

A minimal Python sandbox for learning the **Anthropic Messages API**. Designed for O'Reilly live training demos.

## Quick Start

```bash
# Clone and enter
git clone https://github.com/timothywarner-org/anthropic-api-sandbox.git
cd anthropic-api-sandbox

# Install dependencies (requires uv)
uv sync

# Set your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run examples
uv run sandbox basic "What is the capital of France?"
uv run sandbox stream "Explain TCP/IP in three sentences."
uv run sandbox system --persona "pirate" "Tell me about cloud computing."
```

## Commands

| Command                                    | Description             |
| ------------------------------------------ | ----------------------- |
| `sandbox basic <prompt>`                   | Single request/response |
| `sandbox stream <prompt>`                  | Streaming response      |
| `sandbox system --persona <role> <prompt>` | System prompt pattern   |

See [docs/usage.md](docs/usage.md) for detailed examples.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Anthropic API key

## License

MIT
