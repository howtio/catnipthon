from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

EventCallback = Callable[..., Awaitable[None]]


class EventBusApi:
    """Simple async pub/sub event bus. In-memory only for MVP."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventCallback]] = {}

    async def publish(self, event_type: str, **kwargs: Any) -> None:
        callbacks = self._subscribers.get(event_type, [])
        for cb in callbacks:
            await cb(**kwargs)

    def subscribe(self, event_type: str, callback: EventCallback) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: EventCallback) -> None:
        callbacks = self._subscribers.get(event_type, [])
        if callback in callbacks:
            callbacks.remove(callback)
