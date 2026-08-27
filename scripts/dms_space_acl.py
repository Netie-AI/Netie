"""Space ACL contract for DMS (PRD-001 wave 1). Spec in Netie until dms is reachable.

live_ask today mints from demo_acl() (every table). Two customers in one room
is a demo we cannot give. This module is the failing test that slice must pass:
a Space sees only the tables it was granted, and abstains otherwise.

Not a second Cortex. Not a warehouse ChatGPT overlay.
"""

from __future__ import annotations

from collections.abc import Mapping

Acl = Mapping[str, frozenset[str]]


class SpaceDenied(PermissionError):
    """Abstain. The Space cannot see that table (or does not exist)."""


# The production bug: a demo allowlist of every table, ignoring space_id.
DEMO_ALL_TABLES = frozenset({"inventory", "shipments", "invoices", "hr_notes"})


def tables_for_space(acl: Acl, space_id: str) -> frozenset[str]:
    if space_id not in acl:
        raise SpaceDenied(f"unknown space {space_id}")
    tables = acl[space_id]
    if not tables:
        raise SpaceDenied(f"empty space {space_id}")
    return tables


def may_read(acl: Acl, space_id: str, table: str) -> bool:
    try:
        return table in tables_for_space(acl, space_id)
    except SpaceDenied:
        return False


def mint_manifest(acl: Acl, space_id: str) -> tuple[str, ...]:
    """Tables this Space may touch. Must not fall back to DEMO_ALL_TABLES."""
    granted = tables_for_space(acl, space_id)
    if granted == DEMO_ALL_TABLES and space_id != "demo":
        raise SpaceDenied("demo_acl leak")
    return tuple(sorted(granted))


def answer_or_abstain(acl: Acl, space_id: str, table: str, rows: list[dict]) -> dict:
    if not may_read(acl, space_id, table):
        return {
            "status": "ABSTAIN",
            "reason": f"space {space_id} cannot read {table}",
            "rows": [],
        }
    return {"status": "OK", "table": table, "rows": rows}
