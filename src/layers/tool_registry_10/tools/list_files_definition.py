from __future__ import annotations

from src.layers.tool_registry_10.types import ToolDef


LIST_FILES: ToolDef = ToolDef(
    name="list_files",
    description="List files/dirs in a path. Tree view.",
    category="fs",
    permission="low",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path relative to workspace root (default: '.')",
                "default": ".",
            },
        },
    },
)
