# Usage Guide

Detailed command examples for the Anthropic API Sandbox.

## Prerequisites

1. Install [uv](https://docs.astral.sh/uv/)
2. Clone this repository
3. Copy `.env.example` to `.env` and add your Anthropic API key

## Commands

### Basic Request/Response

The simplest pattern: send a prompt, receive a complete response.

```bash
uv run sandbox basic "What is the capital of France?"
```

**What it demonstrates:**

- Creating a Messages API request
- Extracting text from the response content blocks
- Single-turn conversation pattern

### Streaming Response

Real-time token streaming for responsive UX.

```bash
uv run sandbox stream "Explain TCP/IP in three sentences."
```

**What it demonstrates:**

- Using `client.messages.stream()` context manager
- Iterating over `stream.text_stream` for real-time output
- Flushing output for immediate display

### System Prompt Pattern

Set assistant behavior and persona before the conversation.

```bash
uv run sandbox system --persona "pirate" "Tell me about cloud computing."
uv run sandbox system --persona "Socratic teacher" "What is recursion?"
uv run sandbox system --persona "1950s radio announcer" "Describe Python programming."
```

**What it demonstrates:**

- Adding a `system` parameter to shape responses
- Role-playing and persona patterns
- Establishing constraints and tone

## Model Override

To use a different model, set `ANTHROPIC_MODEL` in your `.env`:

```bash
ANTHROPIC_MODEL=claude-3-haiku-20240307
```

## Troubleshooting

**"Configuration error: ANTHROPIC_API_KEY not set"**

- Ensure `.env` exists and contains a valid key
- Check that the key is not the placeholder value

**"API error: ..."**

- Verify your API key is valid at https://console.anthropic.com/
- Check your account has sufficient credits
- Ensure you're not rate-limited

## Development

Run tests:

```bash
uv run pytest -v
```

Run linter:

```bash
uv run ruff check src tests
```

Format code:

```bash
uv run ruff format src tests
```
