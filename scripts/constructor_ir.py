"""Fail-closed Constructor -> Cortex IR. Canvas JS may drift; this is the import.

constructor_honesty.py only refuses xyflow-as-compiler. This module compiles.
Crew/Cortex agents import compile_ir instead of copying Activeflow or Activepieces.
"""

from __future__ import annotations

from typing import Any

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


class ConstructorIRDenied(ValueError):
    """Graph does not compile. Constructor must not invent Cortex defaults."""


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
) -> dict[str, Any]:
    nodes = list(nodes or [])
    edges = list(edges or [])
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
        if kind == "tool_call" and not str(n.get("action_type") or "").strip():
            raise ConstructorIRDenied("tool_call missing action_type")
        if kind in OBJECT_KINDS and not str(n.get("object_type") or "").strip():
            raise ConstructorIRDenied("unlabeled object")
        if n.get("object_type") is None and str(n.get("data_point") or "") == "":
            if str(n.get("note") or "").lower().find("inventory") >= 0:
                raise ConstructorIRDenied("unlabeled set point")
    ids = {_id(n) for n in nodes}
    for e in edges:
        if e.get("from") not in ids or e.get("to") not in ids:
            raise ConstructorIRDenied("dangling edge")
    order = topo(nodes, edges)
    if len(order) != len(nodes):
        raise ConstructorIRDenied("cycle")
    by_id = {_id(n): n for n in nodes}
    kahn_nodes = [by_id[i] for i in order]
    sink = next((n for n in reversed(kahn_nodes) if n.get("kind") == "app"), None)
    if sink is None:
        sink = next((n for n in reversed(kahn_nodes) if n.get("kind") == "audit"), None)
    if sink is None:
        sink = kahn_nodes[-1]
    entry = kahn_nodes[0]
    ir_nodes = []
    for n in nodes:
        nid = _id(n)
        kind = CORTEX_KIND[n["kind"]]
        if nid == _id(sink) and n.get("kind") in {"app", "audit"}:
            kind = "EMIT"
        elif kind == "EMIT":
            kind = "DETERMINISTIC_RULE"
        ir_nodes.append(
            {
                "id": nid,
                "kind": kind,
                "constructor_kind": n["kind"],
                "object_type": n.get("object_type") or None,
                "data_point": n.get("data_point") or None,
                "action_type": n.get("action_type") or None,
                "tier": n.get("tier") if n.get("tier") else None,
                "requires_confirm": n.get("kind") == "tool_call",
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
