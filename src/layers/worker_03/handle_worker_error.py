from __future__ import annotations

from src.shared.errors import WorkerError
from src.layers.queue_02 import QueueLayerApi


def handle_worker_error(
    queue: QueueLayerApi, task_id: str, exception: Exception
) -> None:
    """Catch and record a worker processing error."""
    error_msg = f"{type(exception).__name__}: {exception}"
    queue.update_status(task_id, "failed")
    task = queue.get_task(task_id)
    if task is not None:
        task.error = error_msg

    raise WorkerError(error_msg) from exception
