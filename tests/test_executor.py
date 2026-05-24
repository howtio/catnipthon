from __future__ import annotations

from src.layers.executor_11 import ExecutorLayerApi
from src.layers.eventbus_09 import EventBusLayerApi
from src.layers.tool_registry_10 import ToolRegistryLayerApi


def test_executor_subscribes_and_mocks() -> None:
    eventbus = EventBusLayerApi()
    registry = ToolRegistryLayerApi()
    executor = ExecutorLayerApi(eventbus, registry)  # noqa: F841

    eventbus.publish("tool.call.requested", {
        "tool_call_id": "tc1",
        "tool_name": "list_files",
        "arguments": {"path": "."},
    })

    result = eventbus.wait_for_tool_result("tc1", timeout=5.0)
    assert result is not None
    assert "tool_call_id" in result
    assert result["tool_call_id"] == "tc1"


def test_executor_sync_call() -> None:
    eventbus = EventBusLayerApi()
    registry = ToolRegistryLayerApi()
    executor = ExecutorLayerApi(eventbus, registry)

    result = executor.execute_sync("list_files", {"path": "."})
    assert result.success is True
    assert "src" in result.output


def test_executor_unknown_tool() -> None:
    eventbus = EventBusLayerApi()
    registry = ToolRegistryLayerApi()
    executor = ExecutorLayerApi(eventbus, registry)

    result = executor.execute_sync("nonexistent_tool", {})
    assert result.success is False
