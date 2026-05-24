from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any

from src.layers.eventbus_09.event_bus import EventBus
from src.layers.eventbus_09.types import Event
from src.layers.eventbus_09.event_types import TOOL_CALL_RESULT, TOOL_CALL_FAILED


class EventBusLayerApi:
    """09-eventbus public API: publish/subscribe event system with tool result waiting."""

    def __init__(self) -> None:
        self._bus = EventBus()
        self._waiters: dict[str, threading.Event] = {}

    def publish(self, event_type: str, payload: dict[str, Any] | None = None) -> Event:
        event = self._bus.publish(event_type, payload)
        # Notify waiters for tool results
        if event_type in (TOOL_CALL_RESULT, TOOL_CALL_FAILED):
            tool_call_id = (payload or {}).get("tool_call_id", "")
            if tool_call_id in self._waiters:
                self._waiters[tool_call_id].set()
        return event

    def subscribe(
        self, event_type: str, callback: Callable[[Event], None]
    ) -> Callable[[], None]:
        return self._bus.subscribe(event_type, callback)

    def get_history(self, event_type: str | None = None) -> list[Event]:
        return self._bus.get_history(event_type)

    def wait_for_tool_result(
        self, tool_call_id: str, timeout: float | None = None
    ) -> dict[str, Any] | None:
        """Wait for a tool.call.result or tool.call.failed event by tool_call_id."""
        event = threading.Event()
        self._waiters[tool_call_id] = event

        try:
            # Also check if result already arrived
            for e in self._bus.get_history(TOOL_CALL_RESULT):
                if e.payload.get("tool_call_id") == tool_call_id:
                    return e.payload
            for e in self._bus.get_history(TOOL_CALL_FAILED):
                if e.payload.get("tool_call_id") == tool_call_id:
                    return e.payload

            if not event.wait(timeout=timeout):
                return None  # timeout

            # Fetch the result from history
            for e in self._bus.get_history(TOOL_CALL_RESULT):
                if e.payload.get("tool_call_id") == tool_call_id:
                    return e.payload
            for e in self._bus.get_history(TOOL_CALL_FAILED):
                if e.payload.get("tool_call_id") == tool_call_id:
                    return e.payload
            return None
        finally:
            self._waiters.pop(tool_call_id, None)

    def get_events(self, event_type: str | None = None) -> list[Event]:
        """Alias for get_history."""
        return self.get_history(event_type)
