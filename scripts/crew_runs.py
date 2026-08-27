"""Parent-run graph. Children cannot replace the parent. WIP is 2 open parents.

DR-0012: one parent owns the original task; children spawn from a named deficit;
OpenVault answers may this child invoke/leave/spend; index is ids+status only.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from crew_ov_gate import GateAsk, OpenVaultCrewGate
from crew_tool_wrap import CortexDenied
from crew_verify import VerifyDenied, close_ticket

MAX_OPEN_PARENTS = 2


class WipDenied(PermissionError):
    """Two epics in flight. A third parent does not start."""


class ParentDropped(PermissionError):
    """Child tried to outlive or replace the parent. Ticket stays open."""


@dataclass
class Run:
    id: str
    ticket_id: str
    parent_id: str | None
    status: str
    deficit: str = ""
    transcript: str = ""


@dataclass
class CrewGraph:
    ov: OpenVaultCrewGate
    runs: dict[str, Run] = field(default_factory=dict)

    def open_parent(self, run_id: str, ticket_id: str) -> Run:
        open_parents = [
            r
            for r in self.runs.values()
            if r.parent_id is None and r.status == "open"
        ]
        if len(open_parents) >= MAX_OPEN_PARENTS:
            raise WipDenied("WIP: 2 epics")
        run = Run(id=run_id, ticket_id=ticket_id, parent_id=None, status="open")
        self.runs[run_id] = run
        return run

    def spawn_child(
        self,
        *,
        parent_id: str,
        child_id: str,
        deficit: str,
        intent: str = "invoke",
        kind: str = "skill",
        resource_id: str = "netie-kb.skills",
    ) -> Run:
        parent = self.runs.get(parent_id)
        if parent is None or parent.parent_id is not None:
            raise ParentDropped("parent run missing")
        if parent.status != "open":
            raise ParentDropped("parent not open")
        if not deficit.strip():
            raise CortexDenied("no deficit")
        self.ov.allow(
            GateAsk(
                kind=kind,
                id=resource_id,
                intent=intent,
                parent_run_id=parent_id,
                child_id=child_id,
                deficit=deficit.strip(),
            )
        )
        child = Run(
            id=child_id,
            ticket_id=parent.ticket_id,
            parent_id=parent_id,
            status="open",
            deficit=deficit.strip(),
        )
        self.runs[child_id] = child
        return child

    def finish_child(self, child_id: str, status: str = "done") -> Run:
        child = self.runs[child_id]
        if child.parent_id is None:
            raise ParentDropped("not a child")
        child.status = status
        return child

    def finish_parent(
        self,
        parent_id: str,
        *,
        implementer_run_id: str,
        verifier_run_id: str,
        evidence: str,
    ) -> Run:
        parent = self.runs[parent_id]
        if parent.parent_id is not None:
            raise ParentDropped("not a parent")
        open_kids = [
            r
            for r in self.runs.values()
            if r.parent_id == parent_id and r.status == "open"
        ]
        if open_kids:
            raise ParentDropped("open children")
        close_ticket(
            ticket_id=parent.ticket_id,
            implementer_run_id=implementer_run_id,
            verifier_run_id=verifier_run_id,
            evidence=evidence,
        )
        parent.status = "done"
        return parent

    def index(self) -> dict:
        """Token-cheap. No transcripts, no skill bodies, no deficit text."""
        return {
            "runs": [
                {
                    "id": r.id,
                    "status": r.status,
                    "parent_id": r.parent_id,
                    "ticket_id": r.ticket_id,
                }
                for r in self.runs.values()
            ]
        }
