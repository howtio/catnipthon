from __future__ import annotations

import time

from src.shared import RunTask, get_logger


class HarnessLayerApi:
    """Phase 1 placeholder — marks tasks done without real orchestration."""

    def __init__(self) -> None:
        self._log = get_logger("harness")

    async def run(self, task: RunTask) -> RunTask:
        self._log.info("Harness placeholder processing task %s", task.id)
        task.started_at = time.time()
        task.result = (
            f"[Phase 1 placeholder] Task {task.id} completed. "
            f"Message: {task.user_message}"
        )
        task.finished_at = time.time()
        task.status = "done"
        return task
