from __future__ import annotations

from src.layers.skills_06.types import SkillMatchResult


def inject_skills_into_prompt(system_prompt: str, skill_result: SkillMatchResult) -> str:
    """Inject selected skill markdown into the system prompt."""
    if not skill_result.combined_markdown:
        return system_prompt

    injection = f"\n\n## Activated Skills\n\n{skill_result.combined_markdown}\n"
    return system_prompt + injection
