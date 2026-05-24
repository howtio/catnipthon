from __future__ import annotations

from src.layers.context_05.types import ContextResult


def build_base_system_prompt(ctx: ContextResult) -> str:
    """Build the base system prompt from the assembled context."""
    parts: list[str] = []

    # Core instruction
    parts.append("You are catnip-agent, an 11-layer Coding Agent Runtime.")
    parts.append("")

    # Key documents
    if "CLAUDE.md" in ctx.documents:
        parts.append("## Project Rules (CLAUDE.md)")
        parts.append(ctx.documents["CLAUDE.md"])
        parts.append("")

    if ctx.documents:
        parts.append("## Available Documents")
        for name in sorted(ctx.documents.keys()):
            doc = ctx.documents[name]
            parts.append(f"### {name}")
            parts.append(doc[:2000])  # trim to avoid overflow
            parts.append("")

    # Workspace tree
    if ctx.workspace_tree:
        parts.append("## Workspace Structure")
        parts.append(ctx.workspace_tree)
        parts.append("")

    # Startup checklist
    if ctx.startup_checklist:
        parts.append("## Startup Checklist")
        for item in ctx.startup_checklist:
            parts.append(f"- [ ] {item}")
        parts.append("")

    # Carryover tasks
    if ctx.carryover_tasks:
        parts.append("## Carryover Tasks")
        for t in ctx.carryover_tasks:
            parts.append(f"- {t}")
        parts.append("")

    return "\n".join(parts)
