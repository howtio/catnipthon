from __future__ import annotations


class CommandForbidden(Exception):
    """Raised when a shell command is blocked by the command guard."""


# Commands that are always blocked (dangerous)
BLOCKED_COMMANDS = [
    "rm -rf /", "rm -rf ~", "rm -rf .", "rm -rf *",
    "sudo", "su ",
    "curl", "wget",
    "ssh ", "scp ", "rsync",
    "chmod", "chown",
    "mkfs", "dd ",
    ":(){ :|:& };:",  # fork bomb
    "> /dev/sda", "> /dev/sd",
    "shutdown", "reboot", "halt",
    "passwd",
]

# Whitelist of allowed command prefixes
WHITELIST_PREFIXES = [
    "python", "pytest", "mypy", "pip",
    "git status", "git diff", "git log", "git show", "git branch",
    "git add", "git commit", "git push", "git pull", "git checkout",
    "ls", "cat", "echo", "pwd", "cd", "mkdir", "touch", "cp", "mv",
    "dir", "type", "find", "grep", "rg ", "head", "tail",
    "npm ", "node ", "npx",
    "which", "where",
    ".venv/Scripts/python", ".venv/bin/python",
    "powershell", "start", "cls", "clear",
]


def check_command(command: str) -> str:
    """Validate a shell command against the whitelist and blocklist."""
    stripped = command.strip()

    if not stripped:
        raise CommandForbidden("Empty command")

    # Check blocked commands first
    for blocked in BLOCKED_COMMANDS:
        if blocked in stripped:
            raise CommandForbidden(
                f"Command blocked (matches dangerous pattern '{blocked}'): {stripped}"
            )

    # Check whitelist
    for prefix in WHITELIST_PREFIXES:
        if stripped.startswith(prefix):
            return stripped

    raise CommandForbidden(
        f"Command not in whitelist: {stripped[:100]}"
    )
