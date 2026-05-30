from __future__ import annotations

from src.layers.tool_registry_10.types import ToolDef


READ_FILE: ToolDef = ToolDef(
    name="read_file",
    description="Read a file within the workspace.",
    category="fs",
    permission="low",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path relative to workspace root",
            },
        },
        "required": ["file_path"],
    },
)
