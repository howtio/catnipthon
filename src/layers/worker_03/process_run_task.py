from __future__ import annotations

from collections.abc import Callable

from src.shared.types import RunTask
from src.layers.queue_02 import QueueLayerApi
from src.layers.worker_03.mark_task_status import mark_task_done, mark_task_failed


def process_run_task(
    queue: QueueLayerApi,
    task: RunTask,
    process_fn: Callable[[RunTask], str] | None = None,
) -> None:
    """Process a single task: run process_fn or a default echo placeholder."""
    try:
        if process_fn is not None:
            result = process_fn(task)
        else:
            # Phase 1 placeholder: echo the message
            result = f"Processed: {task.user_message}"

        if not isinstance(result, str):
            result = str(result)

        mark_task_done(queue, task.id, result)

    except Exception as exc:
        mark_task_failed(queue, task.id, str(exc))
