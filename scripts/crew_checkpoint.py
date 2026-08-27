"""Deep Agents checkpoints, without the transcript.

LangGraph MemorySaver would persist the conversation. Crew persists ids and
status only. Resume cannot recover a prompt. That is the token-cheap gate.
"""

from __future__ import annotations

import json
from typing import Any

from crew_ov_gate import DROP_KEYS, has_bodies
from crew_runs import CrewGraph


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


def summarise(index: dict[str, Any]) -> dict[str, Any]:
    """Deep Agents summarise, without the conversation."""
    if has_bodies(index):
        raise CheckpointDenied("summary leaked a body")
    runs = [r for r in (index.get("runs") or []) if isinstance(r, dict)]
    out = {
        "open": sum(1 for r in runs if r.get("status") == "open"),
        "done": sum(1 for r in runs if r.get("status") == "done"),
        "run_ids": [r.get("id") for r in runs],
        "tokens": "ids-only",
    }
    dumped = json.dumps(out)
    for needle in DROP_KEYS:
        if needle in dumped:
            raise CheckpointDenied(f"summary contained {needle}")
    return out


def checkpoint_graph(graph: CrewGraph) -> dict[str, Any]:
    return save_checkpoint(graph.index())
