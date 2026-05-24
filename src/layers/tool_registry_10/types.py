from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


PermissionLevel = Literal["low", "medium", "high"]
ToolCategory = Literal["fs", "shell", "vcs"]


@dataclass
class ToolDef:
    """Definition of a registered tool."""

    name: str
    description: str
    category: ToolCategory
    parameters: dict[str, Any]
    permission: PermissionLevel = "medium"
    requires: list[str] = field(default_factory=list)
