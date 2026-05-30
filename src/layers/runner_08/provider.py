from __future__ import annotations

from typing import Any

from src.shared.types import RunTask
from src.layers.runner_08.types import RunnerConfig


def heuristic_plan(task: RunTask) -> list[dict[str, Any]]:
    """Generate a heuristic tool plan based on the user message.

    Phase 3: simple keyword-based routing that produces a sequence
    of tool calls to explore and answer the user's request.
    """
    msg = task.user_message.lower()
    plan: list[dict[str, Any]] = []

    if "list" in msg or "file" in msg or "show" in msg or "tree" in msg:
        plan.append({"tool": "list_files", "args": {"path": "."}})

    if "read" in msg or "show" in msg or "cat" in msg:
        plan.append({"tool": "read_file", "args": {"file_path": "src/main.py"}})

    if "diff" in msg or "git" in msg or "change" in msg:
        plan.append({"tool": "git_diff", "args": {}})

    if not plan:
        # Default: explore + read main
        plan = [
            {"tool": "list_files", "args": {"path": "."}},
            {"tool": "read_file", "args": {"file_path": "src/main.py"}},
        ]

    return plan
