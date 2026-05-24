from __future__ import annotations

from src.layers.tool_registry_10.types import ToolDef


WRITE_FILE: ToolDef = ToolDef(
    name="write_file",
    description="Write content to a file. Creates parent directories if needed. Overwrites existing content.",
    category="fs",
    permission="medium",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file relative to workspace root",
            },
            "content": {
                "type": "string",
                "description": "Content to write to the file",
            },
        },
        "required": ["file_path", "content"],
    },
)
