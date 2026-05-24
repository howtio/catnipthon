from __future__ import annotations

from src.layers.tool_registry_10.types import ToolDef


WEB_FETCH: ToolDef = ToolDef(
    name="web_fetch",
    description="Fetch a URL and return its text content (HTML stripped). Max 10KB.",
    category="web",
    permission="medium",
    parameters={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "HTTP/HTTPS URL to fetch",
            },
        },
        "required": ["url"],
    },
)
