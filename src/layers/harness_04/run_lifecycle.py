from __future__ import annotations

import time

from src.shared.types import RunTask
from src.layers.eventbus_09 import EventBusLayerApi, event_types
from src.layers.context_05 import ContextLayerApi
from src.layers.skills_06 import SkillsLayerApi
from src.layers.memory_07 import MemoryLayerApi
from src.layers.harness_04.types import RunInfo, FinalReport
from src.layers.harness_04.create_run import create_run
from src.layers.harness_04.build_final_report import build_final_report, format_final_report


def run_lifecycle(
    task: RunTask,
    eventbus: EventBusLayerApi,
    context: ContextLayerApi,
    skills: SkillsLayerApi,
    memory: MemoryLayerApi,
) -> str:
    """Run the full lifecycle: Context → Skills → Memory → Runner (placeholder)."""
    run = create_run(task.user_message)
    start = time.time()

    eventbus.publish(event_types.RUN_STARTED, {"run_id": run.run_id, "user_message": task.user_message})

    # Phase 2: Context → Skills → Memory → mock result
    ctx = context.get_context()
    eventbus.publish(event_types.PROMPT_COMPOSED, {"system_prompt_length": len(ctx.system_prompt)})

    skill_result = skills.get_skills(task.user_message)
    enhanced_prompt = skills.inject(ctx.system_prompt, skill_result)

    memory.add_session_entry(f"Task: {task.user_message}")
    memory_block = memory.build_memory_block()
    full_prompt = f"{enhanced_prompt}\n\n{memory_block}"

    eventbus.publish(event_types.PROMPT_COMPOSED, {"full_prompt_length": len(full_prompt)})

    # Runner placeholder: mock answer
    mock_answer = (
        f"[Phase 2 mock] Task '{task.user_message}' processed.\n"
        f"Context loaded: {len(ctx.documents)} docs, workspace scanned.\n"
        f"Skills activated: {', '.join(s.name for s in skill_result.matched_skills)}.\n"
        f"Memory: {len(memory_block)} chars."
    )

    run.status = "completed"
    run.final_answer = mock_answer
    run.steps_used = 1
    run.duration_ms = (time.time() - start) * 1000

    eventbus.publish(event_types.RUN_FINISHED, {"run_id": run.run_id, "steps": run.steps_used})

    report = build_final_report(run)
    return format_final_report(report)
