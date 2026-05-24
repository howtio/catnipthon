from __future__ import annotations

from src.layers.skills_06.types import SkillDef


def match_skills(user_message: str, registry: list[SkillDef]) -> list[SkillDef]:
    """Match a user message against registered skills by keyword."""
    msg_lower = user_message.lower()
    matched: list[SkillDef] = []

    for skill in registry:
        for kw in skill.keywords:
            if kw in msg_lower:
                matched.append(skill)
                break

    return matched
