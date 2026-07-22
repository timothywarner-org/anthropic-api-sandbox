"""Basic Messages API request/response pattern.

Demonstrates the simplest possible API call: send a prompt, receive a response.
"""

import anthropic

from ..config import Config


def run(client: anthropic.Anthropic, config: Config, prompt: str) -> str:
    """Execute a basic Messages API request.

    This is the foundational pattern for all Anthropic API interactions.
    One message in, one response out, no streaming.

    Args:
        client: Configured Anthropic client
        config: Configuration with model and token settings
        prompt: User prompt to send

    Returns:
        The assistant's response text
    """
    message = client.messages.create(
        model=config.model,
        max_tokens=config.max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )

    # Response content is a list of content blocks; extract the text
    return message.content[0].text
