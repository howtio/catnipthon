from __future__ import annotations

import json
import time
from pathlib import Path

from src.layers.memory_07.types import MemorySnapshot, WorkingSet


DEFAULT_MEMORY_FILE = Path(__file__).resolve().parent.parent.parent.parent / "logs" / "catnip-memory.json"


class MemoryLayerApi:
    """07-memory public API: session/working/project memory management."""

    def __init__(self, storage_path: str | Path | None = None) -> None:
        self._path = Path(storage_path) if storage_path else DEFAULT_MEMORY_FILE
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._memory = self._load()

    # --- public API ---

    def get_snapshot(self) -> MemorySnapshot:
        return self._memory

    def add_session_entry(self, entry: str) -> None:
        self._memory.session_entries.append(f"[{time.strftime('%H:%M:%S')}] {entry}")
        self._trim_session()
        self._save()

    def add_observation(self, obs: str) -> None:
        self._memory.observations.append(obs)
        if len(self._memory.observations) > 50:
            self._memory.observations = self._memory.observations[-50:]
        self._save()

    def set_focused_file(self, path: str) -> None:
        self._memory.working_set.focused_file_path = path
        self._update_recent(path)
        self._save()

    def add_carryover_task(self, task: str) -> None:
        self._memory.carryover_tasks.append(task)
        self._save()

    def set_startup_checklist(self, items: list[str]) -> None:
        self._memory.startup_checklist = items
        self._save()

    def build_memory_block(self) -> str:
        """Build a formatted memory block for injection into system prompt."""
        mem = self._memory
        parts: list[str] = []

        if mem.session_entries:
            parts.append("## Recent Session Activity")
            for e in mem.session_entries[-5:]:
                parts.append(f"- {e}")

        ws = mem.working_set
        if ws.focused_file_path:
            parts.append(f"\nFocused file: {ws.focused_file_path}")
        if ws.recent_file_paths:
            parts.append(f"Recent files: {', '.join(ws.recent_file_paths[-3:])}")

        if mem.observations:
            parts.append("\n## Observations")
            for obs in mem.observations[-3:]:
                parts.append(f"- {obs}")

        if mem.carryover_tasks:
            parts.append("\n## Carryover Tasks")
            for t in mem.carryover_tasks:
                parts.append(f"- {t}")

        return "\n".join(parts)

    def add_conversation_turn(self, user_msg: str, assistant_reply: str) -> None:
        """Record a user ↔ assistant turn in conversation history."""
        self._memory.conversation_history.append({
            "role": "user", "content": user_msg,
        })
        self._memory.conversation_history.append({
            "role": "assistant", "content": assistant_reply,
        })
        if len(self._memory.conversation_history) > 40:
            self._memory.conversation_history = self._memory.conversation_history[-40:]
        self._memory.session_entries.append(f"[{time.strftime('%H:%M:%S')}] Q: {user_msg[:60]}")
        self._save()

    def get_conversation_history(self, max_turns: int = 10) -> list[dict[str, str]]:
        """Return recent conversation history for injection into agent context."""
        # Return last max_turns*2 messages (each turn = user + assistant)
        n = max_turns * 2
        return self._memory.conversation_history[-n:]

    def set_conversation_history(self, history: list[dict[str, str]]) -> None:
        """Replace full conversation history (used by REPL to sync)."""
        self._memory.conversation_history = list(history)
        self._save()

    def clear_session(self) -> None:
        self._memory.session_entries.clear()
        self._memory.observations.clear()
        self._memory.conversation_history.clear()
        self._save()

    # --- internals ---

    def _load(self) -> MemorySnapshot:
        try:
            if self._path.is_file():
                data = json.loads(self._path.read_text(encoding="utf-8"))
                if "working_set" in data and isinstance(data["working_set"], dict):
                    data["working_set"] = WorkingSet(**data["working_set"])
                return MemorySnapshot(**data)
        except Exception:
            pass
        return MemorySnapshot()

    def _save(self) -> None:
        try:
            self._path.write_text(
                json.dumps(self._memory, default=vars, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    def _trim_session(self) -> None:
        if len(self._memory.session_entries) > 50:
            self._memory.session_entries = self._memory.session_entries[-50:]

    def _update_recent(self, path: str) -> None:
        recent = self._memory.working_set.recent_file_paths
        if path in recent:
            recent.remove(path)
        recent.append(path)
        if len(recent) > 10:
            self._memory.working_set.recent_file_paths = recent[-10:]
