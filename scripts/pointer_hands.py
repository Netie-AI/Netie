"""UACC hands behind Cortex. Pointer is not a second brain.

Names from `uacc` 1.1.0 on PyPI (MIT, 68 MCP tools). We do not vendor or
import that package. Cortex must allow each name. Planner / workflow /
memory / clipboard / ungoverned JS / ungated leave-machine refuse.
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
SECRET_HANDS = frozenset({"clipboard_read", "clipboard_write"})
SCRIPT_HANDS = frozenset({"browser_execute_js"})
LEAVE_HANDS = frozenset({"open_url", "launch_app", "browser_navigate"})
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
    if tool in LEAVE_HANDS and not ov_leave:
        raise PointerDenied("leave-machine is OpenVault")
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
    return {
        "hand": tool,
        "intent": cortex_intent.strip(),
        "status": "allowed",
    }
