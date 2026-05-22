from __future__ import annotations

from dataclasses import dataclass

from src.layers.gateway_01 import GatewayLayerApi
from src.layers.harness_04 import HarnessLayerApi
from src.layers.queue_02 import QueueLayerApi
from src.layers.worker_03 import WorkerLayerApi


@dataclass
class App:
    queue: QueueLayerApi
    harness: HarnessLayerApi
    worker: WorkerLayerApi
    gateway: GatewayLayerApi


def bootstrap() -> App:
    queue = QueueLayerApi()
    harness = HarnessLayerApi()
    worker = WorkerLayerApi(queue, harness)
    gateway = GatewayLayerApi(queue)
    return App(queue=queue, harness=harness, worker=worker, gateway=gateway)
