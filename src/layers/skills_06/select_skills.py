from __future__ import annotations

from src.layers.skills_06.types import SkillDef, SkillMatchResult
from src.layers.skills_06.skill_registry import build_default_registry
from src.layers.skills_06.skill_matcher import match_skills
from src.layers.skills_06.load_skill_markdown import load_skill_markdown


def select_skills(user_message: str) -> SkillMatchResult:
    """Select and load skills matching a user message."""
    registry = build_default_registry()
    matched = match_skills(user_message, registry)

    if not matched:
        # Fallback: use coding skill
        coding = registry[0]
        coding.markdown_content = load_skill_markdown(coding.name)
        return SkillMatchResult(matched_skills=[coding], combined_markdown=coding.markdown_content)

    combined: list[str] = []
    for skill in matched:
        skill.markdown_content = load_skill_markdown(skill.name)
        combined.append(skill.markdown_content)

    return SkillMatchResult(
        matched_skills=matched,
        combined_markdown="\n\n---\n\n".join(combined),
    )
