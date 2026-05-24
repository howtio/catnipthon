from __future__ import annotations

from src.shared.types import RunTask, TaskStatus


class TaskStatusStore:
    """Thread-safe store mapping task_id -> task with status."""

    def __init__(self) -> None:
        self._tasks: dict[str, RunTask] = {}

    def set(self, task: RunTask) -> None:
        self._tasks[task.id] = task

    def get(self, task_id: str) -> RunTask | None:
        return self._tasks.get(task_id)

    def update_status(self, task_id: str, status: TaskStatus) -> None:
        task = self._tasks.get(task_id)
        if task is not None:
            task.status = status

    def remove(self, task_id: str) -> None:
        self._tasks.pop(task_id, None)
