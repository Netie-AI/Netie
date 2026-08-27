"""Control is Crew's board view. Read-only cards. No dag_runner, no keys.

Not Guacamole. Not a product. Fold into Crew; do not grow a sibling shell.
"""

from __future__ import annotations

from typing import Any

FORBIDDEN_KEYS = frozenset({"skill_body", "prompt", "transcript", "api_key", "password"})


class ControlDenied(PermissionError):
    """Board stays a view. It does not run the loop."""


def project_board(
    *,
    crew_index: dict[str, Any],
    ledger_peek: list[dict[str, Any]],
    refusals: list[dict[str, Any]],
) -> dict[str, Any]:
    cards = []
    for row in crew_index.get("runs") or []:
        if not isinstance(row, dict):
            continue
        if any(k in row for k in FORBIDDEN_KEYS):
            raise ControlDenied("index leaked a body")
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
        if any(k in row for k in FORBIDDEN_KEYS):
            raise ControlDenied("index leaked a body")
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
        if any(k in row for k in FORBIDDEN_KEYS):
            raise ControlDenied("index leaked a body")
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
        if any(k in row for k in FORBIDDEN_KEYS):
            raise ControlDenied("index leaked a body")
        cards.append(
            {"id": row.get("id"), "kind": "ledger", "status": row.get("status")}
        )
    for row in refusals:
        if not isinstance(row, dict):
            continue
        if any(k in row for k in FORBIDDEN_KEYS):
            raise ControlDenied("index leaked a body")
        cards.append(
            {"id": row.get("id"), "kind": "refusal", "reason": row.get("reason")}
        )
    dumped = str(cards)
    for needle in FORBIDDEN_KEYS:
        if needle in dumped:
            raise ControlDenied(f"board contained {needle}")
    return {"product": "crew-board", "cards": cards}


def project_session(
    *,
    run: dict[str, Any],
    todos: list[dict[str, Any]],
    permissions: list[str],
    handoff: dict[str, Any] | None = None,
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
        if any(k in row for k in FORBIDDEN_KEYS):
            raise ControlDenied("session leaked a body")
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
        "permissions": [p for p in permissions if str(p).strip()],
        "handoff_id": (handoff or {}).get("id"),
    }
    dumped = str(session)
    for needle in FORBIDDEN_KEYS:
        if needle in dumped:
            raise ControlDenied(f"session contained {needle}")
    return session


def run_dag(*_a: Any, **_k: Any) -> None:
    raise ControlDenied("Control has no dag_runner")
