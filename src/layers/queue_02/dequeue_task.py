from __future__ import annotations

from src.shared.types import RunTask
from src.layers.queue_02.in_memory_queue import InMemoryQueue


def dequeue_task(queue: InMemoryQueue) -> RunTask | None:
    """Dequeue the next pending task (FIFO order)."""
    return queue.dequeue()
