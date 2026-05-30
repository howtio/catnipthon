from __future__ import annotations

from src.shared.types import RunTask
from src.layers.queue_02.in_memory_queue import InMemoryQueue


def enqueue_task(queue: InMemoryQueue, task: RunTask) -> None:
    """Enqueue a task and update its status to pending."""
    task.status = "pending"
    queue.enqueue(task)
