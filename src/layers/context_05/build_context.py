from __future__ import annotations

from src.layers.context_05.types import ContextResult
from src.layers.context_05.load_docs import load_documents
from src.layers.context_05.scan_workspace import scan_workspace
from src.layers.context_05.build_base_system_prompt import build_base_system_prompt


def build_context() -> ContextResult:
    """Assemble the full context: docs + workspace + system prompt."""
    ctx = ContextResult()

    # Load documents
    ctx.documents = load_documents()

    # Scan workspace
    ctx.workspace_tree = scan_workspace()

    # Placeholder startup checklist (extend as Phase 2 matures)
    ctx.startup_checklist = [
        "Read ONBOARD.md",
        "Read docs/DEV_PROGRESS.md",
        "Run mypy src/",
        "Run pytest",
    ]

    # Build system prompt
    ctx.system_prompt = build_base_system_prompt(ctx)

    return ctx
