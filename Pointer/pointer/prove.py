"""Hardware proof artifact. Never includes pair tokens."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def prove_ok(*, after: dict[str, Any], target_x: int, target_y: int, shot_bytes: int) -> bool:
    """Mouse landed AND a real screenshot exists. Tokens never belong here."""
    return (
        after.get("x") == target_x
        and after.get("y") == target_y
        and int(shot_bytes) >= 100
    )


def write_prove(state_dir: Path, payload: dict[str, Any]) -> Path:
    banned = ("pair_token", "approval_token")
    blob = json.dumps(payload)
    for key in banned:
        if key in payload or f'"{key}"' in blob:
            raise ValueError("prove file must not contain tokens")
    state_dir.mkdir(parents=True, exist_ok=True)
    path = state_dir / "PROVE.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return path
