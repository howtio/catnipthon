from __future__ import annotations

import time

from src.layers.context_05 import ContextLayerApi
from src.layers.eventbus_09 import EventBusApi
from src.layers.eventbus_09.event_types import PROMPT_COMPOSED, RUN_FINISHED, RUN_STARTED
from src.layers.memory_07 import MemoryLayerApi
from src.layers.runner_08 import RunnerLayerApi
from src.layers.skills_06 import SkillsLayerApi
from src.shared import RunTask, create_id, get_logger


class HarnessLayerApi:
    """Orchestrates a single Agent Run: Context → Skills → Memory → Runner."""

    def __init__(
        self,
        context: ContextLayerApi,
        skills: SkillsLayerApi,
        memory: MemoryLayerApi,
        runner: RunnerLayerApi,
        eventbus: EventBusApi,
    ) -> None:
        self._context = context
        self._skills = skills
        self._memory = memory
        self._runner = runner
        self._eventbus = eventbus
        self._log = get_logger("harness")

    async def run(self, task: RunTask) -> RunTask:
        run_id = create_id()
        self._log.info("[%s] Run started for task %s", run_id, task.id)
        task.started_at = time.time()

        await self._eventbus.publish(
            RUN_STARTED, run_id=run_id, task_id=task.id
        )

        # 1. Build context (docs + workspace + system prompt)
        ctx = await self._context.build_context(task)

        # 2. Select and load relevant skills
        skill_bundles = self._skills.select_and_load(task.user_message)
        skills_prompt = self._skills.inject_skills_prompt(skill_bundles)

        # 3. Load memory snapshot
        mem_snapshot = await self._memory.load_snapshot()
        mem_snapshot.startup_checklist = ctx.startup_checklist
        memory_prompt = self._memory.inject_memory_prompt()

        # 4. Compose full prompt
        composed_prompt = (
            f"{ctx.system_prompt}\n\n"
            f"{skills_prompt}\n\n"
            f"{memory_prompt}"
        )
        await self._eventbus.publish(
            PROMPT_COMPOSED,
            run_id=run_id,
            prompt_length=len(composed_prompt),
        )

        # 5. Run through Runner (Phase 2 placeholder)
        runner_result = await self._runner.run(
            system_prompt=composed_prompt,
            user_message=task.user_message,
        )

        # 6. Build final answer
        report_lines = [
            f"=== Final Report (run: {run_id}) ===",
            f"",
            f"Task: {task.user_message}",
            f"Steps used: {runner_result.steps_used}",
            f"Tool calls made: {runner_result.tool_calls_made}",
            f"",
            f"--- Answer ---",
            f"",
            runner_result.answer,
            f"",
            f"--- Context Summary ---",
            f"Docs loaded: {len(ctx.docs_summary)} chars",
            f"Skills matched: {', '.join(b.name for b in skill_bundles) or 'none'}",
            f"Memory entries: {len(mem_snapshot.session_entries)}",
        ]

        task.result = "\n".join(report_lines)
        task.finished_at = time.time()

        # 7. Save memory and add session entry
        self._memory.add_session_entry(
            f"task {task.id}: {task.user_message[:80]}"
        )
        await self._memory.save_snapshot()

        await self._eventbus.publish(
            RUN_FINISHED,
            run_id=run_id,
            task_id=task.id,
            steps_used=runner_result.steps_used,
            tool_calls_made=runner_result.tool_calls_made,
        )

        self._log.info("[%s] Run finished", run_id)
        return task
