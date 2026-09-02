"""Netie-KB is the skill index. Ids and titles only. Never skill_body.

R-0016: distilled skills live in Netie-KB. Crew register_skill takes the id.
kb_show / GET /item must not dump a skill markdown body into a child job.
Rules / workflows / findings / attacks may still show corpus text.
"""

from __future__ import annotations

from typing import Any

DROP_KEYS = frozenset({"skill_body", "prompt", "instructions", "transcript"})


class KbDenied(PermissionError):
    """Skill body tried to leave the index, or the id is missing."""


def show_brief(
    meta: dict[str, Any],
    *,
    body: str | None = None,
    source: str = "netie-kb",
) -> dict[str, Any]:
    """Index row. kind=skill refuses a body. Corpus kinds may keep text."""
    kind = str(meta.get("kind") or "").strip().lower()
    sid = str(meta.get("id") or "").strip()
    title = str(meta.get("title") or "").strip()
    if not sid:
        raise KbDenied("skill id missing")
    blob = f"{sid} {title} {source}".lower()
    if any(k in blob for k in DROP_KEYS):
        raise KbDenied("skill_body must never go to the registry")
    if kind == "skill" and body is not None:
        raise KbDenied("skill_body must never leave the index")
    out: dict[str, Any] = {
        "id": sid,
        "kind": kind or "unknown",
        "title": title,
        "status": str(meta.get("status") or "").strip() or "unknown",
        "source": source,
    }
    tags = meta.get("tags")
    if isinstance(tags, list):
        out["tags"] = [str(t) for t in tags if str(t).strip()]
    return out


def lookup(
    rows: list[dict[str, Any]],
    skill_id: str,
    *,
    source: str = "netie-kb",
) -> dict[str, Any]:
    want = (skill_id or "").strip()
    if not want:
        raise KbDenied("skill id missing")
    for row in rows:
        meta = dict(row)
        if str(meta.get("id") or "").strip() == want:
            return show_brief(meta, body=meta.get("body"), source=source)
    raise KbDenied(f"not found: {want}")


def list_briefs(
    rows: list[dict[str, Any]],
    *,
    kind: str | None = None,
    source: str = "netie-kb",
) -> list[dict[str, Any]]:
    """Catalog. Skills never carry a body even if the source row had one.

    lookup / register_from_kb still refuse a skill row that carries a body.
    Crew that wants ids from a dump with markdown calls this first, then
    register_index.
    """
    want = (kind or "").strip().lower() or None
    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        meta = dict(row)
        k = str(meta.get("kind") or "").strip().lower()
        if want and k != want:
            continue
        meta.pop("body", None)
        meta.pop("skill_body", None)
        out.append(show_brief(meta, body=None, source=source))
    return out
