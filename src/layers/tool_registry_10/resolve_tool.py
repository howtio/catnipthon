from __future__ import annotations

from src.layers.tool_registry_10.tool_registry import ToolRegistry
from src.layers.tool_registry_10.types import ToolDef


def resolve_tool(registry: ToolRegistry, name: str) -> ToolDef | None:
    """Look up a tool by name. Returns None if not found."""
    return registry.get_tool(name)
