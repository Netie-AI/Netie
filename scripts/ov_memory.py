"""Graphiti/zep/graphify stay out. Memory is OpenVault kind + Space ids.

AirGPT retrieve_space already cites a Space. This module is the fourth-store
refuse: no Graphiti graph, no Zep session dump, no Graphify overlay.
OV ACCESS_KINDS already includes memory. Bodies never ride the row.
"""

from __future__ import annotations

from typing import Any

VENDORS = frozenset(
    {
        "graphiti",
        "zep",
        "zep-go",
        "graphify",
        "neo4j",
        "falkordb",
        "mem0",
    }
)
DROP = frozenset({"skill_body", "prompt", "transcript", "embedding", "graph"})


class MemoryDenied(PermissionError):
    """Fourth store or a body on a memory row."""


def refuse_vendor(name: str) -> None:
    needle = (name or "").strip().lower().replace("_", "-")
    if needle in VENDORS or any(v in needle for v in ("graphiti", "zep", "graphify")):
        raise MemoryDenied("memory is OpenVault+Cortex, not a fourth store")


def remember(
    space_id: str,
    item_id: str,
    *,
    vendor: str = "",
    body: object | None = None,
    skill_body: object | None = None,
) -> dict[str, str]:
    refuse_vendor(vendor)
    sid = (space_id or "").strip()
    iid = (item_id or "").strip()
    if not sid:
        raise MemoryDenied("memory needs a Space")
    if not iid:
        raise MemoryDenied("memory needs an id")
    if body is not None or skill_body is not None:
        raise MemoryDenied("memory row is ids-only")
    return {"kind": "memory", "space_id": sid, "id": iid}


def recall(rows: list[dict[str, Any]] | None, space_id: str) -> list[dict[str, str]]:
    """Ids for one Space. Other Spaces and bodies are dropped."""
    want = (space_id or "").strip()
    if not want:
        raise MemoryDenied("memory needs a Space")
    out: list[dict[str, str]] = []
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        if any(k in row for k in DROP):
            raise MemoryDenied("memory row leaked a body")
        if str(row.get("space_id") or "").strip() != want:
            continue
        iid = str(row.get("id") or "").strip()
        if not iid:
            continue
        out.append({"kind": "memory", "space_id": want, "id": iid})
    return out
