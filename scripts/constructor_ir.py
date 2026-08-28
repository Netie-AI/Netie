"""Fail-closed Constructor -> Cortex IR. Canvas JS may drift; this is the import.

constructor_honesty.py only refuses xyflow-as-compiler. This module compiles.
Crew/Cortex agents import compile_ir instead of copying Activeflow or Activepieces.
"""

from __future__ import annotations

from typing import Any

from cortex_path import WRITE_ACTIONS

CORTEX_KIND = {
    "ingest": "DOCUMENT_REF",
    "connector": "DOCUMENT_REF",
    "ontology": "DOCUMENT_REF",
    "insight": "DOCUMENT_REF",
    "foundry": "DOCUMENT_REF",
    "app": "EMIT",
    "agent": "AGENT_TASK",
    "hypothesize": "DOCUMENT_REF",
    "enhance": "DOCUMENT_REF",
    "improve": "DOCUMENT_REF",
    "audit": "DOCUMENT_REF",
    "tool_call": "TOOL_CALL",
}

OBJECT_KINDS = frozenset(
    {"ingest", "connector", "ontology", "insight", "foundry", "enhance", "improve"}
)
ASSUME_NEEDLES = ("inventory", "export_pptx", "T0")
NOTE_LEAK = ("skill_body", "prompt", "transcript")
MAX_NOTE_CHARS = 12000
DEFAULT_OBJECTS = ("inventory", "suppliers")
DEFAULT_OBJECT_POINTS: dict[str, tuple[str, ...]] = {
    "inventory": (
        "sku",
        "sku_name",
        "category",
        "supplier_id",
        "location_id",
        "storage_bin",
        "quantity_kg",
        "reorder_level_kg",
        "unit_cost_myr",
        "last_restocked",
        "expiry_date",
        "is_hazardous",
    ),
    "suppliers": (
        "supplier_id",
        "supplier_name",
        "country",
        "lead_time_days",
        "payment_terms",
        "last_audit_date",
        "risk_score",
    ),
}


class ConstructorIRDenied(ValueError):
    """Graph does not compile. Constructor must not invent Cortex defaults."""


def listed_or_empty(value: Any, listed: tuple[str, ...] | list[str]) -> str:
    want = str(value or "").strip()
    if want not in listed:
        return ""
    return want


def _id(node: dict[str, Any]) -> str:
    raw = node.get("id")
    if raw is None or str(raw).strip() == "":
        raise ConstructorIRDenied("missing id")
    return str(raw)


