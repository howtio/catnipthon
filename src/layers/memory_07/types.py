from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class WorkingSet:
    """Current working objects for the session."""

    focused_file_path: str = ""
    focused_openable_html_path: str = ""
    recent_file_paths: list[str] = field(default_factory=list)
    openable_html_paths: list[str] = field(default_factory=list)


@dataclass
class MemorySnapshot:
    """Full memory snapshot for a session."""

    session_entries: list[str] = field(default_factory=list)
    working_set: WorkingSet = field(default_factory=WorkingSet)
    observations: list[str] = field(default_factory=list)
    project_recent_entries: list[str] = field(default_factory=list)
    carryover_tasks: list[str] = field(default_factory=list)
    startup_checklist: list[str] = field(default_factory=list)
