from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SkillBundle:
    name: str
    keywords: list[str]
    content: str


_SKILL_KEYWORDS: dict[str, list[str]] = {
    "coding": [
        "create", "implement", "write", "code", "add", "build",
        "make", "feature", "function", "class", "module",
    ],
    "testing": [
        "test", "verify", "check", "assert", "pytest", "coverage",
    ],
    "debugging": [
        "debug", "fix", "bug", "error", "broken", "issue",
        "wrong", "fail", "crash",
    ],
    "refactor": [
        "refactor", "restructure", "rename", "clean", "reorganize",
        "move", "extract", "simplify",
    ],
    "review": [
        "review", "inspect", "audit", "assess", "evaluate",
    ],
}


class SkillsLayerApi:
    """Loads SKILL.md files based on keyword matching against user input."""

    def __init__(self, skills_dir: str = "skills") -> None:
        self._skills_dir = Path(skills_dir)
        self._registry: dict[str, SkillBundle] = {}
        self._load_all()

    def _load_all(self) -> None:
        if not self._skills_dir.exists():
            return
        for skill_dir in self._skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            name = skill_dir.name
            self._registry[name] = SkillBundle(
                name=name,
                keywords=_SKILL_KEYWORDS.get(name, []),
                content=skill_md.read_text(encoding="utf-8"),
            )

    def select_and_load(self, user_message: str) -> list[SkillBundle]:
        msg_lower = user_message.lower()
        selected: list[SkillBundle] = []
        for name, bundle in self._registry.items():
            if any(kw in msg_lower for kw in bundle.keywords):
                selected.append(bundle)
        if not selected:
            # Default: include coding skill when no match
            default = self._registry.get("coding")
            if default:
                selected.append(default)
        return selected

    def inject_skills_prompt(self, bundles: list[SkillBundle]) -> str:
        if not bundles:
            return ""
        parts = ["## Available Skills"]
        for b in bundles:
            parts.append(f"\n### Skill: {b.name}\n{b.content}")
        return "\n".join(parts)
