"""Runner placeholder for Phase 2. Phase 3 will implement the real ReAct loop."""

from __future__ import annotations

from src.shared.types import RunTask


class RunnerLayerApi:
    """08-runner placeholder — returns mock results."""

    def run(self, task: RunTask) -> str:
        return f"[mock runner] processed task {task.id}: {task.user_message}"
