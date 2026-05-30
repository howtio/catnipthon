from __future__ import annotations

import uuid
import time

from src.layers.harness_04.types import RunInfo


def create_run(user_message: str) -> RunInfo:
    """Create a new run with a unique ID."""
    return RunInfo(
        run_id=uuid.uuid4().hex[:12],
        user_message=user_message,
        status="created",
    )
