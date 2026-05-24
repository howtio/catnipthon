from __future__ import annotations

from src.layers.tool_registry_10.types import ToolDef


PATCH_FILE: ToolDef = ToolDef(
    name="patch_file",
    description="Apply a string replacement patch to a file (find and replace). Use for surgical edits.",
    category="fs",
    permission="medium",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file relative to workspace root",
            },
            "old_string": {
                "type": "string",
                "description": "Text to search for (must be unique in the file)",
            },
            "new_string": {
                "type": "string",
                "description": "Replacement text",
            },
        },
        "required": ["file_path", "old_string", "new_string"],
    },
)
