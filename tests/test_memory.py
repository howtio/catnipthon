from __future__ import annotations

import tempfile
from pathlib import Path

from src.layers.memory_07 import MemoryLayerApi


def test_memory_add_session_entry() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        mem = MemoryLayerApi(Path(tmp) / "test_memory.json")
        mem.add_session_entry("test entry")
        snap = mem.get_snapshot()
        assert len(snap.session_entries) == 1
        assert "test entry" in snap.session_entries[0]


def test_memory_set_focused_file() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        mem = MemoryLayerApi(Path(tmp) / "test_memory.json")
        mem.set_focused_file("src/main.py")
        snap = mem.get_snapshot()
        assert snap.working_set.focused_file_path == "src/main.py"


def test_memory_clear_session() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        mem = MemoryLayerApi(Path(tmp) / "test_memory.json")
        mem.add_session_entry("entry 1")
        mem.add_session_entry("entry 2")
        mem.clear_session()
        snap = mem.get_snapshot()
        assert len(snap.session_entries) == 0


def test_memory_build_memory_block() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        mem = MemoryLayerApi(Path(tmp) / "test_memory.json")
        mem.add_session_entry("working on feature")
        mem.set_focused_file("src/main.py")
        block = mem.build_memory_block()
        assert len(block) > 0
        assert "main.py" in block or "Recent" in block
