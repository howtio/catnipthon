from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from src.shared import RunTask


@dataclass
class ContextBundle:
    task: RunTask
    docs_summary: str
    workspace_summary: str
    system_prompt: str
    startup_checklist: list[str] = field(default_factory=list)


class ContextLayerApi:
    """Loads docs, scans workspace, builds the system prompt."""

    def __init__(
        self,
        docs_dir: str = "docs",
        workspace_dir: str = "workspace",
    ) -> None:
        self._docs_dir = Path(docs_dir)
        self._workspace_dir = Path(workspace_dir)

    async def build_context(self, task: RunTask) -> ContextBundle:
        docs_summary = self._load_key_docs()
        workspace_summary = self._scan_workspace()
        startup_checklist = self._extract_startup_checklist()
        system_prompt = self._build_system_prompt(
            task, docs_summary, workspace_summary
        )
        return ContextBundle(
            task=task,
            docs_summary=docs_summary,
            workspace_summary=workspace_summary,
            system_prompt=system_prompt,
            startup_checklist=startup_checklist,
        )

    def _load_key_docs(self) -> str:
        key_files = [
            "ONBOARD.md",
            "CLAUDE.md",
            "CODEX_ARCHITECTURE.md",
            "CODEX_MASTER_REQUIREMENTS.md",
        ]
        parts: list[str] = []
        for name in key_files:
            path = self._docs_dir / name
            if not path.exists():
                path = Path(name)  # fallback to root
            if path.exists():
                content = path.read_text(encoding="utf-8")
                parts.append(f"--- {name} ---\n{content}")
        return "\n\n".join(parts)

    def _scan_workspace(self) -> str:
        if not self._workspace_dir.exists():
            return "(no workspace directory)"
        lines: list[str] = []
        for item in sorted(self._workspace_dir.rglob("*")):
            rel = item.relative_to(self._workspace_dir)
            type_tag = "DIR" if item.is_dir() else "FILE"
            lines.append(f"  [{type_tag}] {rel}")
        if not lines:
            return "(empty workspace)"
        return "Workspace contents:\n" + "\n".join(lines)

    def _extract_startup_checklist(self) -> list[str]:
        path = Path("ONBOARD.md")
        if not path.exists():
            return []
        text = path.read_text(encoding="utf-8")
        checklist: list[str] = []
        in_checklist = False
        for line in text.splitlines():
            if "开工强制清单" in line or "开工强制" in line:
                in_checklist = True
                continue
            if in_checklist and line.strip().startswith("- ["):
                checklist.append(line.strip())
            elif in_checklist and line.strip() == "```":
                break
        return checklist

    def _build_system_prompt(
        self,
        task: RunTask,
        docs_summary: str,
        workspace_summary: str,
    ) -> str:
        return (
            f"## Project Context\n\n{docs_summary}\n\n"
            f"## Workspace State\n\n{workspace_summary}\n\n"
            f"## Current Task\n\nUser message: {task.user_message}\n"
        )
