from __future__ import annotations

import pytest

from src.layers.eventbus_09 import EventBusApi


@pytest.mark.asyncio
async def test_publish_and_subscribe() -> None:
    bus = EventBusApi()
    received: list[dict] = []

    async def handler(**kwargs) -> None:
        received.append(kwargs)

    bus.subscribe("test.event", handler)
    await bus.publish("test.event", key="value", count=1)

    assert len(received) == 1
    assert received[0]["key"] == "value"
    assert received[0]["count"] == 1


@pytest.mark.asyncio
async def test_multiple_subscribers() -> None:
    bus = EventBusApi()
    results: list[str] = []

    async def handler_a(**kwargs) -> None:
        results.append("a")

    async def handler_b(**kwargs) -> None:
        results.append("b")

    bus.subscribe("multi", handler_a)
    bus.subscribe("multi", handler_b)
    await bus.publish("multi")

    assert results == ["a", "b"]


@pytest.mark.asyncio
async def test_unsubscribe() -> None:
    bus = EventBusApi()
    calls: list[str] = []

    async def handler(**kwargs) -> None:
        calls.append("called")

    bus.subscribe("ev", handler)
    await bus.publish("ev")
    assert len(calls) == 1

    bus.unsubscribe("ev", handler)
    await bus.publish("ev")
    assert len(calls) == 1  # not called again


@pytest.mark.asyncio
async def test_no_subscribers_does_not_error() -> None:
    bus = EventBusApi()
    await bus.publish("no.listeners")


@pytest.mark.asyncio
async def test_multiple_event_types() -> None:
    bus = EventBusApi()
    events: list[str] = []

    async def on_a(**kwargs) -> None:
        events.append("a")

    async def on_b(**kwargs) -> None:
        events.append("b")

    bus.subscribe("type.a", on_a)
    bus.subscribe("type.b", on_b)
    await bus.publish("type.a")
    await bus.publish("type.b")

    assert events == ["a", "b"]
