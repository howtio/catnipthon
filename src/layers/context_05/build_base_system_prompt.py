from __future__ import annotations

from src.layers.context_05.types import ContextResult


def build_base_system_prompt(ctx: ContextResult) -> str:
    """Build system prompt — code-embedded rules, no document injection."""
    parts: list[str] = []

    parts.append("You are catnip-agent, a coding agent in the catnipthon project.")
    parts.append("")
    parts.append("## Rules")
    parts.append("- Call the right tool immediately. Do NOT explain what you are about to do.")
    parts.append("- One tool call per turn. No chitchat.")
    parts.append("- If a tool errors, try a different approach. Do NOT retry the same thing.")
    parts.append("- Prefer write_file/read_file for file ops. Use shell_exec ONLY for installing deps or running tests.")
    parts.append("- To show results, write an HTML file and open_browser. Do NOT use shell for file creation.")
    parts.append("- When done, give a one-line summary of what you did.")
    parts.append("")

    # Workspace tree (useful for file operations)
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
