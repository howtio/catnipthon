from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Literal

TaskStatus = Literal["pending", "running", "done", "failed"]


@dataclass
class RunTask:
    id: str
    user_message: str
    status: TaskStatus = "pending"
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    finished_at: float | None = None
    result: str | None = None
    error: str | None = None
