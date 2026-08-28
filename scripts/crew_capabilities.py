"""OpenWork-shaped capability MCP. Study the idea. Do not vendor ee/.

search_capabilities lists granted names only (ids, no prompts).
execute_capability runs one granted name through Cortex wrap.
Den-like policy: ungranted / Deep Agents builtin / billing-bypass /
skill_body refuse. Leave-machine names need OpenVault allow.

Not a second dag_runner. Not OpenWork's desktop.
"""

from __future__ import annotations

from typing import Any

from crew_ov_gate import has_bodies
from crew_tool_wrap import CortexDenied, CortexGate, DEEPAGENTS_DIRECT, run_tool
from seat_router import BYPASS_SEATS

LEAVE_CAPS = frozenset(
    {"open_url", "launch_app", "browser_navigate", "ocr_cloud", "leave"}
)


def search_capabilities(granted: frozenset[str] | list[str] | tuple[str, ...]) -> list[str]:
    """Ids the session may call. Builtins and billing-bypass never list."""
    names: list[str] = []
    for raw in granted or []:
        name = (raw or "").strip()
        if not name:
            continue
        if name in DEEPAGENTS_DIRECT or name in BYPASS_SEATS:
            continue
        names.append(name)
    return sorted(set(names))


def execute_capability(
    gate: CortexGate,
    name: str,
    payload: dict[str, Any],
    *,
    granted: frozenset[str] | list[str] | tuple[str, ...],
    ov_allowed: bool = False,
) -> Any:
    """One granted capability through Cortex. Ungranted does not execute."""
    cap = (name or "").strip()
    if not cap:
        raise CortexDenied("empty capability")
    if cap in DEEPAGENTS_DIRECT:
        raise CortexDenied(f"Deep Agents builtin {cap} is not a Crew tool")
    if cap in BYPASS_SEATS:
        raise CortexDenied("billing-bypass product")
    allowed = search_capabilities(granted)
    if cap not in allowed:
        raise CortexDenied(f"capability {cap} not granted")
    if has_bodies(payload or {}):
        raise CortexDenied("skill_body must never go to a child job")
    if cap in LEAVE_CAPS and not ov_allowed:
        raise CortexDenied("leave-machine is OpenVault")
    return run_tool(gate, cap, payload)
