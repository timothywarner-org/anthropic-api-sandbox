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

## PowerShell Utilities

For no-brainer demo runs and restarts, use the scripts in `utilities/`:

```powershell
# Run any mode
.\utilities\Start-Sandbox.ps1 -Command basic -Prompt "What is zero trust?"

# Mode-specific wrappers
.\utilities\Start-Basic.ps1 -Prompt "Explain CIDR in one paragraph."
.\utilities\Start-Stream.ps1 -Prompt "Give me 5 Kubernetes troubleshooting tips."
.\utilities\Start-System.ps1 -Persona "teacher" -Prompt "Explain tokenization simply."

# Replay last run (idempotent restart)
.\utilities\Restart-Sandbox.ps1
```

See [docs/usage.md](docs/usage.md) for detailed examples.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Anthropic API key

## License

MIT
