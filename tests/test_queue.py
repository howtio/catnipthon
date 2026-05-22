from __future__ import annotations

import asyncio

import pytest

from src.layers.queue_02 import QueueLayerApi
from src.shared import QueueError, RunTask, TaskStatus, create_id


def make_task(message: str = "test task") -> RunTask:
    return RunTask(id=create_id(), user_message=message)


@pytest.mark.asyncio
async def test_enqueue_and_dequeue_order() -> None:
    """Tasks are dequeued in FIFO order."""
    queue = QueueLayerApi()
    t1 = make_task("first")
    t2 = make_task("second")
    t3 = make_task("third")

    await queue.enqueue(t1)
    await queue.enqueue(t2)
    await queue.enqueue(t3)

    assert (await queue.dequeue()).id == t1.id
    assert (await queue.dequeue()).id == t2.id
    assert (await queue.dequeue()).id == t3.id


@pytest.mark.asyncio
async def test_task_status_transitions() -> None:
    """Task status transitions: pending → running → done."""
    queue = QueueLayerApi()
    task = make_task()
    await queue.enqueue(task)

    assert queue.get_task_status(task.id) == "pending"

    dequeued = await queue.dequeue()
    queue.update_task_status(dequeued.id, "running")
    assert queue.get_task_status(task.id) == "running"

    queue.update_task_status(dequeued.id, "done", result="all good")
    assert queue.get_task_status(task.id) == "done"


@pytest.mark.asyncio
async def test_task_status_transition_to_failed() -> None:
    """Task status transitions: pending → running → failed."""
    queue = QueueLayerApi()
    task = make_task()
    await queue.enqueue(task)

    dequeued = await queue.dequeue()
    queue.update_task_status(dequeued.id, "running")
    assert queue.get_task_status(task.id) == "running"

    queue.update_task_status(dequeued.id, "failed", error="something broke")
    assert queue.get_task_status(task.id) == "failed"

    snapshot = queue.get_task_snapshot(task.id)
    assert snapshot.error == "something broke"
    assert snapshot.result is None


@pytest.mark.asyncio
async def test_wait_for_completion_signals_on_done() -> None:
    """wait_for_completion returns when the task is marked done."""
    queue = QueueLayerApi()
    task = make_task()
    await queue.enqueue(task)

    dequeued = await queue.dequeue()
    queue.update_task_status(dequeued.id, "running")
    queue.update_task_status(dequeued.id, "done", result="finished")

    result = await queue.wait_for_completion(task.id)
    assert result.status == "done"
    assert result.result == "finished"


@pytest.mark.asyncio
async def test_wait_for_completion_signals_on_failed() -> None:
    """wait_for_completion returns when the task is marked failed."""
    queue = QueueLayerApi()
    task = make_task()
    await queue.enqueue(task)

    dequeued = await queue.dequeue()
    queue.update_task_status(dequeued.id, "running")
    queue.update_task_status(dequeued.id, "failed", error="crash")

    result = await queue.wait_for_completion(task.id)
    assert result.status == "failed"
    assert result.error == "crash"


def test_get_task_status_raises_for_unknown_id() -> None:
    """Querying an unknown task raises QueueError."""
    queue = QueueLayerApi()
    with pytest.raises(QueueError, match="not found"):
        queue.get_task_status("nonexistent")


def test_get_task_snapshot_raises_for_unknown_id() -> None:
    """Snapshot of an unknown task raises QueueError."""
    queue = QueueLayerApi()
    with pytest.raises(QueueError, match="not found"):
        queue.get_task_snapshot("nonexistent")


def test_initial_task_status_is_pending() -> None:
    """A freshly created RunTask has status 'pending'."""
    task = make_task()
    assert task.status == "pending"


@pytest.mark.asyncio
async def test_completion_via_worker_flow() -> None:
    """Integration: enqueue → dequeue → process → mark done → wait returns."""
    queue = QueueLayerApi()
    task = make_task("integration test")
    await queue.enqueue(task)

    # Simulate worker processing
    t = await queue.dequeue()
    queue.update_task_status(t.id, "running")
    queue.update_task_status(t.id, "done", result="processed by worker")

    result = await queue.wait_for_completion(task.id)
    assert result.status == "done"
    assert result.result == "processed by worker"
    assert result.finished_at is not None
