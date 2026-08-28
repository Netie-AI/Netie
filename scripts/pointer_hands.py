"""UACC hands behind Cortex. Pointer is not a second brain.

Names from `uacc` 1.1.0 on PyPI (MIT, 68 MCP tools). We do not vendor or
import that package. Cortex must allow each name. Planner / workflow /
memory / history / clipboard / ungoverned JS / ungated leave-machine /
uncropped screenshot / page dump / process list / env dump refuse.
Paint overlay and hover/drag on a secret field refuse. UACC kill-distance
and user-override stay out (Cortex is the gate).
"""

from __future__ import annotations

from typing import Any

from pointer_click import PointerDenied, _is_secret, click

# Screen 10 + mouse 9 + window 9 + browser 7 + diff 8 + memory 7 + system 6
# + workflow 10 + safety 2 = 68.
UACC_HANDS: tuple[str, ...] = (
    "get_screen_info",
    "get_screen_info_enhanced",
    "screenshot",
    "list_monitors",
    "find_element",
    "uacc_where_is",
    "find_element_relative",
    "find_element_near",
    "get_mouse_position",
    "wait_for_element",
    "smart_click",
    "smart_type",
    "click",
    "click_element",
    "type_text",
    "hotkey",
    "scroll",
    "drag",
    "hover",
    "get_active_window",
    "list_windows",
    "focus_window",
    "resize_window",
    "move_window",
    "minimize_maximize",
    "launch_app",
    "open_url",
    "execute_actions",
    "browser_query",
    "browser_click",
    "browser_type",
    "browser_navigate",
    "browser_get_page_info",
    "browser_execute_js",
    "browser_wait_for",
    "take_snapshot",
    "compare_snapshots",
    "get_screen_diff",
    "verify_action",
    "vlm_analyze",
    "vlm_locate_element",
    "detect_elements_visual",
    "get_action_history",
    "remember_action",
    "query_knowledge",
    "recall_related_apps",
    "memory_summary",
    "app_action_history",
    "uacc_query",
    "uacc_expect",
    "get_system_info",
    "list_processes",
    "clipboard_read",
    "clipboard_write",
    "paint_preset",
    "paint_image",
    "uacc_planner",
    "create_workflow",
    "list_workflows",
    "get_workflow",
    "delete_workflow",
    "run_workflow",
    "start_task",
    "get_task_status",
    "cancel_task",
    "list_tasks",
    "acknowledge_user_override",
    "set_kill_distance",
)

UACC_HANDS_SET = frozenset(UACC_HANDS)

CLICK_HANDS = frozenset({"click", "click_element", "smart_click", "browser_click"})
TYPE_HANDS = frozenset({"type_text", "smart_type", "browser_type"})
KEY_HANDS = frozenset({"hotkey"})
SECRET_HANDS = frozenset({"clipboard_read", "clipboard_write"})
SCRIPT_HANDS = frozenset({"browser_execute_js"})
LEAVE_HANDS = frozenset({"open_url", "launch_app", "browser_navigate"})
# Full-frame pixels (password fields, OTP, cookies). Crop must be a labeled non-secret.
SCREEN_HANDS = frozenset(
    {
        "screenshot",
        "take_snapshot",
        "compare_snapshots",
        "get_screen_diff",
        "detect_elements_visual",
        "get_screen_info_enhanced",
        "vlm_locate_element",
    }
)
# Hover/drag/wait reuse fail-closed click (secret field refuses).
MOTION_HANDS = frozenset({"hover", "drag", "wait_for_element"})
# Full DOM dump includes password values. Not a Pointer hand.
PAGE_HANDS = frozenset({"browser_get_page_info"})
# Process table / env dump is surveillance.
PROCESS_HANDS = frozenset({"list_processes", "get_system_info"})
# Overlay on a password/OTP field (or the whole screen) is capture.
PAINT_HANDS = frozenset({"paint_image", "paint_preset"})
# UACC's own safety plane is a second policy. Cortex is the gate.
OVERRIDE_HANDS = frozenset({"acknowledge_user_override", "set_kill_distance"})
BRAIN_HANDS = frozenset(
    {
        "uacc_planner",
        "create_workflow",
        "list_workflows",
        "get_workflow",
        "delete_workflow",
        "run_workflow",
        "start_task",
        "get_task_status",
        "cancel_task",
        "list_tasks",
        "remember_action",
        "get_action_history",
        "query_knowledge",
        "recall_related_apps",
        "memory_summary",
        "app_action_history",
        "uacc_query",
        "uacc_expect",
        "vlm_analyze",
        "execute_actions",
    }
)


