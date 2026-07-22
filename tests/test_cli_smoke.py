"""Smoke tests for CLI argument parsing and module wiring.

These tests verify the CLI structure works without making API calls.
"""

import os
import subprocess
import sys
from pathlib import Path


def _subprocess_env() -> dict[str, str]:
    """Ensure src-layout package is importable in spawned Python subprocesses."""
    env = os.environ.copy()
    src_path = str(Path(__file__).resolve().parents[1] / "src")
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        src_path if not existing else os.pathsep.join([src_path, existing])
    )
    return env


def test_cli_help_exits_zero():
    """CLI --help should exit successfully."""
    result = subprocess.run(
        [sys.executable, "-m", "anthropic_api_sandbox.cli", "--help"],
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    assert result.returncode == 0
    assert "Anthropic Messages API" in result.stdout


def test_cli_basic_subcommand_help():
    """Basic subcommand help should describe the prompt argument."""
    result = subprocess.run(
        [sys.executable, "-m", "anthropic_api_sandbox.cli", "basic", "--help"],
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    assert result.returncode == 0
    assert "prompt" in result.stdout.lower()


def test_cli_stream_subcommand_help():
    """Stream subcommand help should describe the prompt argument."""
    result = subprocess.run(
        [sys.executable, "-m", "anthropic_api_sandbox.cli", "stream", "--help"],
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    assert result.returncode == 0
    assert "prompt" in result.stdout.lower()


def test_cli_system_subcommand_help():
    """System subcommand help should describe persona and prompt arguments."""
    result = subprocess.run(
        [sys.executable, "-m", "anthropic_api_sandbox.cli", "system", "--help"],
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    assert result.returncode == 0
    assert "persona" in result.stdout.lower()
    assert "prompt" in result.stdout.lower()


def test_cli_missing_command_fails():
    """CLI should fail if no subcommand is provided."""
    result = subprocess.run(
        [sys.executable, "-m", "anthropic_api_sandbox.cli"],
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    assert result.returncode != 0
