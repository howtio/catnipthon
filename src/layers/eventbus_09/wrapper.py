from __future__ import annotations

from collections.abc import Callable
from typing import Any

from src.layers.eventbus_09.event_bus import EventBus
from src.layers.eventbus_09.types import Event


class EventBusLayerApi:
    """09-eventbus public API: publish/subscribe event system."""

    def __init__(self) -> None:
        self._bus = EventBus()

    def publish(self, event_type: str, payload: dict[str, Any] | None = None) -> Event:
        return self._bus.publish(event_type, payload)

    def subscribe(
        self, event_type: str, callback: Callable[[Event], None]
    ) -> Callable[[], None]:
        return self._bus.subscribe(event_type, callback)

    def get_history(self, event_type: str | None = None) -> list[Event]:
        return self._bus.get_history(event_type)
