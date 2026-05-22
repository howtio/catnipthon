from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RunnerResult:
    answer: str
    steps_used: int
    tool_calls_made: int


class RunnerLayerApi:
    """Phase 2 placeholder — returns a mock answer. Real ReAct loop in Phase 3."""

    async def run(self, system_prompt: str, user_message: str) -> RunnerResult:
        answer = (
            f"[Phase 2 placeholder] Pretending to process: {user_message}\n"
            f"Context length: {len(system_prompt)} chars\n"
            "No tools called — Runner not yet connected to DeepSeek."
        )
        return RunnerResult(answer=answer, steps_used=0, tool_calls_made=0)
