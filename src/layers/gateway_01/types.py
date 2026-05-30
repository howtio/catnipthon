from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GatewayConfig:
    """Configuration for the CLI gateway."""

    worker_max_tasks: int = 1
