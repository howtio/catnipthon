from __future__ import annotations

from src.shared.types import RunTask
from src.layers.eventbus_09 import EventBusLayerApi
from src.layers.context_05 import ContextLayerApi
from src.layers.skills_06 import SkillsLayerApi
from src.layers.memory_07 import MemoryLayerApi
from src.layers.runner_08 import RunnerLayerApi
from src.layers.harness_04.run_lifecycle import run_lifecycle


class HarnessLayerApi:
    """04-harness public API: orchestrate a full run lifecycle."""

    def __init__(
        self,
        eventbus: EventBusLayerApi,
        context: ContextLayerApi,
        skills: SkillsLayerApi,
        memory: MemoryLayerApi,
        runner: RunnerLayerApi,
    ) -> None:
        self._eventbus = eventbus
        self._context = context
        self._skills = skills
        self._memory = memory
        self._runner = runner

    def run(self, task: RunTask) -> str:
        """Execute a complete run lifecycle."""
        return run_lifecycle(
            task, self._eventbus, self._context, self._skills, self._memory, self._runner
        )
