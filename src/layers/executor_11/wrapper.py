from __future__ import annotations

import uuid
from typing import Any

from src.layers.eventbus_09 import EventBusLayerApi, event_types
from src.layers.eventbus_09.types import Event
from src.layers.tool_registry_10 import ToolRegistryLayerApi
from src.layers.executor_11.types import ToolCallRequest, ToolResult
from src.layers.executor_11.execute_tool import execute_tool


class ExecutorLayerApi:
    """11-executor public API: listen for tool calls, execute, publish results.

    In Phase 3 this is a skeleton that subscribes to tool.call.requested
    and publishes tool.call.result / tool.call.failed.
    """

    def __init__(
        self, eventbus: EventBusLayerApi, registry: ToolRegistryLayerApi
    ) -> None:
        self._eventbus = eventbus
        self._registry = registry
        self._unsub = self._eventbus.subscribe(
            event_types.TOOL_CALL_REQUESTED, self._on_tool_call
        )

    def _on_tool_call(self, event: Event) -> None:
        """Handle an incoming tool call request."""
        payload = event.payload
        request = ToolCallRequest(
            tool_call_id=payload.get("tool_call_id", uuid.uuid4().hex[:12]),
            tool_name=payload.get("tool_name", ""),
            arguments=payload.get("arguments", {}),
        )

        result = execute_tool(request, self._registry)

        if result.success:
            self._eventbus.publish(event_types.TOOL_CALL_RESULT, {
                "tool_call_id": result.tool_call_id,
                "tool_name": request.tool_name,
                "output": result.output,
            })
        else:
            self._eventbus.publish(event_types.TOOL_CALL_FAILED, {
                "tool_call_id": result.tool_call_id,
                "tool_name": request.tool_name,
                "error": result.error,
            })

    def execute_sync(self, tool_name: str, arguments: dict[str, Any]) -> ToolResult:
        """Synchronous tool execution for testing."""
        request = ToolCallRequest(
            tool_call_id=uuid.uuid4().hex[:12],
            tool_name=tool_name,
            arguments=arguments,
        )
        return execute_tool(request, self._registry)
