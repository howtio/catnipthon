from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.layers.context_05 import ContextLayerApi
from src.layers.eventbus_09 import EventBusApi
from src.layers.harness_04 import HarnessLayerApi
from src.layers.memory_07 import MemoryLayerApi
from src.layers.runner_08 import RunnerLayerApi
from src.layers.skills_06 import SkillsLayerApi
from src.shared import RunTask, create_id


def make_task(msg: str = "integration test") -> RunTask:
    return RunTask(id=create_id(), user_message=msg)


@pytest.mark.asyncio
async def test_harness_full_pipeline() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        eventbus = EventBusApi()
        context = ContextLayerApi(docs_dir="docs", workspace_dir=tmp)
        skills = SkillsLayerApi()
        memory = MemoryLayerApi(storage_path=str(Path(tmp) / "mem.json"))
        runner = RunnerLayerApi()
        harness = HarnessLayerApi(context, skills, memory, runner, eventbus)

        task = make_task("build a demo app")
        result = await harness.run(task)

        assert result.result is not None
        assert "Final Report" in result.result
        assert result.finished_at is not None


@pytest.mark.asyncio
async def test_harness_publishes_run_events() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        eventbus = EventBusApi()
        events: list[str] = []

        async def capture(**kwargs) -> None:
            events.append(kwargs["event_type"])

        # We need the event type in the callback. Let's subscribe specifically.
        async def on_started(**kwargs) -> None:
            events.append("started")

        async def on_finished(**kwargs) -> None:
            events.append("finished")

        eventbus.subscribe("run.started", on_started)
        eventbus.subscribe("run.finished", on_finished)

        context = ContextLayerApi(docs_dir="docs", workspace_dir=tmp)
        skills = SkillsLayerApi()
        memory = MemoryLayerApi(storage_path=str(Path(tmp) / "mem.json"))
        runner = RunnerLayerApi()
        harness = HarnessLayerApi(context, skills, memory, runner, eventbus)

        await harness.run(make_task())

        assert "started" in events
        assert "finished" in events


@pytest.mark.asyncio
async def test_harness_result_contains_skill_info() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        eventbus = EventBusApi()
        context = ContextLayerApi(docs_dir="docs", workspace_dir=tmp)
        skills = SkillsLayerApi()
        memory = MemoryLayerApi(storage_path=str(Path(tmp) / "mem.json"))
        runner = RunnerLayerApi()
        harness = HarnessLayerApi(context, skills, memory, runner, eventbus)

        result = await harness.run(make_task("write test code"))
        assert result.result is not None
        assert "testing" in result.result  # skill matched
