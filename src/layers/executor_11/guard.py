from __future__ import annotations

from typing import Any

from src.layers.tool_registry_10 import ToolRegistryLayerApi
from src.layers.executor_11.policy.permission_guard import check_permission
from src.layers.executor_11.policy.path_guard import check_path
from src.layers.executor_11.policy.command_guard import check_command


class GuardError(Exception):
    """Base error for guard failures."""


def run_guards(
    tool_name: str,
    arguments: dict[str, Any],
    registry: ToolRegistryLayerApi,
) -> dict[str, Any]:
    """Run all relevant guards for a tool call. Returns validated/resolved arguments."""
    tool_def = registry.get_tool(tool_name)
    if tool_def is None:
        raise GuardError(f"Unknown tool: {tool_name}")

    # Permission guard
    check_permission(tool_name, tool_def.permission)

    # Path guard (for fs tools with file_path or path arguments)
    if tool_def.category == "fs":
        for arg_key in ("file_path", "path"):
            if arg_key in arguments and arguments[arg_key]:
                resolved = check_path(str(arguments[arg_key]))
                arguments = {**arguments, arg_key: resolved}

    # Command guard (for shell tools)
    if tool_def.category == "shell" and "command" in arguments:
        check_command(str(arguments["command"]))

    return arguments
