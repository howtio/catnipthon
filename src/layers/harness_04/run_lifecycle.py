from __future__ import annotations

import time
from collections import Counter
from typing import Any

from src.shared.types import RunTask
from src.layers.eventbus_09 import EventBusLayerApi, event_types
from src.layers.context_05 import ContextLayerApi
from src.layers.skills_06 import SkillsLayerApi
from src.layers.memory_07 import MemoryLayerApi
from src.layers.runner_08 import RunnerLayerApi, RunnerConfig
from src.layers.harness_04.types import RunInfo
from src.layers.harness_04.create_run import create_run
from src.layers.harness_04.build_final_report import build_final_report, format_final_report


def _collect_tool_summary(eventbus: EventBusLayerApi) -> dict[str, int]:
    """Build tool_name → call_count from event history."""
    step_events = eventbus.get_history(event_types.AGENT_STEP_FINISHED)
    counter: Counter[str] = Counter()
    for e in step_events:
        tool = e.payload.get("tool", "")
        if tool:
            counter[tool] += 1
    return dict(counter)


def _collect_modified_files(eventbus: EventBusLayerApi) -> list[str]:
    """Detect files written/patched from tool call args."""
    modified: list[str] = []
    tool_events = eventbus.get_history(event_types.TOOL_CALL_REQUESTED)
    for e in tool_events:
        tool_name = e.payload.get("tool_name", "")
        args = e.payload.get("arguments", {})
        if tool_name in ("write_file", "patch_file"):
            file_path = args.get("file_path", "")
            if file_path:
                modified.append(file_path)
    return modified


def _collect_token_usage(eventbus: EventBusLayerApi) -> dict[str, int]:
    """Sum token usage from LLM_USAGE events."""
    events = eventbus.get_history(event_types.LLM_USAGE)
    return {
        "prompt_tokens": sum(e.payload.get("prompt_tokens", 0) for e in events),
        "completion_tokens": sum(e.payload.get("completion_tokens", 0) for e in events),
        "total_tokens": sum(e.payload.get("total_tokens", 0) for e in events),
    }


def run_lifecycle(
    task: RunTask,
    eventbus: EventBusLayerApi,
    context: ContextLayerApi,
    skills: SkillsLayerApi,
    memory: MemoryLayerApi,
    runner: RunnerLayerApi,
    conversation_history: list[dict[str, Any]] | None = None,
) -> str:
    """Run the full lifecycle: Context → Skills → Memory → Runner.

    If conversation_history is provided, the runner passes it to the model
    so prior turns are visible (multi-turn conversation).
    """
    run = create_run(task.user_message)
    start = time.time()

    eventbus.publish(event_types.RUN_STARTED, {"run_id": run.run_id, "user_message": task.user_message})

    ctx = context.get_context()
    eventbus.publish(event_types.PROMPT_COMPOSED, {"system_prompt_length": len(ctx.system_prompt)})

    skill_result = skills.get_skills(task.user_message)
    enhanced_prompt = skills.inject(ctx.system_prompt, skill_result)

    memory.add_session_entry(f"Task: {task.user_message}")
    memory_block = memory.build_memory_block()

    eventbus.publish(event_types.PROMPT_COMPOSED, {"full_prompt_length": len(enhanced_prompt) + len(memory_block)})

    # Build full prompt with context, skills, and memory
    full_prompt = f"{enhanced_prompt}\n\n{memory_block}" if memory_block else enhanced_prompt

    runner_cfg = RunnerConfig(max_steps=15)

    # Run agent with real Runner
    answer = runner.run(task, runner_cfg, system_prompt=full_prompt,
                        conversation_history=conversation_history)

    # Collect run metrics from event history
    step_events = eventbus.get_history(event_types.AGENT_STEP_FINISHED)
    steps_used = len(step_events) or 1

    run.status = "completed"
    run.final_answer = answer
    run.steps_used = steps_used
    run.duration_ms = (time.time() - start) * 1000
    run.tool_summary = _collect_tool_summary(eventbus)
    run.modified_files = _collect_modified_files(eventbus)
    run.token_usage = _collect_token_usage(eventbus)

    eventbus.publish(event_types.RUN_FINISHED, {
        "run_id": run.run_id,
        "steps": steps_used,
        "tool_summary": run.tool_summary,
        "duration_ms": run.duration_ms,
        "token_usage": run.token_usage,
    })

    report = build_final_report(run)
    return format_final_report(report)
