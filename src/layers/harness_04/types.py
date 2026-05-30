from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RunInfo:
    """Metadata for a single run."""

    run_id: str
    user_message: str
    status: str = "created"
    steps_used: int = 0
    duration_ms: float = 0.0
    final_answer: str = ""
    tool_summary: dict[str, int] = field(default_factory=dict)
    modified_files: list[str] = field(default_factory=list)
    token_usage: dict[str, int] = field(default_factory=dict)


@dataclass
class FinalReport:
    """The final output of a run."""

    run_id: str
    steps_used: int
    duration_ms: float
    final_answer: str
    tool_summary: dict[str, Any]
    modified_files: list[str]
    risks: list[str]
    rollback_guide: str
    token_usage: dict[str, int] = field(default_factory=dict)
