from __future__ import annotations

from pathlib import Path


class PathForbidden(Exception):
    """Raised when a file operation targets a path outside the workspace."""


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent  # catnipthon/


def check_path(target_path: str) -> str:
    """Resolve and validate that a path is within workspace boundaries."""
    resolved = (WORKSPACE_ROOT / target_path).resolve()

    try:
        resolved.relative_to(WORKSPACE_ROOT.resolve())
    except ValueError:
        raise PathForbidden(
            f"Path '{target_path}' resolves outside workspace "
            f"({WORKSPACE_ROOT.resolve()})"
        )

    return str(resolved)
