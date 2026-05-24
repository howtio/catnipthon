from __future__ import annotations

from src.shared.types import RunTask
from src.layers.eventbus_09 import EventBusLayerApi
from src.layers.tool_registry_10 import ToolRegistryLayerApi
from src.layers.runner_08.types import RunnerConfig
from src.layers.runner_08.agent_runner import run_agent


class RunnerLayerApi:
    """08-runner public API: agent loop with heuristic planning and tool execution."""

    def __init__(
        self,
        eventbus: EventBusLayerApi,
        registry: ToolRegistryLayerApi,
    ) -> None:
        self._eventbus = eventbus
        self._registry = registry

    def run(
        self,
        task: RunTask,
        config: RunnerConfig | None = None,
    ) -> str:
        """Execute the agent loop and return the final answer."""
        return run_agent(task, self._eventbus, self._registry, config)
