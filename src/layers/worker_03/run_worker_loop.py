from __future__ import annotations

import time
from collections.abc import Callable

from src.shared.types import RunTask
from src.shared.logger import get_logger
from src.layers.queue_02 import QueueLayerApi
from src.layers.worker_03.types import WorkerConfig

log = get_logger("worker")


def run_worker_loop(
    queue: QueueLayerApi,
    process_fn: Callable[[RunTask], str] | None = None,
    config: WorkerConfig | None = None,
) -> list[RunTask]:
    """Synchronous worker loop: dequeue → process → repeat."""
    cfg = config or WorkerConfig()
    completed: list[RunTask] = []
    processed = 0

    while True:
        if cfg.max_tasks > 0 and processed >= cfg.max_tasks:
            break

        task = queue.dequeue()
        if task is None:
            if queue.is_empty:
                break
            time.sleep(cfg.poll_interval_seconds)
            continue

        log.info(f"Processing task {task.id}")
        if process_fn is not None:
            result = process_fn(task)
        else:
            result = f"Processed: {task.user_message}"

        task.status = "done"
        task.finished_at = time.time()
        task.result = str(result)
        completed.append(task)
        processed += 1

    return completed
