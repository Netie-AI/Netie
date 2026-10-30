"""Palantir-class ontology for DMS. Object types are granted tables.

Study notes: cogitorium / semantica / zep. Do not clone Palantir Foundry.
Chat cannot invent an object. Evidence must cite a granted warehouse table.
Not a second warehouse brain.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from dms_space_acl import SpaceDenied, tables_for_space, warehouse_for_space

Acl = Mapping[str, frozenset[str]]
Binds = Mapping[str, str]

# Palantir-shaped names we will not import as a product.
PALANTIR_VENDORS = frozenset(
    {
        "palantir",
        "foundry",
        "ontology-sdk",
        "ontology_sdk",
        "compass",
        "phonograph",
        "object-set",
        "object_set",
    }
)


class OntologyDenied(SpaceDenied):
    """Object type is not a granted table, or evidence has no cite."""


def refuse_vendor(name: str) -> None:
    needle = (name or "").strip().lower().replace(" ", "-")
    if needle in PALANTIR_VENDORS or "palantir" in needle:
        raise OntologyDenied("do not clone Palantir")


def object_types(acl: Acl, space_id: str) -> tuple[str, ...]:
    """Ontology objects = tables this Space may read. Nothing invented."""
    return tuple(sorted(tables_for_space(acl, space_id)))


def mint_object(
    acl: Acl,
    space_id: str,
    name: str,
    *,
    vendor: str = "",
) -> str:
    refuse_vendor(vendor)
    want = (name or "").strip()
    if not want:
        raise OntologyDenied("unlabeled object")
    granted = tables_for_space(acl, space_id)
    if want not in granted:
        raise OntologyDenied(f"object {want} not granted")
    return want


def link_objects(
    acl: Acl,
    space_id: str,
    src: str,
    dest: str,
) -> tuple[str, str]:
    left = mint_object(acl, space_id, src)
    right = mint_object(acl, space_id, dest)
    if left == right:
        raise OntologyDenied("link needs two objects")
    return left, right


def evidence_or_abstain(
    acl: Acl,
    space_id: str,
    row: dict[str, Any] | None,
    *,
    warehouse_id: str,
    binds: Binds,
) -> dict[str, Any]:
    """A row is evidence only when it cites a granted table on the bound warehouse."""
    try:
        bound = warehouse_for_space(binds, space_id)
    except SpaceDenied as exc:
        return {"status": "ABSTAIN", "reason": str(exc), "row": None}
    asked = (warehouse_id or "").strip()
    if asked != bound:
        return {"status": "ABSTAIN", "reason": "wrong warehouse", "row": None}
    bag = dict(row or {})
    table = str(bag.get("table") or bag.get("object_type") or "").strip()
    if not table:
        return {"status": "ABSTAIN", "reason": "evidence has no table", "row": None}
    try:
        mint_object(acl, space_id, table)
    except OntologyDenied as exc:
        return {"status": "ABSTAIN", "reason": str(exc), "row": None}
    return {
        "status": "OK",
        "table": table,
        "warehouse_id": bound,
        "row": dict(bag),
    }
