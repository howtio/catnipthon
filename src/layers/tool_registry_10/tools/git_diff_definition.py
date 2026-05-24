from __future__ import annotations

from src.layers.tool_registry_10.types import ToolDef


GIT_DIFF: ToolDef = ToolDef(
    name="git_diff",
    description="Show unstaged git diff. Read-only.",
    category="vcs",
    permission="low",
    parameters={
        "type": "object",
        "properties": {},
    },
)
