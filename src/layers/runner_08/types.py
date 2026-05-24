from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class StepResult:
    """Result of a single agent step."""

    step_number: int
    tool_call_id: str = ""
    tool_name: str = ""
    tool_arguments: dict[str, Any] = field(default_factory=dict)
    tool_result: str = ""
    tool_success: bool = True
    finished: bool = False
    answer: str = ""


@dataclass
class RunnerConfig:
    """Configuration for the agent runner."""

    max_steps: int = 10
    max_tool_retries: int = 2
    continue_on_tool_error: bool = False
    provider: str = ""  # "heuristic" | "deepseek"; empty = auto-detect

    def __post_init__(self) -> None:
        if not self.provider:
            self.provider = os.environ.get("CATNIP_RUNNER_PROVIDER", "deepseek")
