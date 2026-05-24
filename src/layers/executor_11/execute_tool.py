from __future__ import annotations

import json
import time

from src.layers.executor_11.types import ToolCallRequest, ToolResult
from src.layers.tool_registry_10 import ToolRegistryLayerApi


def execute_tool(request: ToolCallRequest, registry: ToolRegistryLayerApi) -> ToolResult:
    """Execute a tool. Phase 3: mock execution only."""
    tool_def = registry.get_tool(request.tool_name)

    if tool_def is None:
        return ToolResult(
            tool_call_id=request.tool_call_id,
            success=False,
            error=f"Unknown tool: {request.tool_name}",
        )

    # Phase 3: mock result
    return ToolResult(
        tool_call_id=request.tool_call_id,
        success=True,
        output=json.dumps({
            "tool": request.tool_name,
            "status": "mock_result",
            "message": f"[Phase 3 mock] {request.tool_name} executed with args: {request.arguments}",
        }, ensure_ascii=False),
    )
