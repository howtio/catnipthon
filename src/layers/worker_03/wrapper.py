from __future__ import annotations

import asyncio

from src.layers.harness_04 import HarnessLayerApi
from src.layers.queue_02 import QueueLayerApi
from src.shared import RunTask, get_logger


class WorkerLayerApi:
    """Consumes tasks from Queue, delegates to Harness, handles errors."""

    def __init__(self, queue: QueueLayerApi, harness: HarnessLayerApi) -> None:
        self._queue = queue
        self._harness = harness
        self._log = get_logger("worker")
        self._running = False

    async def start(self) -> None:
        self._running = True
        self._log.info("Worker started")
        while self._running:
            try:
                task = await self._queue.dequeue()
                await self._process(task)
            except asyncio.CancelledError:
                self._log.info("Worker cancelled")
                break

    async def _process(self, task: RunTask) -> None:
        try:
            self._queue.update_task_status(task.id, "running")
            result = await self._harness.run(task)
            self._queue.update_task_status(
                task.id, "done", result=result.result
            )
        except Exception as exc:
            self._log.error("Task %s failed: %s", task.id, exc)
            self._queue.update_task_status(task.id, "failed", error=str(exc))

    def stop(self) -> None:
        self._running = False
