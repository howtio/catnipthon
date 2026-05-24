from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ContextResult:
    """The assembled context for a run."""

    system_prompt: str = ""
    documents: dict[str, str] = field(default_factory=dict)
    workspace_tree: str = ""
    startup_checklist: list[str] = field(default_factory=list)
    carryover_tasks: list[str] = field(default_factory=list)
