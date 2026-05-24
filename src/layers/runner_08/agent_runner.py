from __future__ import annotations

import json
import time
import uuid

from src.shared.types import RunTask
from src.layers.eventbus_09 import EventBusLayerApi, event_types
from src.layers.tool_registry_10 import ToolRegistryLayerApi
from src.layers.runner_08.types import StepResult, RunnerConfig
from src.layers.runner_08.provider import heuristic_plan


def run_agent(
    task: RunTask,
    eventbus: EventBusLayerApi,
    registry: ToolRegistryLayerApi,
    config: RunnerConfig | None = None,
) -> str:
    """Run the agent loop with heuristic planning and tool execution.

    Phase 3: heuristic provider generates a plan, each step requests a
    tool via EventBus and waits for the result.
    """
    cfg = config or RunnerConfig()
    plan = heuristic_plan(task)

    if not plan:
        return f"[heuristic] No plan generated for: {task.user_message}"

    results: list[str] = []

    for step_idx, step in enumerate(plan[: cfg.max_steps]):
        tool_call_id = uuid.uuid4().hex[:12]

        eventbus.publish(event_types.TOOL_CALL_REQUESTED, {
            "tool_call_id": tool_call_id,
            "tool_name": step["tool"],
            "arguments": step["args"],
            "step": step_idx,
        })

        result_payload = eventbus.wait_for_tool_result(tool_call_id, timeout=30.0)

        if result_payload is None:
            results.append(f"[timeout] tool {step['tool']} did not respond")
            if not cfg.continue_on_tool_error:
                break
            continue

        if result_payload.get("error"):
            results.append(f"[error] {step['tool']}: {result_payload['error']}")
            if not cfg.continue_on_tool_error:
                break
        else:
            output = result_payload.get("output", "")
            try:
                parsed = json.loads(output)
                message = parsed.get("message", output)
            except (json.JSONDecodeError, TypeError):
                message = output
            results.append(f"[{step['tool']}] {message}")

        eventbus.publish(event_types.AGENT_STEP_FINISHED, {
            "step": step_idx,
            "tool": step["tool"],
            "success": "error" not in result_payload,
        })

    final_answer = "\n".join(results)
    eventbus.publish(event_types.AGENT_ANSWER_PRODUCED, {
        "answer": final_answer,
    })

    return final_answer
