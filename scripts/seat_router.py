"""Licensed-seat router. Original code. Not Grok Bot reconstructed.

Crew may queue a ticket into Cursor, Claude Code, or Codex the operator already
pays for. This module records the dispatch. It does not click a vendor UI
or harvest a session.
"""

from __future__ import annotations

from dataclasses import dataclass

ALLOWED_SEATS = frozenset({"cursor", "claude-code", "codex"})
BYPASS_SEATS = frozenset(
    {
        "grok-bot",
        "grok-bot-reconstructed",
        "pointer-drive",
        "cursor-ui",
        "claude.app",
    }
)


class SeatDenied(PermissionError):
    """Ticket stays in GitHub. No licensed seat, or a billing-bypass product."""


@dataclass(frozen=True)
class SeatDispatch:
    ticket_id: str
    seat: str
    status: str


def dispatch_seat(
    *,
    ticket_id: str,
    seat: str,
    operator_logged_in: bool,
) -> SeatDispatch:
    if not ticket_id.strip():
        raise SeatDenied("no ticket")
    product = seat.strip().lower()
    if product in BYPASS_SEATS:
        raise SeatDenied("billing-bypass product")
    if product not in ALLOWED_SEATS:
        raise SeatDenied(f"not a licensed seat: {seat}")
    if not operator_logged_in:
        raise SeatDenied("no licensed login on this machine")
    return SeatDispatch(ticket_id=ticket_id.strip(), seat=product, status="queued")
