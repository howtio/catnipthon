from __future__ import annotations

from src.layers.tool_registry_10.types import ToolDef


LIST_FILES: ToolDef = ToolDef(
    name="list_files",
    description="List files and directories in a given path. Returns a tree-like view. Path can be relative to workspace root.",
    category="fs",
    permission="low",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Directory path relative to workspace root (default: '.')",
                "default": ".",
            },
        },
    },
)
