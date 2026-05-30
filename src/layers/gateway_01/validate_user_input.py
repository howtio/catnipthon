from __future__ import annotations

from src.shared.errors import GatewayError


def validate_user_input(user_message: str) -> str:
    """Validate user input: must be non-empty after stripping."""
    stripped = user_message.strip()
    if not stripped:
        raise GatewayError("User message cannot be empty")
    return stripped
