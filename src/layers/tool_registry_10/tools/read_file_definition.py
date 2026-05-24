from __future__ import annotations

from src.layers.tool_registry_10.types import ToolDef


READ_FILE: ToolDef = ToolDef(
    name="read_file",
    description="Read the contents of a file. Path must be within the workspace.",
    category="fs",
    permission="low",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file relative to workspace root",
            },
        },
        "required": ["file_path"],
    },
)
