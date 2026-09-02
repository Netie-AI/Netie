"""Skill registry for long-term Crew calling. Ids only. No skill_body.

OpenVault ACCESS_KINDS still omit `skill` until a row exists here.
Gastown/Deep Agents skill files stay out of the blob. Netie-KB is the index.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from crew_tool_wrap import CortexDenied
from kb_lookup import KbDenied, lookup

DROP_KEYS = frozenset({"skill_body", "prompt", "instructions", "transcript", "body"})


class SkillDenied(CortexDenied):
    """No registry row, or a body tried to ride the register call."""


@dataclass
class SkillRegistry:
    """Ids + source. Never the skill text."""

    rows: dict[str, str] = field(default_factory=dict)

    def register(self, skill_id: str, *, source: str = "netie-kb") -> str:
        sid = (skill_id or "").strip()
        src = (source or "").strip()
        if not sid:
            raise SkillDenied("skill id missing")
        if not src:
            raise SkillDenied("skill source missing")
        if any(k in sid.lower() or k in src.lower() for k in DROP_KEYS):
            raise SkillDenied("skill_body must never go to the registry")
        self.rows[sid] = src
        return sid

    def has(self, skill_id: str) -> bool:
        return (skill_id or "").strip() in self.rows

    def index(self) -> list[dict[str, str]]:
        return [{"id": k, "source": v} for k, v in sorted(self.rows.items())]


def register_skill(
    registry: SkillRegistry,
    skill_id: str,
    *,
    source: str = "netie-kb",
    skill_body: object | None = None,
) -> str:
    if skill_body is not None:
        raise SkillDenied("skill_body must never go to the registry")
    return registry.register(skill_id, source=source)


def register_from_kb(
    registry: SkillRegistry,
    rows: list[dict],
    skill_id: str,
    *,
    skill_body: object | None = None,
) -> str:
    """Mint a Crew skill id from a Netie-KB index row. Never a body."""
    if skill_body is not None:
        raise SkillDenied("skill_body must never go to the registry")
    try:
        brief = lookup(rows, skill_id)
    except KbDenied as exc:
        raise SkillDenied(str(exc)) from exc
    if str(brief.get("kind") or "").strip().lower() != "skill":
        raise SkillDenied("not a skill")
    return register_skill(
        registry, brief["id"], source=str(brief.get("source") or "netie-kb")
    )


def register_index(
    registry: SkillRegistry,
    rows: list[dict],
    *,
    skill_body: object | None = None,
) -> list[str]:
    """Register every skill id from a Netie-KB dump. Skip corpus kinds. Never a body."""
    if skill_body is not None:
        raise SkillDenied("skill_body must never go to the registry")
    skills: list[dict] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        kind = str(row.get("kind") or "").strip().lower()
        if kind != "skill":
            continue
        if row.get("body") is not None or row.get("skill_body") is not None:
            raise SkillDenied("skill_body must never go to the registry")
        skills.append(row)
    return [
        register_from_kb(registry, rows, str(row.get("id") or "")) for row in skills
    ]