def invoke_hand(
    name: str,
    *,
    cortex_allowed: bool,
    cortex_intent: str | None,
    element: dict[str, Any] | None = None,
    ov_leave: bool = False,
) -> dict[str, Any]:
    """MCP-wrap one UACC name. Cortex allow is required. No UACC import."""
    tool = (name or "").strip()
    if tool not in UACC_HANDS_SET:
        raise PointerDenied(f"unknown hand {tool or 'none'}")
    if not cortex_allowed:
        raise PointerDenied("no Cortex allow")
    if not (cortex_intent or "").strip():
        raise PointerDenied("no Cortex intent")
    if tool in SECRET_HANDS:
        raise PointerDenied("no clipboard")
    if tool in SCRIPT_HANDS:
        raise PointerDenied("no ungoverned script")
    if tool in BRAIN_HANDS:
        raise PointerDenied("uacc brain stays out; Pointer is hands")
    if tool in OVERRIDE_HANDS:
        raise PointerDenied("uacc override stays out; Cortex is the gate")
    if tool in PROCESS_HANDS:
        if tool == "get_system_info":
            raise PointerDenied("env_dump_refused")
        raise PointerDenied("process_list_refused")
    if tool in PAGE_HANDS:
        raise PointerDenied("no page dump")
    if tool in LEAVE_HANDS and not ov_leave:
        raise PointerDenied("leave-machine is OpenVault")
    if tool in PAINT_HANDS:
        if not isinstance(element, dict):
            raise PointerDenied("paint_uncropped")
        clicked = click(element, cortex_intent=cortex_intent)
        return {"hand": tool, "crop": True, **clicked}
    if tool in MOTION_HANDS:
        if not isinstance(element, dict):
            raise PointerDenied("no target")
        clicked = click(element, cortex_intent=cortex_intent)
        return {"hand": tool, **clicked}
    if tool in SCREEN_HANDS:
        if not isinstance(element, dict):
            raise PointerDenied("screenshot_uncropped")
        clicked = click(element, cortex_intent=cortex_intent)
        return {"hand": tool, "crop": True, **clicked}
    if tool in CLICK_HANDS:
        if not isinstance(element, dict):
            raise PointerDenied("no target")
        clicked = click(element, cortex_intent=cortex_intent)
        return {"hand": tool, **clicked}
    if tool in TYPE_HANDS:
        if not isinstance(element, dict):
            raise PointerDenied("no target")
        if _is_secret(element):
            raise PointerDenied("no secret field")
        clicked = click(element, cortex_intent=cortex_intent)
        return {"hand": tool, **clicked}
    if tool in KEY_HANDS and isinstance(element, dict) and _is_secret(element):
        raise PointerDenied("no secret field")
    if tool == "scroll" and isinstance(element, dict) and _is_secret(element):
        raise PointerDenied("no secret field")
    return {
        "hand": tool,
        "intent": cortex_intent.strip(),
        "status": "allowed",
    }


HOSTED_COMPUTERS = frozenset(
    {
        "e2b",
        "open-computer-use",
        "open_computer_use",
        "perplexity-computer",
        "perplexity_computer",
        "hosted-desktop",
        "hosted_desktop",
    }
)


def bind_computer(vendor: str) -> dict[str, str]:
    """Pointer is a local tray. Not Perplexity Computer, not e2b."""
    name = (vendor or "").strip().lower().replace(" ", "-")
    canon = name.replace("_", "-")
    if "e2b" in canon or "perplexity" in canon or canon in HOSTED_COMPUTERS:
        raise PointerDenied("Pointer is a local tray, not a hosted computer")
    if canon in {"uacc", "pointer"}:
        return {"vendor": canon, "where": "local"}
    raise PointerDenied(f"unknown computer {vendor or 'none'}")
