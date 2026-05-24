from __future__ import annotations

from src.layers.queue_02 import QueueLayerApi
from src.shared.types import RunTask


def test_enqueue_dequeue() -> None:
    queue = QueueLayerApi()
    task = RunTask(id="t1", user_message="hello")

    queue.enqueue(task)
    assert queue.size == 1
    assert queue.is_empty is False

    dequeued = queue.dequeue()
    assert dequeued is not None
    assert dequeued.id == "t1"
    assert dequeued.status == "running"


def test_dequeue_empty() -> None:
    queue = QueueLayerApi()
    assert queue.dequeue() is None
    assert queue.is_empty is True


def test_get_task() -> None:
    queue = QueueLayerApi()
    task = RunTask(id="t2", user_message="world")

    queue.enqueue(task)
    fetched = queue.get_task("t2")
    assert fetched is not None
    assert fetched.user_message == "world"
    assert fetched.status == "pending"


def test_get_task_not_found() -> None:
    queue = QueueLayerApi()
    assert queue.get_task("nonexistent") is None
