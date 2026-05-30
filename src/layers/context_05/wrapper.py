from __future__ import annotations

from src.layers.context_05.types import ContextResult
from src.layers.context_05.build_context import build_context


class ContextLayerApi:
    """05-context public API: assemble documents, workspace, and system prompt."""

    def get_context(self) -> ContextResult:
        """Build and return the full context for a run."""
        return build_context()
