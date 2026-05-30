from __future__ import annotations


class CommandForbidden(Exception):
    """Raised when a shell command is blocked by the command guard."""


# Destructive patterns — these are always blocked
DESTRUCTIVE_PATTERNS = [
    "rm -rf /", "rm -rf ~", "rm -rf .", "rm -rf *",
    "mkfs", "dd ",
    ":(){ :|:& };:",  # fork bomb
    "> /dev/sda", "> /dev/sd",
    "shutdown", "reboot", "halt",
]


def check_command(command: str) -> str:
    """Validate a shell command. Blocks destructive patterns, allows everything else."""
    stripped = command.strip()

    if not stripped:
        raise CommandForbidden("Empty command")

    # Block destructive patterns
    for pattern in DESTRUCTIVE_PATTERNS:
        if pattern in stripped:
            raise CommandForbidden(
                f"Command blocked (matches destructive pattern '{pattern}'): {stripped[:100]}"
            )

    return stripped
