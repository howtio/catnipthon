from __future__ import annotations

import time
from src.shared.types import TaskStatus
from src.layers.queue_02 import QueueLayerApi


def mark_task_done(queue: QueueLayerApi, task_id: str, result: str) -> None:
    """Mark a task as done with a result."""
    queue.update_status(task_id, "done")
    task = queue.get_task(task_id)
    if task is not None:
        task.finished_at = time.time()
        task.result = result


def mark_task_failed(queue: QueueLayerApi, task_id: str, error: str) -> None:
    """Mark a task as failed with an error message."""
    queue.update_status(task_id, "failed")
    task = queue.get_task(task_id)
    if task is not None:
        task.finished_at = time.time()
        task.error = error
