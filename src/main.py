"""catnip-agent — Phase 1: Gateway + Queue + Worker."""

from __future__ import annotations

import sys

from src.shared.cli import print_header, print_result_ok
from src.bootstrap import bootstrap


def main() -> None:
    app = bootstrap()
    print_header()

    if len(sys.argv) > 1:
        result = app.gateway.run_cli(sys.argv[1:])
        print()
        print("=" * 46)
        print(result)
        print("=" * 46)
    else:
        print()
        print("  Usage: python -m src.main \"your message\"")
        print()


if __name__ == "__main__":
    main()
