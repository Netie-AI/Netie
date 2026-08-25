from __future__ import annotations

from pathlib import Path

from netie_exposure.crew import ENGINE, NORTH_STAR_LINKEDIN, ROLES, SOCIAL_POSTING, yaml_mentions_roles


def test_crew_contract() -> None:
    assert ENGINE == "cortex"
    assert SOCIAL_POSTING == "off"
    assert NORTH_STAR_LINKEDIN == 100_000
    yaml_path = Path(__file__).resolve().parents[1] / "crew.yaml"
    text = yaml_path.read_text(encoding="utf-8")
    assert yaml_mentions_roles(text) == []
    assert "social_posting: off" in text
    assert "engine: cortex" in text
