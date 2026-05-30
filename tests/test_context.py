from __future__ import annotations

from src.layers.context_05 import ContextLayerApi


def test_context_has_action_rules() -> None:
    ctx = ContextLayerApi().get_context()
    assert "Call the right tool immediately" in ctx.system_prompt
    assert "One tool call per turn" in ctx.system_prompt


def test_context_has_system_prompt() -> None:
    ctx = ContextLayerApi().get_context()
    assert len(ctx.system_prompt) > 0
    assert "catnip-agent" in ctx.system_prompt


def test_context_has_workspace_tree() -> None:
    ctx = ContextLayerApi().get_context()
    assert len(ctx.workspace_tree) > 0
    assert "src" in ctx.workspace_tree or "gateway_01" in ctx.workspace_tree


def test_context_has_checklist() -> None:
    ctx = ContextLayerApi().get_context()
    assert len(ctx.startup_checklist) > 0
    assert "ONBOARD.md" in ctx.startup_checklist[0]
