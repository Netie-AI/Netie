"""PRD -> epic -> ticket factory. WIP 2. Close updates the parent. No infinite idle agents.

Mirrors Internal/Agents/AGENT_SYSTEM.md. GitHub Issues stay the backlog; this is the
contract Crew must run. A ticket cannot close without a different-run verify and
without editing its epic's task list in the same action.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from crew_verify import close_ticket

TIERS = ("foundation", "boundary", "capability", "surface", "demo")
MAX_OPEN_EPICS = 2


class SliceDenied(PermissionError):
    """PRD Agent refuses. It is a wish, not a spec."""


class FactoryDenied(PermissionError):
    """Epic or ticket stays open."""


@dataclass
class Epic:
    id: str
    title: str
    tier: str
    tasks: dict[str, str] = field(default_factory=dict)
    status: str = "open"


@dataclass
class Ticket:
    id: str
    epic_id: str
    prompt: str
    status: str = "open"


@dataclass
class Factory:
    epics: dict[str, Epic] = field(default_factory=dict)
    tickets: dict[str, Ticket] = field(default_factory=dict)

    def slice_prd(
        self,
        *,
        prd_id: str,
        out_of_scope: str,
        success_assertion: str,
        epics: list[tuple[str, str, str]],
    ) -> list[Epic]:
        if not (out_of_scope or "").strip():
            raise SliceDenied("no out of scope")
        if "WHEN" not in success_assertion or "SHALL" not in success_assertion:
            raise SliceDenied("success assertion not testable")
        ordered = sorted(epics, key=lambda row: TIERS.index(row[2]))
        made: list[Epic] = []
        for eid, title, tier in ordered:
            if tier not in TIERS:
                raise SliceDenied(f"bad tier {tier}")
            epic = Epic(id=eid, title=title, tier=tier, status="queued")
            self.epics[eid] = epic
            made.append(epic)
        return made

    def activate_epic(self, epic_id: str) -> Epic:
        open_n = sum(1 for e in self.epics.values() if e.status == "open")
        if open_n >= MAX_OPEN_EPICS:
            raise FactoryDenied("WIP: 2 epics")
        epic = self.epics[epic_id]
        if epic.status == "done":
            raise FactoryDenied("epic already done")
        epic.status = "open"
        return epic

    def file_ticket(self, *, epic_id: str, ticket_id: str, prompt: str) -> Ticket:
        epic = self.epics[epic_id]
        open_epics = [e for e in self.epics.values() if e.status == "open"]
        if len(open_epics) > MAX_OPEN_EPICS:
            raise FactoryDenied("WIP: 2 epics")
        if epic.status != "open":
            raise FactoryDenied("epic not open")
        if not prompt.strip():
            raise FactoryDenied("no embedded prompt")
        t = Ticket(id=ticket_id, epic_id=epic_id, prompt=prompt.strip())
        self.tickets[ticket_id] = t
        epic.tasks[ticket_id] = "open"
        return t

    def close_ticket(
        self,
        ticket_id: str,
        *,
        implementer_run_id: str,
        verifier_run_id: str,
        evidence: str,
    ) -> str:
        t = self.tickets[ticket_id]
        close_ticket(
            ticket_id=ticket_id,
            implementer_run_id=implementer_run_id,
            verifier_run_id=verifier_run_id,
            evidence=evidence,
        )
        t.status = "done"
        self.epics[t.epic_id].tasks[ticket_id] = "done"
        return (
            f"DONE  {ticket_id}  {evidence.strip()}  {verifier_run_id}"
        )

    def maybe_complete_epic(self, epic_id: str) -> str:
        epic = self.epics[epic_id]
        if not epic.tasks:
            raise FactoryDenied("no tickets")
        if any(v != "done" for v in epic.tasks.values()):
            return f"BLOCKED  {epic_id}  open tickets"
        epic.status = "done"
        return f"DONE  {epic_id}  all tickets verified"
