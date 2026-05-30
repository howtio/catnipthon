from __future__ import annotations

from src.layers.skills_06 import SkillsLayerApi


def test_skills_match_coding_keyword() -> None:
    skills = SkillsLayerApi()
    result = skills.get_skills("implement a new function")
    assert len(result.matched_skills) > 0
    names = [s.name for s in result.matched_skills]
    assert "coding" in names


def test_skills_match_testing() -> None:
    skills = SkillsLayerApi()
    result = skills.get_skills("write a pytest test case")
    assert len(result.matched_skills) > 0
    names = [s.name for s in result.matched_skills]
    assert "testing" in names


def test_skills_fallback_to_coding() -> None:
    skills = SkillsLayerApi()
    result = skills.get_skills("hello world")
    assert len(result.matched_skills) > 0
    assert result.matched_skills[0].name == "coding"


def test_skills_inject_into_prompt() -> None:
    skills = SkillsLayerApi()
    result = skills.get_skills("fix this bug")
    assert len(result.matched_skills) > 0
    names = [s.name for s in result.matched_skills]
    assert "debugging" in names


def test_skills_load_markdown() -> None:
    skills = SkillsLayerApi()
    result = skills.get_skills("implement a feature")
    assert len(result.combined_markdown) > 0
    assert "Coding Skill" in result.combined_markdown
