"""Single source of truth for catnip-agent version.

Reads from pyproject.toml at module load time.
All other modules import from here — never hardcode version strings.
"""

from __future__ import annotations

from pathlib import Path

try:
    _pyproject = Path(__file__).resolve().parent.parent.parent / "pyproject.toml"
    _text = _pyproject.read_text(encoding="utf-8")
    for _line in _text.splitlines():
        _stripped = _line.strip()
        if _stripped.startswith("version"):
            VERSION = _stripped.split("=")[1].strip().strip('"')
            break
    else:
        VERSION = "0.unknown"
except Exception:
    VERSION = "0.unknown"

VERSION_TAG = f"v{VERSION}"
