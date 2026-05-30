from __future__ import annotations

from src.layers.tool_registry_10.types import ToolDef


PATCH_FILE: ToolDef = ToolDef(
    name="patch_file",
    description="Find & replace string in a file. Surgical edit.",
    category="fs",
    permission="medium",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path relative to workspace root",
            },
            "old_string": {
                "type": "string",
                "description": "Text to search for (must be unique)",
            },
            "new_string": {
                "type": "string",
                "description": "Replacement text",
            },
        },
        "required": ["file_path", "old_string", "new_string"],
    },
)
