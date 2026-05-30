from __future__ import annotations

from pathlib import Path


SKILLS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "skills"


def load_skill_markdown(skill_name: str) -> str:
    """Load the SKILL.md file for a given skill name."""
    path = SKILLS_DIR / skill_name / "SKILL.md"
    if not path.is_file():
        return f"[SKILL.md for '{skill_name}' not found]"
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        return f"[error loading {skill_name} skill: {exc}]"
