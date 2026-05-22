from __future__ import annotations

import asyncio
import time

from src.shared import QueueError, RunTask, TaskStatus, get_logger


class QueueLayerApi:
    """In-memory FIFO task queue with status tracking and completion signaling."""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[RunTask] = asyncio.Queue()
        self._tasks: dict[str, RunTask] = {}
        self._completion_events: dict[str, asyncio.Event] = {}
        self._log = get_logger("queue")

    async def enqueue(self, task: RunTask) -> None:
        self._tasks[task.id] = task
        self._completion_events[task.id] = asyncio.Event()
        await self._queue.put(task)
        self._log.info("Task %s enqueued: %s", task.id, task.user_message[:60])

    async def dequeue(self) -> RunTask:
        task = await self._queue.get()
        self._log.info("Task %s dequeued", task.id)
        return task

    def get_task_status(self, task_id: str) -> TaskStatus:
        task = self._tasks.get(task_id)
        if task is None:
            raise QueueError(f"Task {task_id} not found")
        return task.status

    def get_task_snapshot(self, task_id: str) -> RunTask:
        task = self._tasks.get(task_id)
        if task is None:
            raise QueueError(f"Task {task_id} not found")
        return task

    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        *,
        result: str | None = None,
        error: str | None = None,
    ) -> None:
        task = self._tasks.get(task_id)
        if task is None:
            raise QueueError(f"Task {task_id} not found")
        task.status = status
        now = time.time()
        if status == "running" and task.started_at is None:
            task.started_at = now
        if status in ("done", "failed"):
            task.finished_at = now
        if result is not None:
            task.result = result
        if error is not None:
            task.error = error
        if status in ("done", "failed"):
            event = self._completion_events.get(task_id)
            if event:
                event.set()

    async def wait_for_completion(self, task_id: str) -> RunTask:
        event = self._completion_events.get(task_id)
        if event is None:
            raise QueueError(f"Task {task_id} not found")
        await event.wait()
        return self._tasks[task_id]
