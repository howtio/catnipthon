from __future__ import annotations

import uuid
from src.shared.types import RunTask
from src.layers.gateway_01.validate_user_input import validate_user_input


def create_run_task(user_message: str) -> RunTask:
    """Create a RunTask from a validated user message."""
    message = validate_user_input(user_message)
    return RunTask(
        id=uuid.uuid4().hex[:12],
        user_message=message,
    )
