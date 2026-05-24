from __future__ import annotations

import tempfile
from pathlib import Path

from src.layers.executor_11.tools import list_files, read_file, write_file, patch_file


def test_list_files_root() -> None:
    result = list_files(".")
    assert result is not None
    assert "src" in result or "README" in result or "pyproject.toml" in result


def test_read_file() -> None:
    result = read_file("pyproject.toml")
    assert result is not None
    assert "catnip-agent" in result


def test_read_file_not_found() -> None:
    result = read_file("nonexistent_file_xyz.txt")
    assert result.startswith("Error:")


def test_write_and_read() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "test_write.txt"
        result = write_file(str(path), "hello world")
        assert "Written" in result
        assert path.read_text() == "hello world"


def test_patch_file() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "test_patch.txt"
        path.write_text("foo bar foo")
        result = patch_file(str(path), "foo", "baz")
        assert "Patched" in result
        assert path.read_text() == "baz bar baz"


def test_patch_file_not_found() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "test_patch.txt"
        path.write_text("hello")
        result = patch_file(str(path), "nonexistent", "baz")
        assert "not found" in result
