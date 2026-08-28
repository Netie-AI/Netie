"""Space ACL contract for DMS (PRD-001 wave 1). Spec in Netie until dms is reachable.

live_ask today mints from demo_acl() (every table). Two customers in one room
is a demo we cannot give. This module is the failing test that slice must pass:
a Space sees only the tables it was granted, only from the warehouse it is
bound to, and abstains otherwise.

HEAD has two DuckDBs (Studio bronze vs Cortex serving). An uploaded sheet is
unreachable by chat, silently. Naming the warehouse is the fail-close.

Not a second Cortex. Not a warehouse ChatGPT overlay.
"""

from __future__ import annotations

import re
from collections.abc import Mapping

Acl = Mapping[str, frozenset[str]]
Binds = Mapping[str, str]


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


def warehouse_for_space(binds: Binds, space_id: str) -> str:
    wid = (binds.get(space_id) or "").strip()
    if not wid:
        raise SpaceDenied(f"unbound space {space_id}")
    return wid


def may_read(acl: Acl, space_id: str, table: str) -> bool:
    try:
        return table in tables_for_space(acl, space_id)
    except SpaceDenied:
        return False


def known_tables(acl: Acl) -> frozenset[str]:
    names: set[str] = set(DEMO_ALL_TABLES)
    for tables in acl.values():
        names |= set(tables)
    return frozenset(names)


def sql_outside_grant(
    sql: str, *, table: str, granted: frozenset[str], universe: frozenset[str]
) -> str | None:
    """Reason to abstain if SQL names a table this Space cannot read.

    Not a SQL parser. Word-boundary scan of known warehouse names. The asked
    table must appear. A JOIN onto an ungranted name is a punch through the ACL.
    """
    blob = (sql or "").lower()
    asked = (table or "").strip().lower()
    if not asked:
        return "sql has no table"
    if not re.search(rf"\b{re.escape(asked)}\b", blob):
        return f"sql does not name {table}"
    for name in universe:
        if name.lower() == asked:
            continue
        if not re.search(rf"\b{re.escape(name.lower())}\b", blob):
            continue
        if name not in granted:
            return f"sql names {name}"
    return None


def mint_manifest(acl: Acl, space_id: str) -> tuple[str, ...]:
    """Tables this Space may touch. Must not fall back to DEMO_ALL_TABLES."""
    granted = tables_for_space(acl, space_id)
    if granted == DEMO_ALL_TABLES and space_id != "demo":
        raise SpaceDenied("demo_acl leak")
    return tuple(sorted(granted))


def answer_or_abstain(
    acl: Acl,
    space_id: str,
    table: str,
    rows: list[dict],
    *,
    warehouse_id: str,
    binds: Binds,
    sql: str,
    chat_mode: bool = False,
) -> dict:
    if chat_mode:
        return {
            "status": "ABSTAIN",
            "reason": "AnythingLLM overlay; warehouse answers need SQL",
            "rows": [],
        }
    try:
        bound = warehouse_for_space(binds, space_id)
    except SpaceDenied as exc:
        return {"status": "ABSTAIN", "reason": str(exc), "rows": []}
    asked = (warehouse_id or "").strip()
    if asked != bound:
        return {
            "status": "ABSTAIN",
            "reason": f"space {space_id} bound to {bound}, asked {asked or 'none'}",
            "rows": [],
        }
    if not (sql or "").strip():
        return {
            "status": "ABSTAIN",
            "reason": f"space {space_id} answer has no SQL",
            "rows": [],
        }
    if not may_read(acl, space_id, table):
        return {
            "status": "ABSTAIN",
            "reason": f"space {space_id} cannot read {table}",
            "rows": [],
        }
    granted = tables_for_space(acl, space_id)
    leak = sql_outside_grant(
        sql, table=table, granted=granted, universe=known_tables(acl)
    )
    if leak:
        return {
            "status": "ABSTAIN",
            "reason": f"space {space_id} {leak}",
            "rows": [],
        }
    cleaned: list[dict] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        declared = row.get("table") or row.get("_table")
        if declared and declared != table:
            return {
                "status": "ABSTAIN",
                "reason": f"space {space_id} cannot read {declared}",
                "rows": [],
            }
        cleaned.append(dict(row))
    return {
        "status": "OK",
        "table": table,
        "warehouse_id": bound,
        "sql": sql.strip(),
        "rows": cleaned,
    }


def browse_or_abstain(
    acl: Acl,
    space_id: str,
    table: str,
    *,
    tier: str,
) -> dict:
    """Library/Studio browse. Bronze has no HEAD allowlist; this contract does.

    warehouse ChatGPT analogues still cannot see another customer's bronze.
    """
    name = (tier or "").strip().lower()
    if name not in {"warehouse", "bronze"}:
        return {
            "status": "ABSTAIN",
            "reason": f"bad browse tier {tier or 'none'}",
            "rows": [],
        }
    if not may_read(acl, space_id, table):
        return {
            "status": "ABSTAIN",
            "reason": f"space {space_id} cannot browse {table}",
            "rows": [],
        }
    return {"status": "OK", "table": table, "tier": name}
