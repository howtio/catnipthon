"""Real implementations of the 6 MVP tools."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def list_files(path: str = ".") -> str:
    """List files and directories in a given path."""
    target = WORKSPACE_ROOT / path
    if not target.is_dir():
        return f"Error: not a directory: {path}"

    lines: list[str] = []
    try:
        for entry in sorted(target.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            suffix = "/" if entry.is_dir() else ""
            lines.append(f"{entry.name}{suffix}")
        return "\n".join(lines) if lines else "(empty directory)"
    except PermissionError:
        return f"Error: permission denied: {path}"
    except OSError as e:
        return f"Error: {e}"


def read_file(file_path: str) -> str:
    """Read the contents of a file."""
    target = Path(file_path)
    if not target.is_file():
        return f"Error: file not found: {file_path}"
    try:
        content = target.read_text(encoding="utf-8")
        return content
    except UnicodeDecodeError:
        return f"Error: binary file or non-UTF-8 encoding: {file_path}"
    except PermissionError:
        return f"Error: permission denied: {file_path}"
    except OSError as e:
        return f"Error: {e}"


def write_file(file_path: str, content: str) -> str:
    """Write content to a file. Creates parent dirs if needed."""
    target = Path(file_path)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Written {len(content)} bytes to {file_path}"
    except PermissionError:
        return f"Error: permission denied: {file_path}"
    except OSError as e:
        return f"Error: {e}"


def patch_file(file_path: str, old_string: str, new_string: str) -> str:
    """Apply a string replacement in a file."""
    target = Path(file_path)
    if not target.is_file():
        return f"Error: file not found: {file_path}"

    try:
        content = target.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError, OSError) as e:
        return f"Error: {e}"

    if old_string not in content:
        return f"Error: old_string not found in {file_path}"

    count = content.count(old_string)
    new_content = content.replace(old_string, new_string)
    target.write_text(new_content, encoding="utf-8")

    return f"Patched {count} occurrence(s) in {file_path}"


def shell_exec(command: str, timeout_ms: int = 30000) -> str:
    """Execute a shell command and return stdout/stderr."""
    timeout_s = timeout_ms / 1000.0
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        output_parts: list[str] = []
        if result.stdout:
            output_parts.append(result.stdout.rstrip())
        if result.stderr:
            output_parts.append(f"[stderr]\n{result.stderr.rstrip()}")
        output = "\n".join(output_parts) if output_parts else "(no output)"

        if result.returncode != 0:
            output += f"\n[exit code: {result.returncode}]"

        return output
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {timeout_ms}ms"
    except FileNotFoundError:
        return "Error: shell not available on this system"
    except OSError as e:
        return f"Error: {e}"


def git_diff() -> str:
    """Show unstaged git diff."""
    try:
        result = subprocess.run(
            ["git", "diff"],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.stdout:
            return result.stdout
        # Check for staged changes too
        staged = subprocess.run(
            ["git", "diff", "--cached"],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if staged.stdout:
            return f"(staged changes)\n{staged.stdout}"
        return "(no changes)"
    except subprocess.TimeoutExpired:
        return "Error: git diff timed out"
    except FileNotFoundError:
        return "Error: git not available"
    except OSError as e:
        return f"Error: {e}"
