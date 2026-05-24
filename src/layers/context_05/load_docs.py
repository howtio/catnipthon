from __future__ import annotations

from pathlib import Path


DOCS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "docs"


def load_documents() -> dict[str, str]:
    """Load markdown documents from docs/ directory as {filename: content}."""
    result: dict[str, str] = {}
    if not DOCS_DIR.is_dir():
        return result

    for md_file in sorted(DOCS_DIR.glob("*.md")):
        try:
            content = md_file.read_text(encoding="utf-8")
            result[md_file.name] = content
        except Exception:
            result[md_file.name] = f"[error reading {md_file.name}]"

    return result


def load_single_doc(name: str) -> str:
    """Load a single document from docs/ by name."""
    path = DOCS_DIR / name
    if not path.is_file():
        return f"[document {name} not found]"
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        return f"[error reading {name}: {exc}]"
