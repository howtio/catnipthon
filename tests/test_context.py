from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.layers.context_05 import ContextLayerApi
from src.shared import RunTask, create_id


def make_task(msg: str = "test task") -> RunTask:
    return RunTask(id=create_id(), user_message=msg)


@pytest.mark.asyncio
async def test_empty_workspace_is_handled() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp) / "empty_ws"
        ws.mkdir()
        ctx = ContextLayerApi(docs_dir=tmp, workspace_dir=str(ws))
        bundle = await ctx.build_context(make_task())
        assert "(empty workspace)" in bundle.workspace_summary


@pytest.mark.asyncio
async def test_workspace_scanning() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp) / "ws"
        ws.mkdir()
        (ws / "a.py").write_text("")
        (ws / "b").mkdir()
        (ws / "b" / "c.txt").write_text("")

        ctx = ContextLayerApi(docs_dir=tmp, workspace_dir=str(ws))
        bundle = await ctx.build_context(make_task())
        assert "a.py" in bundle.workspace_summary
        assert "b" in bundle.workspace_summary
        assert "c.txt" in bundle.workspace_summary


@pytest.mark.asyncio
async def test_system_prompt_includes_task() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        ctx = ContextLayerApi(docs_dir=tmp, workspace_dir=tmp)
        bundle = await ctx.build_context(make_task("build a web server"))
        assert "build a web server" in bundle.system_prompt
        assert "Current Task" in bundle.system_prompt


@pytest.mark.asyncio
async def test_startup_checklist_from_onboard() -> None:
    ctx = ContextLayerApi()
    bundle = await ctx.build_context(make_task())
    assert isinstance(bundle.startup_checklist, list)


@pytest.mark.asyncio
async def test_docs_loaded_in_context() -> None:
    ctx = ContextLayerApi()
    bundle = await ctx.build_context(make_task("create feature"))
    assert len(bundle.docs_summary) > 0
