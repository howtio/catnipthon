from __future__ import annotations

from dataclasses import dataclass

from src.layers.context_05 import ContextLayerApi
from src.layers.eventbus_09 import EventBusApi
from src.layers.gateway_01 import GatewayLayerApi
from src.layers.harness_04 import HarnessLayerApi
from src.layers.memory_07 import MemoryLayerApi
from src.layers.queue_02 import QueueLayerApi
from src.layers.runner_08 import RunnerLayerApi
from src.layers.skills_06 import SkillsLayerApi
from src.layers.worker_03 import WorkerLayerApi


@dataclass
class App:
    queue: QueueLayerApi
    eventbus: EventBusApi
    context: ContextLayerApi
    skills: SkillsLayerApi
    memory: MemoryLayerApi
    runner: RunnerLayerApi
    harness: HarnessLayerApi
    worker: WorkerLayerApi
    gateway: GatewayLayerApi


def bootstrap() -> App:
    queue = QueueLayerApi()
    eventbus = EventBusApi()
    context = ContextLayerApi()
    skills = SkillsLayerApi()
    memory = MemoryLayerApi()
    runner = RunnerLayerApi()
    harness = HarnessLayerApi(context, skills, memory, runner, eventbus)
    worker = WorkerLayerApi(queue, harness)
    gateway = GatewayLayerApi(queue)
    return App(
        queue=queue,
        eventbus=eventbus,
        context=context,
        skills=skills,
        memory=memory,
        runner=runner,
        harness=harness,
        worker=worker,
        gateway=gateway,
    )
