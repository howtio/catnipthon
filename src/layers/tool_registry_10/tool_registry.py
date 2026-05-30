from __future__ import annotations

from typing import Any

from src.layers.tool_registry_10.types import ToolDef, ToolCategory
from src.layers.tool_registry_10.tools.list_files_definition import LIST_FILES
from src.layers.tool_registry_10.tools.read_file_definition import READ_FILE
from src.layers.tool_registry_10.tools.write_file_definition import WRITE_FILE
from src.layers.tool_registry_10.tools.patch_file_definition import PATCH_FILE
from src.layers.tool_registry_10.tools.shell_exec_definition import SHELL_EXEC
from src.layers.tool_registry_10.tools.git_diff_definition import GIT_DIFF
from src.layers.tool_registry_10.tools.web_fetch_definition import WEB_FETCH
from src.layers.tool_registry_10.tools.web_search_definition import WEB_SEARCH
from src.layers.tool_registry_10.tools.open_browser_definition import OPEN_BROWSER
from src.layers.tool_registry_10.tools.file_search_definition import FILE_SEARCH


_ALL_TOOLS: dict[str, ToolDef] = {
    tool.name: tool
    for tool in [
        LIST_FILES,
        READ_FILE,
        WRITE_FILE,
        PATCH_FILE,
        SHELL_EXEC,
        GIT_DIFF,
        WEB_FETCH,
        WEB_SEARCH,
        OPEN_BROWSER,
        FILE_SEARCH,
    ]
}


class ToolRegistry:
    """Registry for tool definitions. Read-only after initialization."""

    def get_tool(self, name: str) -> ToolDef | None:
        return _ALL_TOOLS.get(name)

    def list_tools(self, category: ToolCategory | None = None) -> list[ToolDef]:
        if category is None:
            return list(_ALL_TOOLS.values())
        return [t for t in _ALL_TOOLS.values() if t.category == category]

    def has_tool(self, name: str) -> bool:
        return name in _ALL_TOOLS

    def to_openai_schemas(self) -> list[dict[str, Any]]:
        """Convert all tools to OpenAI-compatible function calling schemas."""
        schemas: list[dict[str, Any]] = []
        for tool in _ALL_TOOLS.values():
            schemas.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            })
        return schemas
