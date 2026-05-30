from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Event:
    type: str
    payload: dict[str, Any] = field(default_factory=dict)


class EventBusError(Exception):
    """Base error for EventBus layer."""
