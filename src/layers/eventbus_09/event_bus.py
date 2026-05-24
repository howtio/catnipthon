from __future__ import annotations

import threading
import time
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from src.layers.eventbus_09.types import Event


class EventBus:
    """Simple in-process pub/sub event bus. Thread-safe."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._subscribers: dict[str, list[Callable[[Event], None]]] = defaultdict(list)
        self._history: list[Event] = []

    def publish(self, event_type: str, payload: dict[str, Any] | None = None) -> Event:
        """Publish an event and notify subscribers."""
        event = Event(type=event_type, payload=payload or {})
        with self._lock:
            self._history.append(event)
            cbs = list(self._subscribers.get(event_type, []))
        for cb in cbs:
            cb(event)
        return event

    def subscribe(self, event_type: str, callback: Callable[[Event], None]) -> Callable[[], None]:
        """Subscribe to an event type. Returns an unsubscribe callable."""
        with self._lock:
            self._subscribers[event_type].append(callback)

        def unsubscribe() -> None:
            with self._lock:
                lst = self._subscribers.get(event_type)
                if lst and callback in lst:
                    lst.remove(callback)

        return unsubscribe

    def get_history(self, event_type: str | None = None) -> list[Event]:
        """Get published events, optionally filtered by type."""
        with self._lock:
            if event_type is None:
                return list(self._history)
            return [e for e in self._history if e.type == event_type]

    def clear(self) -> None:
        """Clear all subscribers and history."""
        with self._lock:
            self._subscribers.clear()
            self._history.clear()
