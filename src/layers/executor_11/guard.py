from __future__ import annotations

from typing import Any

from src.layers.tool_registry_10 import ToolRegistryLayerApi
from src.layers.executor_11.policy.permission_guard import check_permission
from src.layers.executor_11.policy.path_guard import check_path
from src.layers.executor_11.policy.command_guard import check_command


class GuardError(Exception):
    """Base error for guard failures."""


def _check_url(url: str) -> None:
    """Validate URL for web tools."""
    if not isinstance(url, str) or not url.strip():
        raise GuardError("URL must be a non-empty string")
    if not url.startswith(("http://", "https://")):
        raise GuardError("Only http/https URLs are allowed")
    # Block common SSRF targets
    blocked = ("localhost", "127.0.0.1", "0.0.0.0", "[::1]", "169.254.", "10.", "172.16.", "192.168.")
    import urllib.parse
    host = urllib.parse.urlparse(url).hostname or ""
    if any(host.startswith(b) for b in blocked):
        raise GuardError(f"URL blocked (internal address): {host}")


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

    # URL guard (for web tools)
    if tool_def.category == "web":
        for arg_key in ("url",):
            if arg_key in arguments and arguments[arg_key]:
                _check_url(str(arguments[arg_key]))

    return arguments
