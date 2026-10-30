"""Bind a Constructor piece label to a Cortex allowlisted write.

Activepieces/Activeflow catalogs stay out of this tree. Unknown piece = refuse.
Bind a label to Cortex `WRITE_ACTIONS`. Unknown piece refuses.
"""

from __future__ import annotations

from cortex_path import WRITE_ACTIONS


class PieceDenied(ValueError):
    """Unlabeled or unregistered Constructor piece. Do not invent export_pptx."""


def bind_action(label: str | None) -> str:
    name = (label or "").strip()
    if not name:
        raise PieceDenied("unlabeled action")
    if name not in WRITE_ACTIONS:
        raise PieceDenied(f"unknown piece {name}")
    return name
