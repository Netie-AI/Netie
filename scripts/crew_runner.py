"""Ticket runner. Cortex refusal stays on the board. Ticket stays open.

PRD-002: WHEN the runner calls a tool Cortex would refuse, THE SYSTEM SHALL
show the refusal on the board and leave the ticket open. The embedded prompt
never goes to a child job.

Leave-machine names go through execute_capability(ov=) and POST skill ids.
Cortex tools stay on run_tool / prepare_tool. warehouse.query never POSTs.
"""

from __future__ import annotations

from typing import Any

from control_board import board_index, project_board
from crew_budget import BudgetDenied, TokenBudget
from crew_capabilities import LEAVE_CAPS, execute_capability
from crew_factory import Factory, FactoryDenied
from crew_ov_gate import OpenVaultCrewGate, has_bodies
from crew_runs import CrewGraph
from crew_skills import SkillRegistry
from crew_tool_wrap import CortexDenied, CortexGate, run_tool


def run_open_ticket(
    factory: Factory,
    ticket_id: str,
    *,
    gate: CortexGate,
    tool: str,
    payload: dict[str, Any],
    budget: TokenBudget | None = None,
    ov: OpenVaultCrewGate | None = None,
    ov_allowed: bool = False,
    parent_run_id: str = "",
    child_id: str = "",
    granted: frozenset[str] | list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    ticket = factory.tickets.get(ticket_id)
    if ticket is None or ticket.status != "open":
        raise FactoryDenied("ticket not open")
    body = dict(payload or {})
    if has_bodies(body) or "prompt" in body:
        raise CortexDenied("skill_body must never go to a child job")
    if budget is None:
        raise CortexDenied("token budget required; Deep Agents default is unbounded spend")
    try:
        name = (tool or "").strip()
        if name in LEAVE_CAPS:
            caps = granted if granted is not None else (name,)
            out = execute_capability(
                gate,
                name,
                body,
                granted=caps,
                ov_allowed=ov_allowed,
                ov=ov,
                parent_run_id=parent_run_id,
                child_id=(child_id or ticket_id).strip(),
                budget=budget,
            )
        else:
            # Cortex tools stay on prepare_tool. warehouse.query never POSTs.
            out = run_tool(gate, tool, body, budget=budget)
        result: dict[str, Any] = {
            "status": "DONE",
            "ticket_id": ticket_id,
            "output": out,
            "refusal": None,
        }
    except (CortexDenied, BudgetDenied) as exc:
        result = {
            "status": "FAILED",
            "ticket_id": ticket_id,
            "output": None,
            "refusal": str(exc),
        }
    if ticket.status != "open":
        raise FactoryDenied("runner closed the ticket")
    return result


def board_from_runs(
    factory: Factory,
    results: list[dict[str, Any]],
    *,
    graph: CrewGraph | None = None,
    registry: SkillRegistry | None = None,
) -> dict[str, Any]:
    """Ticket-runner board. Factory tickets plus graph runs and skill ids.

    `registry` defaults to `graph.ov.registry` the same way persist does.
    Prompts and skill bodies still refuse.
    """
    refusals = [
        {"id": r["ticket_id"], "reason": r["refusal"]}
        for r in results
        if r.get("status") == "FAILED" and r.get("refusal")
    ]
    target = registry
    if target is None and graph is not None:
        target = getattr(graph.ov, "registry", None)
    idx = board_index(
        graph_index=graph.index() if graph is not None else None,
        factory_index=factory.index(),
        skills=target.index() if target is not None else None,
    )
    return project_board(
        crew_index=idx,
        ledger_peek=[],
        refusals=refusals,
    )
