"""Streaming response pattern for the Messages API.

Demonstrates real-time token streaming for responsive UX.
"""

from collections.abc import Generator

import anthropic

from ..config import Config


def run(
    client: anthropic.Anthropic, config: Config, prompt: str
) -> Generator[str, None, None]:
    """Execute a streaming Messages API request.

    Yields tokens as they arrive from the API, enabling real-time display.
    Use this pattern when response latency matters more than simplicity.

    Args:
        client: Configured Anthropic client
        config: Configuration with model and token settings
        prompt: User prompt to send

    Yields:
        Individual text chunks as they stream from the API
    """
    with client.messages.stream(
        model=config.model,
        max_tokens=config.max_tokens,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        yield from stream.text_stream
