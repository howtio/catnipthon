from __future__ import annotations

import threading
import time
from collections.abc import Callable

from src.shared.types import RunTask
from src.layers.queue_02 import QueueLayerApi
from src.layers.worker_03.types import WorkerConfig
from src.layers.worker_03.run_worker_loop import run_worker_loop


class WorkerLayerApi:
    """03-worker public API: consume tasks from the queue."""

    def __init__(self, queue: QueueLayerApi) -> None:
        self._queue = queue
        self._process_fn: Callable[[RunTask], str] | None = None

    def set_process_fn(self, fn: Callable[[RunTask], str]) -> None:
        """Set the task processing function (replaces placeholder)."""
        self._process_fn = fn

    def run_once(
        self, config: WorkerConfig | None = None
    ) -> list[RunTask]:
        """Run the worker loop synchronously."""
        return run_worker_loop(self._queue, self._process_fn, config)

    def run_with_heartbeat(self, config: WorkerConfig | None = None) -> list[RunTask]:
        """Run the worker loop with a background heartbeat thread.

        The heartbeat thread refreshes the heartbeat timestamp for all
        running tasks at a regular interval so the queue layer can
        detect stale/dead tasks.
        """
        cfg = config or WorkerConfig()

        def _heartbeat_loop() -> None:
            while True:
                for task in self._queue.get_running_tasks():
                    self._queue.update_heartbeat(task.id)
                time.sleep(cfg.heartbeat_interval_seconds)

        t = threading.Thread(target=_heartbeat_loop, daemon=True)
        t.start()

        return run_worker_loop(self._queue, self._process_fn, config)
