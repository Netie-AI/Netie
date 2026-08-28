"""Locate this repo's scripts/ for sibling checkout or editable install."""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def scripts_dir() -> Path:
    """Repo-root scripts/. Editable uv install keeps this layout."""
    sibling = _HERE.parent / "scripts"
    if (sibling / "crew_deepagents.py").is_file():
        return sibling
    raise ImportError(
        "Netie contracts need the repo scripts/ tree. "
        "uv add --editable git+https://github.com/Netie-AI/Netie.git"
    )


ROOT = _HERE.parent
SCRIPTS = scripts_dir()
_SCRIPTS = str(SCRIPTS)
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)
