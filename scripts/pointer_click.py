"""Pointer fail-closed click. Unlabeled UI does not get a click.

Not UACC, not Perplexity Computer, not a Cursor billing bypass.
Cortex supplies the intent. This module only refuses ambiguous targets.
Does not read a local env file or hold keys.
"""

from __future__ import annotations

from typing import Any


class PointerDenied(PermissionError):
    """No click. Ambiguous or ungated."""


def _name(element: dict[str, Any]) -> str:
    for key in ("name", "label", "aria_label", "accessible_name"):
        val = element.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def may_click(element: dict[str, Any]) -> bool:
    if not _name(element):
        return False
    role = str(element.get("role") or "").strip().lower()
    if role in {"", "unknown"}:
        return False
    return True


def click(element: dict[str, Any], *, cortex_intent: str | None) -> dict[str, str]:
    if not (cortex_intent or "").strip():
        raise PointerDenied("no Cortex intent")
    if not may_click(element):
        raise PointerDenied("unlabeled")
    return {"clicked": _name(element), "intent": cortex_intent.strip()}
