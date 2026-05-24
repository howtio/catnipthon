from __future__ import annotations

import argparse
import sys


def parse_cli_args(args: list[str] | None = None) -> str:
    """Parse CLI arguments and return the user message string.

    Usage: python -m src.main "your message here"
    """
    parser = argparse.ArgumentParser(
        description="catnip-agent — 11-layer Coding Agent Runtime",
        usage="%(prog)s <message>",
    )
    parser.add_argument(
        "message",
        nargs="?",
        default="",
        help="The user message/question for the agent",
    )

    parsed = parser.parse_args(args)
    msg: str = parsed.message or ""

    if not msg:
        parser.print_help()
        sys.exit(0)

    return msg
