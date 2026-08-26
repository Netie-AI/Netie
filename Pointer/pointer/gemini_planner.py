"""Optional Gemini planner for the All Things Agentic hackathon.

Not Cortex. Not imported by `pointer serve`. Fail-closed without a key.
Accepts GEMINI_API_KEY (google-genai docs) or GOOGLE_API_KEY (OpenVault
provider `google`). Pointer does not fetch secrets from OpenVault.
Never emits `shell`. Never sets POINTER_ALLOW_REMOTE.
"""

from __future__ import annotations

import json
import os
from typing import Any

from pointer.protocol import SCHEMA, Intent


class PlannerError(RuntimeError):
    pass


SYSTEM = (
    "You are a planner for a fail-closed laptop daemon. "
    "Reply with JSON only, schema pointer.intent/v1. "
    "source must be local-test. "
    "actions.type may be perceive, move, click, type, hotkey, wait, verify, file_write, file_delete. "
    "Never use shell. Never ask to bind 0.0.0.0 or POINTER_ALLOW_REMOTE. "
    "Keep actions short. Coordinates are integers."
)


def gemini_key_source() -> tuple[str | None, str | None]:
    gem = os.environ.get("GEMINI_API_KEY", "").strip()
    if gem:
        return gem, "GEMINI_API_KEY"
    goog = os.environ.get("GOOGLE_API_KEY", "").strip()
    if goog:
        return goog, "GOOGLE_API_KEY"
    return None, None


def gemini_configured() -> bool:
    return gemini_key_source()[0] is not None


def plan(goal: str, *, model: str | None = None) -> dict[str, Any]:
    text = (goal or "").strip()
    if not text:
        raise PlannerError("goal is required")
    key, _source = gemini_key_source()
    if not key:
        raise PlannerError("GEMINI_API_KEY or GOOGLE_API_KEY missing")
    model_name = model or os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
    raw = _generate(key, model_name, text)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PlannerError(f"Gemini did not return JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise PlannerError("Gemini JSON must be an object")
    data.setdefault("schema", SCHEMA)
    data.setdefault("intent_id", "hackathon-1")
    data.setdefault("source", "local-test")
    data.setdefault("goal", text)
    data["allow_local_act"] = True
    intent = Intent.from_dict(data)
    if any(a.type == "shell" for a in intent.actions):
        raise PlannerError("shell is refused")
    return intent.to_dict()


def _generate(key: str, model: str, goal: str) -> str:
    try:
        from google import genai
    except ImportError as exc:
        raise PlannerError("google-genai is not installed") from exc
    client = genai.Client(api_key=key)
    resp = client.models.generate_content(
        model=model,
        contents=goal,
        config={
            "system_instruction": SYSTEM,
            "response_mime_type": "application/json",
        },
    )
    text = getattr(resp, "text", None)
    if not text:
        raise PlannerError("Gemini returned empty text")
    return text
