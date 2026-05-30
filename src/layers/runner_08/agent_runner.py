from __future__ import annotations

import json
import os
import uuid
from typing import Any

from src.shared.types import RunTask
from src.layers.eventbus_09 import EventBusLayerApi, event_types
from src.layers.tool_registry_10 import ToolRegistryLayerApi
from src.layers.runner_08.types import RunnerConfig
from src.layers.runner_08.provider import heuristic_plan
from src.layers.runner_08.deepseek_provider import run_deepseek


def run_agent(
    task: RunTask,
    eventbus: EventBusLayerApi,
    registry: ToolRegistryLayerApi,
    system_prompt: str = "",
    config: RunnerConfig | None = None,
    conversation_history: list[dict[str, Any]] | None = None,
) -> str:
    """Run the agent loop. Uses deepseek provider if configured, else heuristic.

    Args:
        conversation_history: accumulated messages from prior turns so the
            model sees the full conversation context.
    """
    cfg = config or RunnerConfig()

    if cfg.provider == "deepseek" and os.environ.get("DEEPSEEK_API_KEY"):
        return run_deepseek(task, eventbus, registry, system_prompt, cfg,
                            conversation_history=conversation_history)

    # Heuristic provider (default)
    plan = heuristic_plan(task)

    if not plan:
        msg = f"[heuristic] No plan generated for: {task.user_message}"
        eventbus.publish(event_types.AGENT_ANSWER_PRODUCED, {"answer": msg})
        return msg

    eventbus.publish(event_types.AGENT_PLAN_GENERATED, {
        "plan": plan,
        "step_count": len(plan),
    })

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
            results.append(f"[{step['tool']}] {output}")

        eventbus.publish(event_types.AGENT_STEP_FINISHED, {
            "step": step_idx,
            "tool": step["tool"],
            "success": "error" not in result_payload,
        })

    final_answer = "\n".join(results)

    eventbus.publish(event_types.AGENT_REASONING_SUMMARY, {
        "steps_completed": len(results),
        "tools_used": list(dict.fromkeys(r.split("]")[0].lstrip("[") if "]" in r else "" for r in results)),
    })

    eventbus.publish(event_types.AGENT_ANSWER_PRODUCED, {
        "answer": final_answer,
    })

    return final_answer
