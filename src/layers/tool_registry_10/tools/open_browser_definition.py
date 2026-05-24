from __future__ import annotations

from src.layers.tool_registry_10.types import ToolDef


OPEN_BROWSER: ToolDef = ToolDef(
    name="open_browser",
    description="Open a URL in the default browser. HTTP/HTTPS only.",
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
