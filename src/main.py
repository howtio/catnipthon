"""catnip-agent — CLI 2.0: batch mode + interactive REPL."""

from __future__ import annotations

import sys

from src.shared.cli import print_header
from src.bootstrap import bootstrap
from src.shared.interactive import run_interactive


def main() -> None:
    app = bootstrap()
    print_header()

    if len(sys.argv) > 1:
        # Batch mode: run a single task
        print()
        print("=" * 46)
        try:
            result = app.gateway.run_cli(sys.argv[1:])
        except Exception as e:
            print(f"  [!] Error: {e}")
            sys.exit(1)
        try:
            print(result)
        except UnicodeEncodeError:
            safe = result.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(
                sys.stdout.encoding or "utf-8", errors="replace"
            )
            print(safe)
        print("=" * 46)
    else:
        # Interactive mode
        run_interactive(app)


if __name__ == "__main__":
    main()
