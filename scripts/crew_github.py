"""GitHub Issues stay the backlog. Issue body never becomes a child job.

PRD-002: pull one ticket with an embedded prompt; the runner calls Cortex
with a payload that does not carry that prompt. A body that looks like a
skill dump is a refusal, not a child.
"""

from __future__ import annotations

from crew_budget import TokenBudget
from crew_factory import Factory, FactoryDenied
from crew_ov_gate import OpenVaultCrewGate
from crew_runner import run_open_ticket
from crew_tool_wrap import CortexDenied, CortexGate


class IssueDenied(CortexDenied):
    """Issue text stays on GitHub. The runner only sees ids and a tool name."""


def mint_issue(
    factory: Factory,
    *,
    epic_id: str,
    number: int,
    title: str,
    body: str = "",
) -> str:
    """Mint a Factory ticket from a GitHub issue. Body is not a skill_body."""
    blob = f"{title or ''}\n{body or ''}".lower()
    if "skill_body" in blob or "transcript" in blob:
        raise IssueDenied("issue body stays out of the runner")
    name = (title or "").strip()
    if not name:
        raise FactoryDenied("no issue title")
    tid = f"gh-{int(number)}"
    factory.file_ticket(epic_id=epic_id, ticket_id=tid, prompt=name)
    return tid


def run_issue(
    factory: Factory,
    ticket_id: str,
    *,
    gate: CortexGate,
    tool: str,
    payload: dict,
    budget: TokenBudget | None = None,
    ov: OpenVaultCrewGate | None = None,
    ov_allowed: bool = False,
    parent_run_id: str = "",
    child_id: str = "",
    granted: frozenset[str] | list[str] | tuple[str, ...] | None = None,
) -> dict:
    """Run the ticket. Do not copy factory.tickets[ticket_id].prompt into payload."""
    body = dict(payload or {})
    ticket = factory.tickets.get(ticket_id)
    if ticket is not None and ticket.prompt and ticket.prompt in str(body):
        raise IssueDenied("embedded prompt must not go to a child job")
    return run_open_ticket(
        factory,
        ticket_id,
        gate=gate,
        tool=tool,
        payload=body,
        budget=budget,
        ov=ov,
        ov_allowed=ov_allowed,
        parent_run_id=parent_run_id,
        child_id=child_id,
        granted=granted,
    )
