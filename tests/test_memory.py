from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.layers.memory_07 import MemoryLayerApi, MemorySnapshot


@pytest.mark.asyncio
async def test_load_snapshot_creates_default() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        mem = MemoryLayerApi(storage_path=str(Path(tmp) / "mem.json"))
        snap = await mem.load_snapshot()
        assert isinstance(snap, MemorySnapshot)
        assert snap.session_entries == []


@pytest.mark.asyncio
async def test_save_and_load_snapshot() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "mem.json")
        mem = MemoryLayerApi(storage_path=path)

        snap = await mem.load_snapshot()
        snap.session_entries.append("entry 1")
        snap.carryover_tasks.append("finish refactor")
        await mem.save_snapshot()

        # Load in a new instance
        mem2 = MemoryLayerApi(storage_path=path)
        snap2 = await mem2.load_snapshot()
        assert "entry 1" in snap2.session_entries
        assert "finish refactor" in snap2.carryover_tasks


@pytest.mark.asyncio
async def test_add_session_entry_trims_old() -> None:
    mem = MemoryLayerApi()
    await mem.load_snapshot()
    for i in range(60):
        mem.add_session_entry(f"entry {i}")
    snap = mem.current_snapshot()
    assert len(snap.session_entries) == 50
    assert snap.session_entries[-1] == "entry 59"


@pytest.mark.asyncio
async def test_add_observation_trims_old() -> None:
    mem = MemoryLayerApi()
    await mem.load_snapshot()
    for i in range(25):
        mem.add_observation(f"obs {i}")
    snap = mem.current_snapshot()
    assert len(snap.observations) == 20


def test_set_focused_file_adds_to_recent() -> None:
    mem = MemoryLayerApi()
    mem.set_focused_file("src/main.py")
    mem.set_focused_file("src/bootstrap.py")
    snap = mem.current_snapshot()
    assert snap.working_set.focused_file_path == "src/bootstrap.py"
    assert "src/main.py" in snap.working_set.recent_file_paths
    assert "src/bootstrap.py" in snap.working_set.recent_file_paths


def test_set_focused_file_trims_old() -> None:
    mem = MemoryLayerApi()
    for i in range(15):
        mem.set_focused_file(f"file_{i}.py")
    snap = mem.current_snapshot()
    assert len(snap.working_set.recent_file_paths) == 10


def test_inject_memory_prompt_no_data() -> None:
    mem = MemoryLayerApi()
    prompt = mem.inject_memory_prompt()
    assert "(no prior memory)" in prompt


def test_inject_memory_prompt_with_data() -> None:
    mem = MemoryLayerApi()
    snap = mem.current_snapshot()
    snap.observations.append("tool result: created file")
    snap.working_set.recent_file_paths.append("src/main.py")
    snap.carryover_tasks.append("run tests")
    prompt = mem.inject_memory_prompt()
    assert "tool result" in prompt
    assert "src/main.py" in prompt
    assert "run tests" in prompt
    assert "(no prior memory)" not in prompt
