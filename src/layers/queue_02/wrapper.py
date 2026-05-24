from __future__ import annotations

from src.shared.types import RunTask, TaskStatus
from src.layers.queue_02.in_memory_queue import InMemoryQueue
from src.layers.queue_02.task_status_store import TaskStatusStore
from src.layers.queue_02.enqueue_task import enqueue_task
from src.layers.queue_02.dequeue_task import dequeue_task


class QueueLayerApi:
    """02-queue public API: FIFO task queue with status management."""

    def __init__(self) -> None:
        self._store = TaskStatusStore()
        self._queue = InMemoryQueue(self._store)

    def enqueue(self, task: RunTask) -> None:
        """Add a task to the queue (status → pending)."""
        enqueue_task(self._queue, task)

    def dequeue(self) -> RunTask | None:
        """Pop the next pending task (status → running)."""
        return dequeue_task(self._queue)

    def get_task(self, task_id: str) -> RunTask | None:
        """Look up a task by ID."""
        return self._queue.get_task(task_id)

    def update_status(self, task_id: str, status: TaskStatus) -> None:
        """Update the status of a task."""
        self._queue.update_status(task_id, status)

    @property
    def size(self) -> int:
        return self._queue.size

    @property
    def is_empty(self) -> bool:
        return self._queue.is_empty
