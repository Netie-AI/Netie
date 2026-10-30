"""Pointer fail-closed click. Unlabeled UI does not get a click.

Not UACC, not Perplexity Computer, not a Cursor billing bypass.
Cortex supplies the intent. This module only refuses ambiguous targets.
Does not read a local env file or hold keys. Does not click password,
OTP, or cookie fields even when they are labeled.
"""

from __future__ import annotations

from typing import Any


class PointerDenied(PermissionError):
    """No click. Ambiguous, ungated, or a secret field."""


SECRET_TYPES = frozenset({"password", "hidden"})
SECRET_AUTOCOMPLETE = frozenset(
    {"current-password", "new-password", "one-time-code"}
)
SECRET_NAMES = frozenset(
    {
        "password",
        "passwd",
        "otp",
        "2fa",
        "totp",
        "pin",
        "secret",
        "cookie",
        "api key",
        "api_key",
    }
)


def _name(element: dict[str, Any]) -> str:
    for key in ("name", "label", "aria_label", "accessible_name"):
        val = element.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _is_secret(element: dict[str, Any]) -> bool:
    itype = str(element.get("type") or "").strip().lower()
    if itype in SECRET_TYPES:
        return True
    ac = str(element.get("autocomplete") or "").strip().lower()
    if ac in SECRET_AUTOCOMPLETE:
        return True
    name = _name(element).lower()
    if name in SECRET_NAMES:
        return True
    for needle in ("password", "passwd", "otp", "2fa", "totp", "api key"):
        if needle in name:
            return True
    return False


def may_click(element: dict[str, Any]) -> bool:
    if not _name(element):
        return False
    role = str(element.get("role") or "").strip().lower()
    if role in {"", "unknown"}:
        return False
    if _is_secret(element):
        return False
    return True


def click(element: dict[str, Any], *, cortex_intent: str | None) -> dict[str, str]:
    if not (cortex_intent or "").strip():
        raise PointerDenied("no Cortex intent")
    if _is_secret(element):
        raise PointerDenied("no secret field")
    if not may_click(element):
        raise PointerDenied("unlabeled")
    return {"clicked": _name(element), "intent": cortex_intent.strip()}
