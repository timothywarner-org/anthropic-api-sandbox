"""Configuration management for Anthropic API access.

Loads API key and model settings from environment variables with validation.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Config:
    """Immutable configuration for Anthropic API access.

    Attributes:
        api_key: Anthropic API key (required)
        model: Model identifier to use for requests
        max_tokens: Default maximum tokens for responses
    """

    api_key: str
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 1024


def load_config() -> Config:
    """Load configuration from environment variables.

    Reads from .env file if present, then validates required settings.

    Returns:
        Config object with validated settings

    Raises:
        ConfigError: If ANTHROPIC_API_KEY is not set
    """
    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        raise ConfigError(
            "ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key."
        )

    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    return Config(api_key=api_key, model=model)
