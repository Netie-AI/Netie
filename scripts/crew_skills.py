"""Skill registry for long-term Crew calling. Ids only. No skill_body.

OpenVault ACCESS_KINDS still omit `skill` until a row exists here.
Gastown/Deep Agents skill files stay out of the blob. Netie-KB is the index.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from crew_tool_wrap import CortexDenied

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
