"""Ticket runner. Cortex refusal stays on the board. Ticket stays open.

PRD-002: WHEN the runner calls a tool Cortex would refuse, THE SYSTEM SHALL
show the refusal on the board and leave the ticket open. The embedded prompt
never goes to a child job.
"""

from __future__ import annotations

from typing import Any

from control_board import project_board
from crew_factory import Factory, FactoryDenied
from crew_ov_gate import has_bodies
from crew_tool_wrap import CortexDenied, CortexGate, run_tool


def run_open_ticket(
    factory: Factory,
    ticket_id: str,
    *,
    gate: CortexGate,
    tool: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    ticket = factory.tickets.get(ticket_id)
    if ticket is None or ticket.status != "open":
        raise FactoryDenied("ticket not open")
    body = dict(payload or {})
    if has_bodies(body) or "prompt" in body:
        raise CortexDenied("skill_body must never go to a child job")
    try:
        out = run_tool(gate, tool, body)
        result: dict[str, Any] = {
            "status": "DONE",
            "ticket_id": ticket_id,
            "output": out,
            "refusal": None,
        }
    except CortexDenied as exc:
        result = {
            "status": "FAILED",
            "ticket_id": ticket_id,
            "output": None,
            "refusal": str(exc),
        }
    if ticket.status != "open":
        raise FactoryDenied("runner closed the ticket")
    return result


def board_from_runs(factory: Factory, results: list[dict[str, Any]]) -> dict[str, Any]:
    refusals = [
        {"id": r["ticket_id"], "reason": r["refusal"]}
        for r in results
        if r.get("status") == "FAILED" and r.get("refusal")
    ]
    return project_board(
        crew_index=factory.index(),
        ledger_peek=[],
        refusals=refusals,
    )
