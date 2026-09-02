"""Control is Crew's board view. Read-only cards. No dag_runner, no keys.

Not Guacamole. Not a product. Fold into Crew; do not grow a sibling shell.
"""

from __future__ import annotations

import json
from typing import Any

from crew_capabilities import search_capabilities


FORBIDDEN_KEYS = frozenset({"skill_body", "prompt", "transcript", "api_key", "password"})
MAX_BOARD_CHARS = 12000  # same DitchContext as DMS/AirGPT/Space
# Control is not Apache Guacamole. Those protocols are not board cards.
RDP_KINDS = frozenset(
    {
        "rdp",
        "vnc",
        "guacamole",
        "guacd",
        "remote_desktop",
        "ssh",
        "telnet",
        "kubernetes",
        "k8s",
        "k8s_exec",
    }
)


class ControlDenied(PermissionError):
    """Board stays a view. It does not run the loop."""


def _guard_row(row: dict[str, Any]) -> None:
    if any(k in row for k in FORBIDDEN_KEYS):
        raise ControlDenied("index leaked a body")
    kind = str(row.get("kind") or "").strip().lower()
    if kind in RDP_KINDS:
        raise ControlDenied("Control is not Guacamole")


def _budget_ok(blob: object, *, max_chars: int, what: str) -> None:
    budget = max_chars if max_chars > 0 else MAX_BOARD_CHARS
    dumped = json.dumps(blob, separators=(",", ":"), default=str)
    if len(dumped) > budget:
        raise ControlDenied(f"{what} over DitchContext")
    for needle in FORBIDDEN_KEYS:
        if needle in dumped:
            raise ControlDenied(f"{what} contained {needle}")


def project_board(
    *,
    crew_index: dict[str, Any],
    ledger_peek: list[dict[str, Any]],
    refusals: list[dict[str, Any]],
    max_chars: int = MAX_BOARD_CHARS,
) -> dict[str, Any]:
    cards = []
    for row in crew_index.get("runs") or []:
        if not isinstance(row, dict):
            continue
        _guard_row(row)
        cards.append(
            {
                "id": row.get("id"),
                "status": row.get("status"),
                "ticket_id": row.get("ticket_id"),
                "kind": "run",
            }
        )
    for row in crew_index.get("tickets") or []:
        if not isinstance(row, dict):
            continue
        _guard_row(row)
        cards.append(
            {
                "id": row.get("id"),
                "status": row.get("status"),
                "ticket_id": row.get("id"),
                "epic_id": row.get("epic_id"),
                "kind": "ticket",
            }
        )
    for row in crew_index.get("epics") or []:
        if not isinstance(row, dict):
            continue
        _guard_row(row)
        cards.append(
            {
                "id": row.get("id"),
                "status": row.get("status"),
                "tier": row.get("tier"),
                "kind": "epic",
            }
        )
    for row in ledger_peek:
        if not isinstance(row, dict):
            continue
        _guard_row(row)
        cards.append(
            {"id": row.get("id"), "kind": "ledger", "status": row.get("status")}
        )
    for row in refusals:
        if not isinstance(row, dict):
            continue
        _guard_row(row)
        cards.append(
            {"id": row.get("id"), "kind": "refusal", "reason": row.get("reason")}
        )
    for row in crew_index.get("skills") or []:
        if not isinstance(row, dict):
            continue
        _guard_row(row)
        cards.append(
            {
                "id": row.get("id"),
                "source": row.get("source"),
                "kind": "skill",
            }
        )
    board = {"product": "crew-board", "cards": cards}
    _budget_ok(board, max_chars=max_chars, what="board")
    return board


def project_session(
    *,
    run: dict[str, Any],
    todos: list[dict[str, Any]],
    permissions: list[str],
    handoff: dict[str, Any] | None = None,
    max_chars: int = MAX_BOARD_CHARS,
) -> dict[str, Any]:
    """OpenWork-shaped session: one live run, no transcript body."""
    if not isinstance(run, dict):
        raise ControlDenied("no run")
    rows: list[dict[str, Any]] = [run, *(todos or [])]
    if handoff is not None:
        rows.append(handoff)
    for row in rows:
        if not isinstance(row, dict):
            continue
        _guard_row(row)
    session = {
        "product": "crew-session",
        "run_id": run.get("id"),
        "status": run.get("status"),
        "ticket_id": run.get("ticket_id"),
        "todos": [
            {"id": t.get("id"), "status": t.get("status")}
            for t in todos
            if isinstance(t, dict)
        ],
        "permissions": search_capabilities(permissions),
        "handoff_id": (handoff or {}).get("id"),
    }
    _budget_ok(session, max_chars=max_chars, what="session")
    return session


def run_dag(*_a: Any, **_k: Any) -> None:
    raise ControlDenied("Control has no dag_runner")
