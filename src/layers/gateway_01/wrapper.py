from __future__ import annotations

import sys

from src.layers.queue_02 import QueueLayerApi
from src.shared import RunTask, create_id, get_logger


class GatewayLayerApi:
    """Entry point: parses CLI input, creates tasks, submits to Queue."""

    def __init__(self, queue: QueueLayerApi) -> None:
        self._queue = queue
        self._log = get_logger("gateway")

    async def submit(self, user_message: str) -> RunTask:
        task = RunTask(
            id=create_id(),
            user_message=user_message,
        )
        self._log.info("Submitting task %s", task.id)
        await self._queue.enqueue(task)
        result = await self._queue.wait_for_completion(task.id)
        self._log.info("Task %s finished with status %s", task.id, result.status)
        return result

    @staticmethod
    def parse_args() -> str:
        if len(sys.argv) > 1:
            return " ".join(sys.argv[1:])
        return "default task"
