"""Locate contract modules: editable sibling scripts/ or wheel netie/_contracts."""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def scripts_dir() -> Path:
    """Repo-root scripts/ on an editable checkout, else the bundled wheel copy."""
    sibling = _HERE.parent / "scripts"
    if (sibling / "crew_deepagents.py").is_file():
        return sibling
    bundled = _HERE / "_contracts"
    if (bundled / "crew_deepagents.py").is_file():
        return bundled
    raise ImportError(
        "Netie contracts missing. uv add git+https://github.com/Netie-AI/Netie.git"
    )


ROOT = _HERE.parent
SCRIPTS = scripts_dir()
_SCRIPTS = str(SCRIPTS)
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)
