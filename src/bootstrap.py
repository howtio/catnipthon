"""Phase 3 wiring: all 11 layers are created in dependency order."""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from src.shared.types import RunTask
from src.shared.jsonl_logger import attach_jsonl_logger
from src.layers.gateway_01 import GatewayLayerApi, GatewayConfig
from src.layers.queue_02 import QueueLayerApi
from src.layers.worker_03 import WorkerLayerApi
from src.layers.eventbus_09 import EventBusLayerApi
from src.layers.context_05 import ContextLayerApi
from src.layers.skills_06 import SkillsLayerApi
from src.layers.memory_07 import MemoryLayerApi
from src.layers.runner_08 import RunnerLayerApi
from src.layers.tool_registry_10 import ToolRegistryLayerApi
from src.layers.executor_11 import ExecutorLayerApi
from src.layers.harness_04 import HarnessLayerApi


def _ensure_api_key() -> None:
    """Load DEEPSEEK_API_KEY from apikey.txt if env var not set."""
    if os.environ.get("DEEPSEEK_API_KEY"):
        return
    key_file = Path(__file__).resolve().parent.parent / "apikey.txt"
    if key_file.exists():
        for line in key_file.read_text(encoding="utf-8").strip().splitlines():
            line = line.strip()
            if line.startswith("DEEPSEEK_API_KEY="):
                val = line.split("=", 1)[1].strip()
                if val:
                    os.environ["DEEPSEEK_API_KEY"] = val


@dataclass
class App:
    gateway: GatewayLayerApi
    queue: QueueLayerApi
    worker: WorkerLayerApi
    eventbus: EventBusLayerApi
    context: ContextLayerApi
    skills: SkillsLayerApi
    memory: MemoryLayerApi
    runner: RunnerLayerApi
    tool_registry: ToolRegistryLayerApi
    executor: ExecutorLayerApi
    harness: HarnessLayerApi


def bootstrap() -> App:
    """Create and wire all layer instances (Phase 3)."""
    _ensure_api_key()

    # No-dependency layers (instantiation order doesn't matter within this group)
    queue = QueueLayerApi()
    eventbus = EventBusLayerApi()

    # Attach JSONL event logging (writes all events to logs/catnip.jsonl)
    attach_jsonl_logger(eventbus)

    context = ContextLayerApi()
    skills = SkillsLayerApi()
    memory = MemoryLayerApi()
    registry = ToolRegistryLayerApi()

    # EventBus + ToolRegistry needed by Executor and Runner
    executor = ExecutorLayerApi(eventbus, registry)
    runner = RunnerLayerApi(eventbus, registry)

    # Harness orchestrates the flow
    harness = HarnessLayerApi(eventbus, context, skills, memory, runner)

    # Worker uses Harness for processing
    worker = WorkerLayerApi(queue)
    harness_fn: Callable[[RunTask], str] = harness.run
    worker.set_process_fn(harness_fn)

    # Gateway bridges CLI to Queue → Worker
    gateway = GatewayLayerApi(queue, worker, GatewayConfig(worker_max_tasks=1))

    return App(
        gateway=gateway,
        queue=queue,
        worker=worker,
        eventbus=eventbus,
        context=context,
        skills=skills,
        memory=memory,
        runner=runner,
        tool_registry=registry,
        executor=executor,
        harness=harness,
    )
