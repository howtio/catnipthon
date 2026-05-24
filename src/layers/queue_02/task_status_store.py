from __future__ import annotations

import threading
import time

from src.shared.types import RunTask, TaskStatus


class TaskStatusStore:
    """Thread-safe store mapping task_id -> task with status."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._tasks: dict[str, RunTask] = {}

    def set(self, task: RunTask) -> None:
        with self._lock:
            self._tasks[task.id] = task

    def get(self, task_id: str) -> RunTask | None:
        with self._lock:
            return self._tasks.get(task_id)

    def update_status(self, task_id: str, status: TaskStatus) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is not None:
                task.status = status

    def remove(self, task_id: str) -> None:
        with self._lock:
            self._tasks.pop(task_id, None)

    def append_requirement(self, task_id: str, requirement: str) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is not None:
                task.appended_requirements.append(requirement)

    def update_heartbeat(self, task_id: str) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is not None:
                task.last_heartbeat_at = time.time()

    def get_stale_tasks(self, timeout: float) -> list[RunTask]:
        now = time.time()
        with self._lock:
            stale: list[RunTask] = []
            for task in self._tasks.values():
                if task.status == "running" and task.last_heartbeat_at is not None:
                    if now - task.last_heartbeat_at > timeout:
                        stale.append(task)
            return stale

    def get_running(self) -> list[RunTask]:
        with self._lock:
            return [t for t in self._tasks.values() if t.status == "running"]
