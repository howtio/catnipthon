from __future__ import annotations

from typing import Any

from src.layers.executor_11.types import ToolCallRequest, ToolResult
from src.layers.tool_registry_10 import ToolRegistryLayerApi
from src.layers.executor_11.guard import run_guards, GuardError
from src.layers.executor_11.tools import (
    list_files,
    read_file,
    write_file,
    patch_file,
    shell_exec,
    git_diff,
    web_fetch,
    web_search,
    open_browser,
    file_search,
)


_TOOL_IMPLS: dict[str, Any] = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "patch_file": patch_file,
    "shell_exec": shell_exec,
    "git_diff": git_diff,
    "web_fetch": web_fetch,
    "web_search": web_search,
    "open_browser": open_browser,
    "file_search": file_search,
}


def execute_tool(
    request: ToolCallRequest,
    registry: ToolRegistryLayerApi,
) -> ToolResult:
    """Execute a tool with real implementation. Runs guards before execution."""
    tool_def = registry.get_tool(request.tool_name)

    if tool_def is None:
        return ToolResult(
            tool_call_id=request.tool_call_id,
            success=False,
            error=f"Unknown tool: {request.tool_name}",
        )

    # Run guards
    try:
        validated_args = run_guards(request.tool_name, request.arguments, registry)
    except (GuardError, PermissionError, Exception) as e:
        return ToolResult(
            tool_call_id=request.tool_call_id,
            success=False,
            error=f"Guard blocked: {e}",
        )

    # Execute
    impl = _TOOL_IMPLS.get(request.tool_name)
    if impl is None:
        return ToolResult(
            tool_call_id=request.tool_call_id,
            success=False,
            error=f"No implementation for tool: {request.tool_name}",
        )

    try:
        output = impl(**validated_args)
        if isinstance(output, str) and output.startswith("Error:"):
            return ToolResult(
                tool_call_id=request.tool_call_id,
                success=False,
                error=output,
            )
        return ToolResult(
            tool_call_id=request.tool_call_id,
            success=True,
            output=str(output),
        )
    except Exception as e:
        return ToolResult(
            tool_call_id=request.tool_call_id,
            success=False,
            error=f"{type(e).__name__}: {e}",
        )
