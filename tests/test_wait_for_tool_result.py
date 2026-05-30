from __future__ import annotations

import threading

from src.layers.eventbus_09 import EventBusLayerApi, event_types


def test_wait_for_tool_result_already_published() -> None:
    bus = EventBusLayerApi()
    bus.publish(event_types.TOOL_CALL_RESULT, {
        "tool_call_id": "tc1",
        "output": "done",
    })
    result = bus.wait_for_tool_result("tc1", timeout=5.0)
    assert result is not None
    assert result["output"] == "done"


def test_wait_for_tool_result_timeout() -> None:
    bus = EventBusLayerApi()
    result = bus.wait_for_tool_result("no_such_id", timeout=0.1)
    assert result is None


def test_wait_for_tool_result_concurrent() -> None:
    bus = EventBusLayerApi()

    def publish_later() -> None:
        import time
        time.sleep(0.05)
        bus.publish(event_types.TOOL_CALL_RESULT, {
            "tool_call_id": "tc_concurrent",
            "output": "concurrent_result",
        })

    t = threading.Thread(target=publish_later, daemon=True)
    t.start()

    result = bus.wait_for_tool_result("tc_concurrent", timeout=5.0)
    assert result is not None
    assert result["output"] == "concurrent_result"
