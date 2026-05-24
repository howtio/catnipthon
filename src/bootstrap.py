"""Phase 1 wiring: Gateway + Queue + Worker."""

from __future__ import annotations

from dataclasses import dataclass

from src.layers.gateway_01 import GatewayLayerApi
from src.layers.queue_02 import QueueLayerApi
from src.layers.worker_03 import WorkerLayerApi


@dataclass
class App:
    gateway: GatewayLayerApi
    queue: QueueLayerApi
    worker: WorkerLayerApi


def bootstrap() -> App:
    """Create and wire layer instances."""
    queue = QueueLayerApi()
    worker = WorkerLayerApi(queue)
    gateway = GatewayLayerApi(queue, worker)

    return App(gateway=gateway, queue=queue, worker=worker)
