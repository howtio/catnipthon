from __future__ import annotations

from src.shared.types import RunTask
from src.layers.eventbus_09 import EventBusLayerApi, event_types
from src.layers.tool_registry_10 import ToolRegistryLayerApi
from src.layers.executor_11 import ExecutorLayerApi
from src.layers.runner_08 import RunnerLayerApi


def test_runner_requests_tool_via_eventbus() -> None:
    eventbus = EventBusLayerApi()
    registry = ToolRegistryLayerApi()
    executor = ExecutorLayerApi(eventbus, registry)  # noqa: F841 — subscribes automatically
    runner = RunnerLayerApi(eventbus, registry)

    task = RunTask(id="r1", user_message="list files")
    result = runner.run(task)

    assert result is not None
    # Should have called list_files tool
    history = eventbus.get_history(event_types.TOOL_CALL_REQUESTED)
    assert len(history) >= 1
    assert history[0].payload["tool_name"] == "list_files"


def test_runner_publishes_step_events() -> None:
    eventbus = EventBusLayerApi()
    registry = ToolRegistryLayerApi()
    executor = ExecutorLayerApi(eventbus, registry)
    runner = RunnerLayerApi(eventbus, registry)

    task = RunTask(id="r2", user_message="read main.py")
    runner.run(task)

    step_events = eventbus.get_history(event_types.AGENT_STEP_FINISHED)
    assert len(step_events) >= 1


def test_runner_produces_answer_event() -> None:
    eventbus = EventBusLayerApi()
    registry = ToolRegistryLayerApi()
    executor = ExecutorLayerApi(eventbus, registry)
    runner = RunnerLayerApi(eventbus, registry)

    task = RunTask(id="r3", user_message="git diff")
    runner.run(task)

    answer_events = eventbus.get_history(event_types.AGENT_ANSWER_PRODUCED)
    assert len(answer_events) == 1
