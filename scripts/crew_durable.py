"""Long-term Crew calling: ids-only disk, prompts from tickets not the blob.

Gastown/OpenWork/Deep Agents MemorySaver would persist the conversation.
Crew resumes run ids after process death and rebinds work from GitHub/Factory.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from crew_checkpoint import CheckpointDenied, checkpoint_graph, load_checkpoint
from crew_runs import CrewGraph
from crew_skills import SkillRegistry, register_skill


def persist(
    path: str | Path,
    graph: CrewGraph,
    registry: SkillRegistry | None = None,
) -> dict[str, Any]:
    blob = checkpoint_graph(graph, registry)
    Path(path).write_text(json.dumps(blob), encoding="utf-8")
    return blob


def load_disk(path: str | Path) -> dict[str, Any]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return load_checkpoint(raw)


def resume(
    graph: CrewGraph,
    blob: dict[str, Any],
    *,
    tickets: dict[str, str],
    registry: SkillRegistry | None = None,
) -> CrewGraph:
    """Rebuild open ids. `tickets` is ticket_id -> deficit from source of truth."""
    clean = load_checkpoint(blob)
    dumped = json.dumps(clean)
    if "prompt" in dumped or "transcript" in dumped or "skill_body" in dumped:
        raise CheckpointDenied("resume blob leaked a body")
    if registry is not None:
        for row in clean.get("skills") or []:
            if not isinstance(row, dict):
                continue
            register_skill(
                registry,
                str(row.get("id") or ""),
                source=str(row.get("source") or "netie-kb"),
            )
    parents = [
        r
        for r in clean.get("runs") or []
        if isinstance(r, dict) and not r.get("parent_id")
    ]
    children = [
        r
        for r in clean.get("runs") or []
        if isinstance(r, dict) and r.get("parent_id")
    ]
    for row in parents:
        if row.get("status") != "open":
            continue
        rid = row.get("id")
        tid = row.get("ticket_id")
        if not rid or not tid:
            raise CheckpointDenied("resume missing parent ids")
        graph.open_parent(str(rid), str(tid))
    for row in children:
        if row.get("status") != "open":
            continue
        tid = str(row.get("ticket_id") or "")
        deficit = (tickets.get(tid) or "").strip()
        if not deficit:
            raise CheckpointDenied("resume needs ticket source, not checkpoint prompt")
        graph.spawn_child(
            parent_id=str(row["parent_id"]),
            child_id=str(row["id"]),
            deficit=deficit,
        )
    return graph
