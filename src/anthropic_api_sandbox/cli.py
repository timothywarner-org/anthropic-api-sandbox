"""Command-line interface for Anthropic API examples.

Provides subcommands for each API pattern: basic, stream, and system.
"""

import argparse
import sys

from .client import create_client
from .config import ConfigError, load_config
from .examples import basic, stream, system_prompt


def main() -> int:
    """Entry point for the sandbox CLI.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        prog="sandbox",
        description="Anthropic Messages API teaching examples",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Basic command: simple request/response
    basic_parser = subparsers.add_parser(
        "basic",
        help="Send a basic request and print the response",
    )
    basic_parser.add_argument("prompt", help="The prompt to send")

    # Stream command: streaming response
    stream_parser = subparsers.add_parser(
        "stream",
        help="Send a request and stream the response",
    )
    stream_parser.add_argument("prompt", help="The prompt to send")

    # System command: system prompt pattern
    system_parser = subparsers.add_parser(
        "system",
        help="Send a request with a system prompt persona",
    )
    system_parser.add_argument(
        "--persona",
        required=True,
        help="Role or persona for the assistant (e.g., pirate, teacher)",
    )
    system_parser.add_argument("prompt", help="The prompt to send")

    args = parser.parse_args()

    try:
        config = load_config()
        client = create_client(config)
    except ConfigError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1

    try:
        if args.command == "basic":
            response = basic.run(client, config, args.prompt)
            print(response)

        elif args.command == "stream":
            for chunk in stream.run(client, config, args.prompt):
                print(chunk, end="", flush=True)
            print()  # Final newline

        elif args.command == "system":
            response = system_prompt.run(client, config, args.prompt, args.persona)
            print(response)

    except Exception as e:
        print(f"API error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
