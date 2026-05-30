from __future__ import annotations

from typing import Any

from src.layers.eventbus_09.event_bus import EventBus
from src.layers.eventbus_09.types import Event


def publish_event(
    bus: EventBus, event_type: str, payload: dict[str, Any] | None = None
) -> Event:
    """Convenience wrapper for EventBus.publish."""
    return bus.publish(event_type, payload)
