"""Tests for configuration loading and validation."""

from dataclasses import FrozenInstanceError

import pytest

from anthropic_api_sandbox.config import Config, ConfigError, load_config


def test_config_dataclass_is_immutable():
    """Config should be a frozen dataclass."""
    config = Config(api_key="test-key")
    with pytest.raises(FrozenInstanceError):
        config.api_key = "new-key"


def test_config_has_sensible_defaults():
    """Config should have default model and max_tokens."""
    config = Config(api_key="test-key")
    assert config.model == "claude-sonnet-4-20250514"
    assert config.max_tokens == 1024


def test_load_config_raises_on_missing_key(monkeypatch):
    """load_config should raise ConfigError if API key is not set."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ConfigError) as exc_info:
        load_config()
    assert "ANTHROPIC_API_KEY" in str(exc_info.value)


def test_load_config_raises_on_placeholder_key(monkeypatch):
    """load_config should reject the placeholder value from .env.example."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "your-api-key-here")
    with pytest.raises(ConfigError):
        load_config()


def test_load_config_raises_on_whitespace_only_key(monkeypatch):
    """load_config should reject whitespace-only API key values."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "   ")
    with pytest.raises(ConfigError):
        load_config()


def test_load_config_accepts_valid_key(monkeypatch):
    """load_config should succeed with a valid API key."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
    config = load_config()
    assert config.api_key == "sk-ant-test-key"


def test_load_config_respects_model_override(monkeypatch):
    """load_config should use ANTHROPIC_MODEL if set."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
    config = load_config()
    assert config.model == "claude-3-haiku-20240307"
