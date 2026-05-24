from __future__ import annotations

from typing import Any

from src.layers.tool_registry_10.types import PermissionLevel


class PermissionDenied(Exception):
    """Raised when a tool call exceeds the allowed permission level."""


def check_permission(
    tool_name: str,
    required_level: PermissionLevel,
    granted_level: PermissionLevel = "medium",
) -> None:
    """Check if the granted level meets the required level.

    Levels: low < medium < high
    - low: any operation
    - medium: most operations (default)
    - high: restricted operations (shell exec etc.)
    """
    levels = {"low": 0, "medium": 1, "high": 2}
    if levels.get(required_level, 0) > levels.get(granted_level, 1):
        raise PermissionDenied(
            f"Permission denied for '{tool_name}': "
            f"requires '{required_level}', granted '{granted_level}'"
        )