def topo(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> list[str]:
    """Kahn prefix only. Cyclic leftovers are omitted, not appended."""
    ids = [_id(n) for n in nodes]
    incoming = {i: 0 for i in ids}
    for e in edges:
        if e.get("to") in incoming:
            incoming[e["to"]] += 1
    q = [i for i in ids if incoming[i] == 0]
    out: list[str] = []
    while q:
        cur = q.pop(0)
        out.append(cur)
        for e in edges:
            if e.get("from") != cur:
                continue
            dest = e.get("to")
            if dest not in incoming:
                continue
            incoming[dest] -= 1
            if incoming[dest] == 0:
                q.append(dest)
    return out


def _components(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> int:
    ids = [_id(n) for n in nodes]
    adj: dict[str, set[str]] = {i: set() for i in ids}
    for e in edges:
        a, b = e.get("from"), e.get("to")
        if a in adj and b in adj:
            adj[a].add(str(b))
            adj[b].add(str(a))
    seen: set[str] = set()
    n = 0
    for start in ids:
        if start in seen:
            continue
        n += 1
        stack = [start]
        while stack:
            cur = stack.pop()
            if cur in seen:
                continue
            seen.add(cur)
            stack.extend(adj[cur] - seen)
    return n


def refuse_assumed(utterance: str, injected: dict[str, Any] | None) -> None:
    """Chat/buildGraph must not inject inventory / export_pptx / T0 unsaid."""
    text = (utterance or "").lower()
    bag = injected or {}
    for needle in ASSUME_NEEDLES:
        hit = needle in text
        values = [str(v).lower() for v in bag.values() if v is not None]
        if needle in values and not hit:
            raise ConstructorIRDenied(f"assumed {needle}")


def compile_ir(
    nodes: list[dict[str, Any]] | None,
    edges: list[dict[str, Any]] | None = None,
    *,
    ghost: bool = False,
    utterance: str = "",
    assumed: dict[str, Any] | None = None,
    objects: list[str] | tuple[str, ...] | None = None,
    object_points: dict[str, list[str] | tuple[str, ...]] | None = None,
) -> dict[str, Any]:
    nodes = list(nodes or [])
    edges = list(edges or [])
    listed = tuple(objects) if objects else DEFAULT_OBJECTS
    points = object_points or DEFAULT_OBJECT_POINTS
    if assumed:
        refuse_assumed(utterance, assumed)
    if not nodes:
        raise ConstructorIRDenied("empty graph")
    seen: set[str] = set()
    for n in nodes:
        nid = _id(n)
        if nid in seen:
            raise ConstructorIRDenied(f"duplicate id: {nid}")
        seen.add(nid)
        kind = n.get("kind")
        if kind not in CORTEX_KIND:
            raise ConstructorIRDenied(f"unknown kind: {kind}")
        note = str(n.get("note") or "")
        if len(note) > MAX_NOTE_CHARS:
            raise ConstructorIRDenied("NOTE_LEAK")
        low = note.lower()
        if any(needle in low for needle in NOTE_LEAK):
            raise ConstructorIRDenied("NOTE_LEAK")
        if kind == "tool_call":
            at = str(n.get("action_type") or "").strip()
            if not at:
                raise ConstructorIRDenied("tool_call missing action_type")
            if at not in WRITE_ACTIONS:
                raise ConstructorIRDenied("tool_call unknown action_type")
        if kind in OBJECT_KINDS and not str(n.get("object_type") or "").strip():
            raise ConstructorIRDenied("unlabeled object")
        if n.get("object_type") is None and str(n.get("data_point") or "") == "":
            if "inventory" in low:
                raise ConstructorIRDenied("unlabeled set point")
    ids = {_id(n) for n in nodes}
    for e in edges:
        if e.get("from") not in ids or e.get("to") not in ids:
            raise ConstructorIRDenied("dangling edge")
    if _components(nodes, edges) > 1:
        raise ConstructorIRDenied("disconnected")
    order = topo(nodes, edges)
    if len(order) != len(nodes):
        raise ConstructorIRDenied("cycle")
    by_id = {_id(n): n for n in nodes}
    kahn_nodes = [by_id[i] for i in order]
    apps = [n for n in kahn_nodes if n.get("kind") == "app"]
    sink = apps[-1] if apps else None
    if sink is None:
        audits = [n for n in kahn_nodes if n.get("kind") == "audit"]
        sink = audits[-1] if audits else None
    if sink is None:
        sinks = [
            n
            for n in kahn_nodes
            if not any(e.get("from") == _id(n) for e in edges)
        ]
        if len(sinks) != 1:
            raise ConstructorIRDenied("ambiguous output")
        sink = sinks[0]
    entry = kahn_nodes[0]
    ir_nodes = []
    for n in kahn_nodes:
        nid = _id(n)
        kind = CORTEX_KIND[n["kind"]]
        if nid == _id(sink) and n.get("kind") in {"app", "audit"}:
            kind = "EMIT"
        elif kind == "EMIT":
            kind = "DETERMINISTIC_RULE"
        object_type = listed_or_empty(n.get("object_type"), listed) or None
        fetch_from = str(n.get("fetch_from") or "").strip()
        if fetch_from:
            want = f"warehouse.{object_type}" if object_type else ""
            if fetch_from != want:
                raise ConstructorIRDenied("fetch_from mismatch")
        data_point = str(n.get("data_point") or "").strip() or None
        if data_point:
            allowed = tuple(points.get(object_type or "", ()) or ())
            if data_point not in allowed:
                raise ConstructorIRDenied("unlisted data_point")
        action_type = str(n.get("action_type") or "").strip() or None
        ir_nodes.append(
            {
                "id": nid,
                "kind": kind,
                "constructor_kind": n["kind"],
                "object_type": object_type,
                "data_point": data_point,
                "action_type": action_type,
                "tier": str(n.get("tier") or "").strip() or None,
                "requires_confirm": n.get("kind") == "tool_call"
                or action_type in WRITE_ACTIONS,
            }
        )
    return {
        "version": "1.0",
        "engine": "cortex",
        "ghost": bool(ghost),
        "entry_node_id": _id(entry),
        "output_node_id": _id(sink),
        "nodes": ir_nodes,
        "edges": list(edges),
    }


def ghost_walk(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Refuse instead of walking a fake order. No leftover cycle walk."""
    compile_ir(nodes, edges, ghost=True)
    return topo(nodes, edges or [])
