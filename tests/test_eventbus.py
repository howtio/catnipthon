from __future__ import annotations

from src.layers.eventbus_09 import EventBusLayerApi, event_types


def test_publish_and_history() -> None:
    bus = EventBusLayerApi()
    bus.publish("test.event", {"key": "value"})
    history = bus.get_history()
    assert len(history) == 1
    assert history[0].type == "test.event"
    assert history[0].payload["key"] == "value"


def test_subscribe_callback() -> None:
    bus = EventBusLayerApi()
    received: list[str] = []

    def cb(event):
        received.append(event.type)

    bus.subscribe("my.event", cb)
    bus.publish("my.event", {})
    assert received == ["my.event"]


def test_unsubscribe() -> None:
    bus = EventBusLayerApi()
    received: list[str] = []

    def cb(event):
        received.append(event.type)

    unsub = bus.subscribe("my.event", cb)
    bus.publish("my.event", {})
    assert len(received) == 1

    unsub()
    bus.publish("my.event", {})
    assert len(received) == 1  # no additional call


def test_filtered_history() -> None:
    bus = EventBusLayerApi()
    bus.publish("a", {})
    bus.publish("b", {})
    bus.publish("a", {})

    a_events = bus.get_history("a")
    assert len(a_events) == 2

    b_events = bus.get_history("b")
    assert len(b_events) == 1


def test_run_event_types() -> None:
    bus = EventBusLayerApi()
    bus.publish(event_types.RUN_STARTED, {"run_id": "r1"})
    bus.publish(event_types.RUN_FINISHED, {"run_id": "r1"})
    bus.publish(event_types.PROMPT_COMPOSED, {"length": 100})

    assert len(bus.get_history()) == 3
