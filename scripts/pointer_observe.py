"""Governed computer.observe. Native Pointer observe stays DR-0005.

Default Pointer `computer.observe` still publishes uncropped PNG, clipboard,
and window titles. Cortex callers opt in with governed=True. Uncropped
screenshot, clipboard, and window dump refuse. A labeled non-secret crop
may confirm a screenshot without returning pixels.
"""

from __future__ import annotations

from typing import Any

from pointer_click import PointerDenied, click


def guard_observe(
    *,
    cortex_allowed: bool,
    cortex_intent: str | None,
    screenshot: Any = None,
    clipboard: Any = None,
    windows: Any = None,
    foreground: Any = None,
    crop: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Opt-in Cortex path. Does not rewrite native observe."""
    if not cortex_allowed:
        raise PointerDenied("no Cortex allow")
    if not (cortex_intent or "").strip():
        raise PointerDenied("no Cortex intent")
    if _clipboard_present(clipboard):
        raise PointerDenied("no clipboard")
    if _window_dump(windows, foreground):
        raise PointerDenied("window_dump_refused")
    if _screenshot_present(screenshot):
        if not isinstance(crop, dict):
            raise PointerDenied("screenshot_uncropped")
        clicked = click(crop, cortex_intent=cortex_intent)
        return {
            "ok": True,
            "governed": True,
            "crop": True,
            "clicked": clicked["clicked"],
            "screenshot": {"present": True, "cropped": True},
            "clipboard": None,
            "windows": [],
            "foreground": None,
        }
    return {
        "ok": True,
        "governed": True,
        "screenshot": None,
        "clipboard": None,
        "windows": [],
        "foreground": None,
    }


def _screenshot_present(screenshot: Any) -> bool:
    if screenshot in (None, False, ""):
        return False
    if isinstance(screenshot, dict):
        return bool(screenshot.get("dataUrl") or screenshot.get("present"))
    return True


def _clipboard_present(clipboard: Any) -> bool:
    if clipboard in (None, False, ""):
        return False
    if isinstance(clipboard, dict):
        return bool(clipboard.get("text") or clipboard.get("present"))
    return True


def _window_dump(windows: Any, foreground: Any) -> bool:
    if isinstance(foreground, dict) and foreground:
        return True
    if isinstance(windows, list) and windows:
        return True
    return False
