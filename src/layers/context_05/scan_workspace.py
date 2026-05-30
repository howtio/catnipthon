from __future__ import annotations

from pathlib import Path


WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent.parent
SKIP_DIRS = {
    ".venv", "__pycache__", ".git", ".mypy_cache", ".pytest_cache",
    ".local-secrets", "node_modules", "logs", "sessions",
}


def scan_workspace(root: Path | None = None) -> str:
    """Scan workspace and return a tree-like string representation."""
    root = root or WORKSPACE_DIR
    lines: list[str] = []

    def _walk(dir_path: Path, prefix: str = "") -> None:
        entries = sorted(
            [e for e in dir_path.iterdir() if e.name not in SKIP_DIRS],
            key=lambda x: (not x.is_dir(), x.name.lower()),
        )
        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{entry.name}")
            if entry.is_dir():
                extension = "    " if is_last else "│   "
                _walk(entry, prefix + extension)

    _walk(root)
    return "\n".join(lines)
