from __future__ import annotations

from src.layers.skills_06.types import SkillDef


def build_default_registry() -> list[SkillDef]:
    """Build the default skill registry with tagline keywords."""
    return [
        SkillDef(
            name="coding",
            keywords=["implement", "create", "add", "write", "code", "modify", "function", "new file", "patch"],
        ),
        SkillDef(
            name="testing",
            keywords=["test", "pytest", "unittest", "coverage", "test case", "assert"],
        ),
        SkillDef(
            name="debugging",
            keywords=["debug", "bug", "fix", "error", "crash", "traceback", "issue", "not working", "broken"],
        ),
        SkillDef(
            name="refactor",
            keywords=["refactor", "restructure", "clean up", "reorganize", "improve", "extract", "rename"],
        ),
        SkillDef(
            name="review",
            keywords=["review", "audit", "inspect", "check", "validate", "verify"],
        ),
    ]
