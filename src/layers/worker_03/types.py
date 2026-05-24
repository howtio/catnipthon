from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class WorkerConfig:
    """Configuration for the worker loop."""

    poll_interval_seconds: float = 0.1
    max_tasks: int = 0  # 0 = unlimited
    heartbeat_interval_seconds: float = 5.0
