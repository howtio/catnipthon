from __future__ import annotations

import time
from collections import deque
from src.shared.types import RunTask, TaskStatus
from src.layers.queue_02.task_status_store import TaskStatusStore


class InMemoryQueue:
    """FIFO queue backed by a deque and a status store."""

    def __init__(self, store: TaskStatusStore) -> None:
        self._queue: deque[RunTask] = deque()
        self._store = store

    def enqueue(self, task: RunTask) -> None:
        self._queue.append(task)
        self._store.set(task)

    def dequeue(self) -> RunTask | None:
        if not self._queue:
            return None
        task = self._queue.popleft()
        task.status = "running"
        task.started_at = time.time()
        return task

    def peek(self) -> RunTask | None:
        if not self._queue:
            return None
        return self._queue[0]

    @property
    def size(self) -> int:
        return len(self._queue)

    @property
    def is_empty(self) -> bool:
        return len(self._queue) == 0

    def get_task(self, task_id: str) -> RunTask | None:
        return self._store.get(task_id)

    def update_status(self, task_id: str, status: TaskStatus) -> None:
        self._store.update_status(task_id, status)
