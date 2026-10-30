"""How Cortex routes today. JEPA and gen-cFSM are not on this path.

Executable form of TAS-CORTEX / ESTATE-GAP section 0. Not a serving engine.
Invocable writes: export_pptx, item.intake, amend.apply, call_action.
agent.checked is an event.
"""

from __future__ import annotations

COLD_START = ("minimal", "sequential", "dag")
WRITE_ACTIONS = frozenset(
    {"export_pptx", "item.intake", "amend.apply", "call_action"}
)
PARKED = frozenset({"jepa", "gen-cfsm", "osr"})
# Claude Code's job. Cortex is governed Q&A, not a coding agent.
CODING_TOOLS = frozenset(
    {
        "bash",
        "shell",
        "execute",
        "write_file",
        "edit_file",
        "ls",
        "read_file",
        "glob",
        "grep",
        "delete",
    }
)
# Pointer native observe stays DR-0005. Cortex callers go through guard_observe.
OBSERVE_TOOLS = frozenset(
    {
        "computer.observe",
        "observe",
        "screenshot",
        "get_screen_info",
        "get_screen_info_enhanced",
        "uacc_screenshot",
        "uacc_screen_info",
        "uacc_screen_info_enhanced",
    }
)


class RouteDenied(PermissionError):
    """Parked organ or ungoverned write."""


def _observe_or_deny(tool: str, observe: dict | None, *, intent: str) -> None:
    """Cortex must call guard_observe. Product copy may lack pointer_observe."""
    name = (tool or "").strip()
    if name not in OBSERVE_TOOLS:
        return
    payload = observe or {}
    crop = payload.get("crop") if isinstance(payload.get("crop"), dict) else None
    try:
        from pointer_observe import PointerDenied, guard_observe
    except ImportError:
        if payload.get("clipboard"):
            raise RouteDenied("no clipboard")
        if payload.get("windows") or payload.get("foreground"):
            raise RouteDenied("window_dump_refused")
        if payload.get("screenshot") and crop is None:
            raise RouteDenied("screenshot_uncropped")
        return
    try:
        guard_observe(
            cortex_allowed=True,
            cortex_intent=intent,
            screenshot=payload.get("screenshot"),
            clipboard=payload.get("clipboard"),
            windows=payload.get("windows"),
            foreground=payload.get("foreground"),
            crop=crop,
        )
    except PointerDenied as exc:
        raise RouteDenied(str(exc)) from exc


def auto_route(
    *,
    cosine: float,
    winner_runs: int,
    candidates: list[str],
) -> str:
    parked = [c for c in candidates if c.lower() in PARKED]
    if parked:
        raise RouteDenied(f"parked not on path: {parked}")
    live = [c for c in candidates if c.lower() not in PARKED]
    if not live:
        raise RouteDenied("no live candidate")
    if cosine >= 0.80 and winner_runs >= 3:
        return live[0]
    return live[min(2, len(live) - 1)]


def run_question(
    shape: str,
    *,
    write: str | None = None,
    tool: str | None = None,
    via_tool_runner: bool = True,
    actor: str | None = None,
    role: str | None = None,
    verified: bool = False,
    pack: str = "default",
    a2a: bool = False,
    c7_sql: bool = False,
    observe: dict | None = None,
) -> dict[str, str]:
    if shape not in COLD_START:
        raise RouteDenied(f"bad shape {shape}")
    if c7_sql:
        raise RouteDenied("C7 generated-SQL is off (17 confidently wrong)")
    if write and write not in WRITE_ACTIONS:
        raise RouteDenied(f"write not in action registry: {write}")
    if write and not (actor or "").strip():
        raise RouteDenied("write needs an actor; RBAC is missing on execute modules")
    if tool and tool.strip() in CODING_TOOLS:
        raise RouteDenied(
            "Cortex is not Claude Code; depend Deep Agents under tool_runner"
        )
    if (write or tool) and not (role or "").strip():
        raise RouteDenied("execute needs a role")
    if tool and not via_tool_runner:
        raise RouteDenied(f"{tool} skipped tool_runner")
    if tool:
        _observe_or_deny(
            tool,
            observe,
            intent=(actor or role or "observe").strip() or "observe",
        )
    if a2a and (pack or "").strip().lower() != "dms":
        raise RouteDenied("a2a/messages is dms-pack only")
    if not verified:
        raise RouteDenied("answer needs verified; HEAD leaves it optional on /dms/query")
    return {
        "router": "race_router.auto_route",
        "shape": shape,
        "dms": "keyword_cascade",
        "c7_sql": "off",
        "write": write or "none",
        "tool": tool or "none",
        "actor": (actor or "").strip() or "none",
        "role": (role or "").strip() or "none",
        "verified": "true",
        "pack": (pack or "default").strip() or "default",
        "observe": (
            "guard_observe"
            if (tool or "").strip() in OBSERVE_TOOLS
            else "off"
        ),
        "jepa": "off-path",
        "gen_cfsm": "off-path",
    }
