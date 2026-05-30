from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any

from src.layers.eventbus_09.event_bus import EventBus
from src.layers.eventbus_09.types import Event
from src.layers.eventbus_09.event_types import TOOL_CALL_RESULT, TOOL_CALL_FAILED


class EventBusLayerApi:
    """09-eventbus public API: publish/subscribe event system with tool result waiting.

    Thread-safe: publishes and subscriptions are protected by locks.
    """

    def __init__(self) -> None:
        self._bus = EventBus()
        self._waiters: dict[str, threading.Event] = {}
        self._waiters_lock = threading.Lock()

    def publish(self, event_type: str, payload: dict[str, Any] | None = None) -> Event:
        event = self._bus.publish(event_type, payload)
        if event_type in (TOOL_CALL_RESULT, TOOL_CALL_FAILED):
            tool_call_id = (payload or {}).get("tool_call_id", "")
            if tool_call_id:
                with self._waiters_lock:
                    ev = self._waiters.get(tool_call_id)
                    if ev:
                        ev.set()
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
        with self._waiters_lock:
            # Check if result already arrived (race-free: lock covers both check and insert)
            for e in self._bus.get_history(TOOL_CALL_RESULT):
                if e.payload.get("tool_call_id") == tool_call_id:
                    return e.payload
            for e in self._bus.get_history(TOOL_CALL_FAILED):
                if e.payload.get("tool_call_id") == tool_call_id:
                    return e.payload
            self._waiters[tool_call_id] = event

        try:
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
            with self._waiters_lock:
                self._waiters.pop(tool_call_id, None)

    def get_events(self, event_type: str | None = None) -> list[Event]:
        """Alias for get_history."""
        return self.get_history(event_type)
