from __future__ import annotations

from src.shared.types import RunTask
from src.layers.eventbus_09 import EventBusLayerApi
from src.layers.context_05 import ContextLayerApi
from src.layers.skills_06 import SkillsLayerApi
from src.layers.memory_07 import MemoryLayerApi
from src.layers.runner_08 import RunnerLayerApi
from src.layers.tool_registry_10 import ToolRegistryLayerApi
from src.layers.executor_11 import ExecutorLayerApi
from src.layers.harness_04 import HarnessLayerApi


def _make_harness() -> HarnessLayerApi:
    """Helper to create a fully-wired harness for testing."""
    eventbus = EventBusLayerApi()
    context = ContextLayerApi()
    skills = SkillsLayerApi()
    memory = MemoryLayerApi()
    registry = ToolRegistryLayerApi()
    executor = ExecutorLayerApi(eventbus, registry)  # noqa: F841
    runner = RunnerLayerApi(eventbus, registry)
    return HarnessLayerApi(eventbus, context, skills, memory, runner)


def test_harness_run_returns_report() -> None:
    harness = _make_harness()

    task = RunTask(id="test1", user_message="run tests")
    result = harness.run(task)

    assert result is not None
    assert len(result) > 0


def test_harness_publishes_run_events() -> None:
    harness = _make_harness()

    task = RunTask(id="test2", user_message="check context")
    harness.run(task)

    # Access the eventbus through the harness - check event types
    history = harness._eventbus.get_history()
    types = [e.type for e in history]
    assert "run.started" in types
    assert "run.finished" in types
    assert "prompt.composed" in types


def test_harness_metrics_do_not_accumulate_across_runs(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("CATNIP_RUNNER_PROVIDER", "heuristic")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    harness = _make_harness()

    first = harness.run(RunTask(id="first", user_message="run tests"))
    second = harness.run(RunTask(id="second", user_message="run tests"))

    assert "Steps: 2" in first
    assert "Tools used: list_files (1), read_file (1)" in first
    assert "Steps: 2" in second
    assert "Tools used: list_files (1), read_file (1)" in second
