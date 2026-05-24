from __future__ import annotations

from src.layers.tool_registry_10.types import ToolDef


WEB_SEARCH: ToolDef = ToolDef(
    name="web_search",
    description="Search the web via DuckDuckGo. Returns top result snippets.",
    category="web",
    permission="high",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query",
            },
            "max_results": {
                "type": "integer",
                "description": "Max results (1-10, default: 5)",
                "default": 5,
            },
        },
        "required": ["query"],
    },
)
