"""Crew roster. Cortex is the engine; these are roles, not a second loop."""

from __future__ import annotations

from pathlib import Path

CREW_YAML = Path(__file__).resolve().parents[2] / "crew.yaml"

ROLES = (
    "vanguard",
    "cortex",
    "closer",
    "linkedin",
    "reddit",
    "github",
    "news",
    "hire",
    "invite",
)

ENGINE = "cortex"
SOCIAL_POSTING = "off"
NORTH_STAR_LINKEDIN = 100_000


def summary() -> dict[str, object]:
    return {
        "engine": ENGINE,
        "social_posting": SOCIAL_POSTING,
        "roles": list(ROLES),
        "pattern": ["vanguard", "cortex", "closer"],
        "north_star": {"linkedin_followers": NORTH_STAR_LINKEDIN, "organic": True},
        "fan_out": "channel_specialists_only",
    }


def yaml_mentions_roles(text: str) -> list[str]:
    missing = [r for r in ROLES if r not in text]
    return missing
