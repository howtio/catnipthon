from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ToolCallRequest:
    """A tool call request from the Runner."""

    tool_call_id: str
    tool_name: str
    arguments: dict[str, Any]


@dataclass
class ToolResult:
    """Result of a tool execution."""

    tool_call_id: str
    success: bool
    output: str = ""
    error: str = ""
