from __future__ import annotations

from collections.abc import Callable

from src.layers.eventbus_09.event_bus import EventBus
from src.layers.eventbus_09.types import Event


def subscribe_event(
    bus: EventBus, event_type: str, callback: Callable[[Event], None]
) -> Callable[[], None]:
    """Convenience wrapper for EventBus.subscribe. Returns unsubscribe fn."""
    return bus.subscribe(event_type, callback)
