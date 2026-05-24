"""In-process session memory — tracks files, tools, and user context.

No disk persistence. Gets injected as compact context before each run.
"""

from __future__ import annotations

from typing import Any


class SessionMemory:
    """Lightweight in-memory tracker for a single session.

    Tracks:
    - Files read / written during the session
    - Tools called (name → call_count)
    - User preferences / requirements mentioned
    - Last few conversation summaries
    """

    def __init__(self) -> None:
        self._files_read: set[str] = set()
        self._files_written: set[str] = set()
        self._tool_counts: dict[str, int] = {}
        self._user_notes: list[str] = []
        self._turn_summaries: list[str] = []

    # ── file tracking ──

    def track_file_read(self, path: str) -> None:
        self._files_read.add(path)

    def track_file_written(self, path: str) -> None:
        self._files_written.add(path)

    # ── tool tracking ──

    def track_tool_call(self, name: str, success: bool = True) -> None:
        self._tool_counts[name] = self._tool_counts.get(name, 0) + 1

    # ── user context ──

    def add_user_note(self, note: str) -> None:
        self._user_notes.append(note)
        if len(self._user_notes) > 10:
            self._user_notes = self._user_notes[-10:]

    def add_turn_summary(self, summary: str) -> None:
        self._turn_summaries.append(summary)
        if len(self._turn_summaries) > 10:
            self._turn_summaries = self._turn_summaries[-10:]

    # ── context generation ──

    def build_context(self) -> str:
        """Build a compact session memory block for system prompt injection."""
        parts: list[str] = []

        if self._files_read:
            files = sorted(self._files_read)
            parts.append(f"Read files ({len(files)}): {', '.join(files[:8])}")
            if len(files) > 8:
                parts[-1] += f" +{len(files) - 8} more"

        if self._files_written:
            files = sorted(self._files_written)
            parts.append(f"Written files ({len(files)}): {', '.join(files[:8])}")
            if len(files) > 8:
                parts[-1] += f" +{len(files) - 8} more"

        if self._tool_counts:
            tool_list = ", ".join(f"{n}({c})" for n, c in sorted(self._tool_counts.items()))
            parts.append(f"Tools used: {tool_list}")

        if self._user_notes:
            notes = "; ".join(self._user_notes[-3:])
            parts.append(f"User context: {notes}")

        if self._turn_summaries:
            parts.append("Recent turns:")
            for s in self._turn_summaries[-3:]:
                parts.append(f"  - {s}")

        return "\n".join(parts)

    def reset(self) -> None:
        self._files_read.clear()
        self._files_written.clear()
        self._tool_counts.clear()
        self._user_notes.clear()
        self._turn_summaries.clear()
