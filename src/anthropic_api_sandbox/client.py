"""Anthropic client factory.

Creates configured Anthropic client instances for API access.
"""

import anthropic

from .config import Config


def create_client(config: Config) -> anthropic.Anthropic:
    """Create an Anthropic client with the given configuration.

    Args:
        config: Validated configuration with API key

    Returns:
        Configured Anthropic client ready for API calls
    """
    return anthropic.Anthropic(api_key=config.api_key)
