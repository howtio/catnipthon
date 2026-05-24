from __future__ import annotations

from src.layers.tool_registry_10.types import ToolDef


SHELL_EXEC: ToolDef = ToolDef(
    name="shell_exec",
    description="Execute a shell command and return its stdout and stderr. Blocking, with a configurable timeout.",
    category="shell",
    permission="high",
    requires=["command_guard"],
    parameters={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Shell command to execute",
            },
            "timeout_ms": {
                "type": "integer",
                "description": "Timeout in milliseconds (default: 30000)",
                "default": 30000,
            },
        },
        "required": ["command"],
    },
)
