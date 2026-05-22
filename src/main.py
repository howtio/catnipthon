"""catnip-agent — 11-Layer Coding Agent Runtime.

Scaffold entry point. Shows the banner and exits.
Start implementing layers, then wire them in bootstrap.py.
"""

from __future__ import annotations

from src.shared.cli import print_header


def main() -> None:
    print_header()
    print()
    print("  Scaffold ready. Next steps:")
    print("    1. Read docs/CONSTRUCTION_PLAN.md")
    print("    2. Start Phase 1: Gateway + Queue + Worker")
    print("    3. Wire your layers in src/bootstrap.py")
    print("    4. Come back to src/main.py to run the pipeline")
    print()


if __name__ == "__main__":
    main()
