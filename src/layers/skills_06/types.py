from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SkillDef:
    """Definition of a registered skill."""

    name: str
    keywords: list[str]
    markdown_content: str = ""


@dataclass
class SkillMatchResult:
    """Result of matching skills against a user message."""

    matched_skills: list[SkillDef] = field(default_factory=list)
    combined_markdown: str = ""
