from __future__ import annotations

from typing import Any

from src.layers.tool_registry_10.types import ToolDef, ToolCategory
from src.layers.tool_registry_10.tool_registry import ToolRegistry


class ToolRegistryLayerApi:
    """10-tool-registry public API: manage tool definitions."""

    def __init__(self) -> None:
        self._registry = ToolRegistry()

    def get_tool(self, name: str) -> ToolDef | None:
        return self._registry.get_tool(name)

    def list_tools(self, category: ToolCategory | None = None) -> list[ToolDef]:
        return self._registry.list_tools(category)

    def has_tool(self, name: str) -> bool:
        return self._registry.has_tool(name)

    def to_openai_schemas(self) -> list[dict[str, Any]]:
        return self._registry.to_openai_schemas()
