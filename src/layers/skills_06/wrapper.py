from __future__ import annotations

from src.layers.skills_06.types import SkillMatchResult
from src.layers.skills_06.select_skills import select_skills
from src.layers.skills_06.inject_skills import inject_skills_into_prompt


class SkillsLayerApi:
    """06-skills public API: match and inject skills based on user message."""

    def get_skills(self, user_message: str) -> SkillMatchResult:
        """Select skills matching the user message."""
        return select_skills(user_message)

    def inject(self, system_prompt: str, skill_result: SkillMatchResult) -> str:
        """Inject skill markdown into the system prompt."""
        return inject_skills_into_prompt(system_prompt, skill_result)
