from __future__ import annotations

from src.shared.types import RunTask
from src.layers.queue_02 import QueueLayerApi
from src.layers.worker_03 import WorkerLayerApi, WorkerConfig
from src.layers.gateway_01.parse_cli_args import parse_cli_args
from src.layers.gateway_01.create_run_task import create_run_task
from src.layers.gateway_01.types import GatewayConfig


class GatewayLayerApi:
    """01-gateway public API: parse CLI input, create tasks, show results."""

    def __init__(
        self,
        queue: QueueLayerApi,
        worker: WorkerLayerApi,
        config: GatewayConfig | None = None,
    ) -> None:
        self._queue = queue
        self._worker = worker
        self._config = config or GatewayConfig()

    def run_cli(self, args: list[str] | None = None) -> str:
        """Parse CLI args, create task, enqueue, process, return result."""
        user_message = parse_cli_args(args)
        task = create_run_task(user_message)

        self._queue.enqueue(task)
        completed = self._worker.run_once(
            config=WorkerConfig(max_tasks=self._config.worker_max_tasks)
        )

        if completed:
            t = completed[0]
            return t.result or f"[no result from task {t.id}]"

        return f"[no tasks completed; task {task.id} status={task.status}]"
