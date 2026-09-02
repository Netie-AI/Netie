"""Deep Agents checkpoints, without the transcript.

LangGraph MemorySaver would persist the conversation. Crew persists ids and
status only. Resume cannot recover a prompt. That is the token-cheap gate.
"""

from __future__ import annotations

import json
from typing import Any

from crew_ov_gate import DROP_KEYS, has_bodies
from crew_runs import CrewGraph
from crew_skills import SkillRegistry


class CheckpointDenied(PermissionError):
    """Checkpoint stays ids-only. Ticket stays open."""


def save_checkpoint(
    index: dict[str, Any],
    *,
    todos: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if has_bodies(index) or has_bodies(todos or []):
        raise CheckpointDenied("checkpoint leaked a body")
    blob: dict[str, Any] = {
        "runs": [
            {
                "id": r.get("id"),
                "status": r.get("status"),
                "parent_id": r.get("parent_id"),
                "ticket_id": r.get("ticket_id"),
            }
            for r in (index.get("runs") or [])
            if isinstance(r, dict)
        ],
        "todos": [
            {"id": t.get("id"), "status": t.get("status")}
            for t in (todos or [])
            if isinstance(t, dict)
        ],
        "skills": [
            {"id": s.get("id"), "source": s.get("source")}
            for s in (index.get("skills") or [])
            if isinstance(s, dict)
        ],
    }
    dumped = json.dumps(blob)
    for needle in DROP_KEYS:
        if needle in dumped:
            raise CheckpointDenied(f"checkpoint contained {needle}")
    return blob


def load_checkpoint(blob: dict[str, Any]) -> dict[str, Any]:
    if has_bodies(blob):
        raise CheckpointDenied("checkpoint leaked a body")
    return save_checkpoint(blob, todos=blob.get("todos") if isinstance(blob, dict) else None)


def summarise(
    index: dict[str, Any],
    registry: SkillRegistry | None = None,
) -> dict[str, Any]:
    """Deep Agents summarise, without the conversation. Skill ids, not bodies."""
    if has_bodies(index):
        raise CheckpointDenied("summary leaked a body")
    runs = [r for r in (index.get("runs") or []) if isinstance(r, dict)]
    skills = [s for s in (index.get("skills") or []) if isinstance(s, dict)]
    if registry is not None:
        skills = registry.index()
    for row in skills:
        if has_bodies(row):
            raise CheckpointDenied("summary leaked a body")
    out = {
        "open": sum(1 for r in runs if r.get("status") == "open"),
        "done": sum(1 for r in runs if r.get("status") == "done"),
        "run_ids": [r.get("id") for r in runs],
        "skills": len(skills),
        "skill_ids": [s.get("id") for s in skills],
        "tokens": "ids-only",
    }
    dumped = json.dumps(out)
    for needle in DROP_KEYS:
        if needle in dumped:
            raise CheckpointDenied(f"summary contained {needle}")
    return out


def checkpoint_graph(
    graph: CrewGraph,
    registry: SkillRegistry | None = None,
) -> dict[str, Any]:
    """Ids-only blob. `registry` defaults to `graph.ov.registry` like persist."""
    target = registry if registry is not None else getattr(graph.ov, "registry", None)
    idx = graph.index()
    if target is not None:
        idx = {**idx, "skills": target.index()}
    return save_checkpoint(idx)
