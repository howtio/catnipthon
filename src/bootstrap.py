"""Phase 2 wiring: all 8 layers (Gateway → Queue → Worker → Harness → Context → Skills → Memory → EventBus)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from src.shared.types import RunTask
from src.layers.gateway_01 import GatewayLayerApi, GatewayConfig
from src.layers.queue_02 import QueueLayerApi
from src.layers.worker_03 import WorkerLayerApi
from src.layers.eventbus_09 import EventBusLayerApi
from src.layers.context_05 import ContextLayerApi
from src.layers.skills_06 import SkillsLayerApi
from src.layers.memory_07 import MemoryLayerApi
from src.layers.harness_04 import HarnessLayerApi


@dataclass
class App:
    gateway: GatewayLayerApi
    queue: QueueLayerApi
    worker: WorkerLayerApi
    eventbus: EventBusLayerApi
    context: ContextLayerApi
    skills: SkillsLayerApi
    memory: MemoryLayerApi
    harness: HarnessLayerApi


def bootstrap() -> App:
    """Create and wire all layer instances (Phase 2)."""
    queue = QueueLayerApi()
    eventbus = EventBusLayerApi()
    context = ContextLayerApi()
    skills = SkillsLayerApi()
    memory = MemoryLayerApi()
    harness = HarnessLayerApi(eventbus, context, skills, memory)
    worker = WorkerLayerApi(queue)

    harness_fn: Callable[[RunTask], str] = harness.run
    worker.set_process_fn(harness_fn)

    gateway = GatewayLayerApi(queue, worker, GatewayConfig(worker_max_tasks=1))

    return App(
        gateway=gateway,
        queue=queue,
        worker=worker,
        eventbus=eventbus,
        context=context,
        skills=skills,
        memory=memory,
        harness=harness,
    )
