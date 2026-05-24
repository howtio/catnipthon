from __future__ import annotations

from src.layers.tool_registry_10.types import ToolDef


FILE_SEARCH: ToolDef = ToolDef(
    name="file_search",
    description="Search files by name glob or text content in workspace.",
    category="fs",
    permission="low",
    parameters={
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Glob pattern (e.g. '*.py') or text to search",
            },
            "content": {
                "type": "string",
                "description": "If set, search file contents for this text instead of name",
                "default": "",
            },
            "max_results": {
                "type": "integer",
                "description": "Max results (default: 20)",
                "default": 20,
            },
        },
        "required": ["pattern"],
    },
)
