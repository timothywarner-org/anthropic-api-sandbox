"""System prompt pattern for the Messages API.

Demonstrates how to set assistant behavior and persona using system prompts.
"""

import anthropic

from ..config import Config


def run(client: anthropic.Anthropic, config: Config, prompt: str, persona: str) -> str:
    """Execute a Messages API request with a system prompt.

    System prompts establish the assistant's role, personality, and constraints.
    They're processed before user messages and shape all subsequent responses.

    Args:
        client: Configured Anthropic client
        config: Configuration with model and token settings
        prompt: User prompt to send
        persona: Role or persona for the assistant (e.g., "pirate", "teacher")

    Returns:
        The assistant's response text, shaped by the system prompt
    """
    system_prompt = (
        f"You are a helpful assistant who responds as a {persona}. Stay in character."
    )

    message = client.messages.create(
        model=config.model,
        max_tokens=config.max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text
