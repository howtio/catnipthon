from __future__ import annotations

from src.layers.skills_06 import SkillsLayerApi


def test_skills_are_loaded_on_init() -> None:
    skills = SkillsLayerApi()
    bundles = skills.select_and_load("default")
    assert len(bundles) > 0


def test_coding_keyword_matches() -> None:
    skills = SkillsLayerApi()
    bundles = skills.select_and_load("implement a new feature")
    names = {b.name for b in bundles}
    assert "coding" in names


def test_testing_keyword_matches() -> None:
    skills = SkillsLayerApi()
    bundles = skills.select_and_load("write pytest tests")
    names = {b.name for b in bundles}
    assert "testing" in names


def test_debugging_keyword_matches() -> None:
    skills = SkillsLayerApi()
    bundles = skills.select_and_load("fix the bug in auth")
    names = {b.name for b in bundles}
    assert "debugging" in names


def test_refactor_keyword_matches() -> None:
    skills = SkillsLayerApi()
    bundles = skills.select_and_load("refactor the database layer")
    names = {b.name for b in bundles}
    assert "refactor" in names


def test_review_keyword_matches() -> None:
    skills = SkillsLayerApi()
    bundles = skills.select_and_load("review the pull request")
    names = {b.name for b in bundles}
    assert "review" in names


def test_defaults_to_coding_when_no_match() -> None:
    skills = SkillsLayerApi()
    bundles = skills.select_and_load("xyzzy foobar blarg")
    names = {b.name for b in bundles}
    assert names == {"coding"}


def test_inject_skills_prompt_formats_correctly() -> None:
    skills = SkillsLayerApi()
    bundles = skills.select_and_load("write code")
    prompt = skills.inject_skills_prompt(bundles)
    assert "## Available Skills" in prompt
    assert "Skill: coding" in prompt
