from __future__ import annotations

from src.shared.types import RunTask
from src.layers.eventbus_09 import EventBusLayerApi
from src.layers.context_05 import ContextLayerApi
from src.layers.skills_06 import SkillsLayerApi
from src.layers.memory_07 import MemoryLayerApi
from src.layers.harness_04 import HarnessLayerApi


def test_harness_run_returns_report() -> None:
    eventbus = EventBusLayerApi()
    context = ContextLayerApi()
    skills = SkillsLayerApi()
    memory = MemoryLayerApi()
    harness = HarnessLayerApi(eventbus, context, skills, memory)

    task = RunTask(id="test1", user_message="run tests")
    result = harness.run(task)

    assert result is not None
    assert len(result) > 0
    assert "Phase 2 mock" in result


def test_harness_publishes_run_events() -> None:
    eventbus = EventBusLayerApi()
    context = ContextLayerApi()
    skills = SkillsLayerApi()
    memory = MemoryLayerApi()
    harness = HarnessLayerApi(eventbus, context, skills, memory)

    task = RunTask(id="test2", user_message="check context")
    harness.run(task)

    history = eventbus.get_history()
    types = [e.type for e in history]
    assert "run.started" in types
    assert "run.finished" in types
    assert "prompt.composed" in types
