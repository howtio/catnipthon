"""Scaffold: dependency assembly point.

Wire your layer instances here and return them as an App.
See docs/CONSTRUCTION_PLAN.md for the phase-by-phase roadmap.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class App:
    """Replace with your wired layer instances as you implement each Phase."""


def bootstrap() -> App:
    """Create and wire your layer instances.

    Example (Phase 1):
        from src.layers.queue_02 import QueueLayerApi
        from src.layers.worker_03 import WorkerLayerApi
        ...
    """
    return App()
