"""Different-run verification (NETIE.md R-0003). The implementer cannot close.

Crew may mark DONE only when a second run supplies evidence. Same-run close is
FAILED, not a shortcut.
"""

from __future__ import annotations

from dataclasses import dataclass


class VerifyDenied(PermissionError):
    """Ticket stays open. The adversary is never the verifier."""


@dataclass(frozen=True)
class TicketClose:
    ticket_id: str
    status: str
    implementer_run_id: str
    verified_by: str
    evidence: str


def close_ticket(
    *,
    ticket_id: str,
    implementer_run_id: str,
    verifier_run_id: str,
    evidence: str,
) -> TicketClose:
    if not ticket_id.strip():
        raise VerifyDenied("no ticket")
    if not implementer_run_id.strip() or not verifier_run_id.strip():
        raise VerifyDenied("both runs required")
    if implementer_run_id == verifier_run_id:
        raise VerifyDenied("adversary is never the verifier")
    if not evidence.strip():
        raise VerifyDenied("no evidence")
    return TicketClose(
        ticket_id=ticket_id,
        status="DONE",
        implementer_run_id=implementer_run_id,
        verified_by=verifier_run_id,
        evidence=evidence.strip(),
    )
