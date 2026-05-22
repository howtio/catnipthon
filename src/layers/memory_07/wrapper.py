from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class WorkingSet:
    focused_file_path: str | None = None
    focused_openable_html_path: str | None = None
    recent_file_paths: list[str] = field(default_factory=list)
    openable_html_paths: list[str] = field(default_factory=list)


@dataclass
class MemorySnapshot:
    session_entries: list[str] = field(default_factory=list)
    working_set: WorkingSet = field(default_factory=WorkingSet)
    observations: list[str] = field(default_factory=list)
    project_recent_entries: list[str] = field(default_factory=list)
    carryover_tasks: list[str] = field(default_factory=list)
    startup_checklist: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_entries": self.session_entries,
            "working_set": {
                "focused_file_path": self.working_set.focused_file_path,
                "focused_openable_html_path": (
                    self.working_set.focused_openable_html_path
                ),
                "recent_file_paths": self.working_set.recent_file_paths,
                "openable_html_paths": self.working_set.openable_html_paths,
            },
            "observations": self.observations,
            "project_recent_entries": self.project_recent_entries,
            "carryover_tasks": self.carryover_tasks,
            "startup_checklist": self.startup_checklist,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> MemorySnapshot:
        ws = d.get("working_set", {})
        return cls(
            session_entries=d.get("session_entries", []),
            working_set=WorkingSet(
                focused_file_path=ws.get("focused_file_path"),
                focused_openable_html_path=ws.get("focused_openable_html_path"),
                recent_file_paths=ws.get("recent_file_paths", []),
                openable_html_paths=ws.get("openable_html_paths", []),
            ),
            observations=d.get("observations", []),
            project_recent_entries=d.get("project_recent_entries", []),
            carryover_tasks=d.get("carryover_tasks", []),
            startup_checklist=d.get("startup_checklist", []),
        )


class MemoryLayerApi:
    """Session memory + working memory + persistence to local JSON."""

    def __init__(self, storage_path: str = "logs/catnip-memory.json") -> None:
        self._storage_path = Path(storage_path)
        self._snapshot: MemorySnapshot | None = None

    async def load_snapshot(self) -> MemorySnapshot:
        if self._storage_path.exists():
            try:
                data = json.loads(self._storage_path.read_text(encoding="utf-8"))
                self._snapshot = MemorySnapshot.from_dict(data)
                return self._snapshot
            except (json.JSONDecodeError, KeyError):
                pass
        self._snapshot = MemorySnapshot()
        return self._snapshot

    async def save_snapshot(self) -> None:
        if self._snapshot is None:
            return
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._storage_path.write_text(
            json.dumps(self._snapshot.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def current_snapshot(self) -> MemorySnapshot:
        if self._snapshot is None:
            self._snapshot = MemorySnapshot()
        return self._snapshot

    def add_session_entry(self, entry: str) -> None:
        snap = self.current_snapshot()
        snap.session_entries.append(entry)
        if len(snap.session_entries) > 50:
            snap.session_entries = snap.session_entries[-50:]

    def add_observation(self, observation: str) -> None:
        snap = self.current_snapshot()
        snap.observations.append(observation)
        if len(snap.observations) > 20:
            snap.observations = snap.observations[-20:]

    def set_focused_file(self, path: str) -> None:
        snap = self.current_snapshot()
        snap.working_set.focused_file_path = path
        if path not in snap.working_set.recent_file_paths:
            snap.working_set.recent_file_paths.append(path)
        if len(snap.working_set.recent_file_paths) > 10:
            snap.working_set.recent_file_paths = (
                snap.working_set.recent_file_paths[-10:]
            )

    def inject_memory_prompt(self) -> str:
        snap = self.current_snapshot()
        parts = ["## Memory Context"]
        if snap.carryover_tasks:
            parts.append("\n### Carry-over Tasks")
            for t in snap.carryover_tasks:
                parts.append(f"- {t}")
        if snap.observations:
            parts.append("\n### Recent Observations")
            for o in snap.observations[-5:]:
                parts.append(f"- {o}")
        if snap.working_set.recent_file_paths:
            parts.append("\n### Recently Touched Files")
            for f in snap.working_set.recent_file_paths[-5:]:
                parts.append(f"- {f}")
        if snap.startup_checklist:
            parts.append("\n### Startup Checklist")
            for item in snap.startup_checklist:
                parts.append(item)
        if len(parts) == 1:
            return "(no prior memory)"
        return "\n".join(parts)
