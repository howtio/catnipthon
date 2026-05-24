from __future__ import annotations

from src.layers.context_05.types import ContextResult


def _trim(text: str, max_chars: int = 800) -> str:
    """Trim document text: keep first max_chars/2 and last max_chars/2."""
    if len(text) <= max_chars:
        return text
    half = max_chars // 2
    return f"{text[:half]}\n... [trimmed to {max_chars}] ...\n{text[-half:]}"


def build_base_system_prompt(ctx: ContextResult) -> str:
    """Build a concise, action-oriented system prompt."""
    parts: list[str] = []

    # Core identity — short
    parts.append("You are catnip-agent, an 11-layer Coding Agent Runtime in the catnipthon project.")

    # Action rule — this is the most important instruction
    parts.append("")
    parts.append("## Rules")
    parts.append("- Call the right tool immediately. Do NOT explain what you're about to do — just do it.")
    parts.append("- One tool call per turn. No chitchat.")
    parts.append("- If a tool returns an error, try a different approach. Do NOT retry the same thing.")
    parts.append("- When done, give a one-line summary of what you did.")
    parts.append("")

    # Architecture rules (condensed from CLAUDE.md)
    if "CLAUDE.md" in ctx.documents:
        claude = ctx.documents["CLAUDE.md"]
        # Extract architecture iron rule section
        if "## 架构铁律" in claude:
            arch_section = claude.split("## 架构铁律")[1].split("##")[0].strip()
            parts.append("## Architecture")
            parts.append(arch_section)
            parts.append("")

    # Key documents (only first 600 chars each)
    if ctx.documents:
        parts.append("## Docs")
        for name in sorted(ctx.documents.keys()):
            doc = ctx.documents[name]
            parts.append(f"### {name}")
            parts.append(_trim(doc, max_chars=600))
            parts.append("")

    # Workspace tree
    if ctx.workspace_tree:
        parts.append("## Workspace")
        parts.append(ctx.workspace_tree[:1000])
        parts.append("")

    # Startup checklist
    if ctx.startup_checklist:
        parts.append("## Checklist")
        for item in ctx.startup_checklist:
            parts.append(f"- {item}")
        parts.append("")

    # Carryover tasks
    if ctx.carryover_tasks:
        parts.append("## Carryover")
        for t in ctx.carryover_tasks:
            parts.append(f"- {t}")
        parts.append("")

    return "\n".join(parts)
