from __future__ import annotations

from src.layers.tool_registry_10.types import ToolDef


OPEN_BROWSER: ToolDef = ToolDef(
    name="open_browser",
    description="Open a URL or local file in the default browser. Supports http/https and local file paths.",
    category="web",
    permission="medium",
    parameters={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "HTTP/HTTPS URL to open",
            },
        },
        "required": ["url"],
    },
)
