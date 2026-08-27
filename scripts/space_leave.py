"""Space leave-machine contract. OpenVault decides. Direct provider POST is a bug.

TAS-SPACE (2026-08-02): AiService posts document text to Groq/Gemini without a gate;
Baidu OCR uploads on poor local quality; keys land in plaintext user.env; login
falls back to scanning a local vault. This module is the failing test those
callers must pass. Space repo is still 404 here.
"""

from __future__ import annotations

from typing import Any

from crew_ov_gate import GateAsk, OpenVaultCrewGate
from crew_tool_wrap import CortexDenied


class SpaceLeaveDenied(PermissionError):
    """Document stays on the machine. Ticket/UI must show the refusal."""


def leave(
    ov: OpenVaultCrewGate,
    *,
    intent: str,
    parent_run_id: str,
    child_id: str,
    deficit: str,
) -> dict[str, Any]:
    """intent is leave (model/OCR upload) or invoke. Missing allow is a refusal."""
    if intent not in {"leave", "invoke"}:
        raise SpaceLeaveDenied(f"bad intent {intent}")
    try:
        return ov.allow(
            GateAsk(
                kind="service",
                id="space.ai",
                intent=intent,
                parent_run_id=parent_run_id,
                child_id=child_id,
                deficit=deficit,
            )
        )
    except CortexDenied as exc:
        raise SpaceLeaveDenied(str(exc)) from exc


ENV_BASENAMES = frozenset({"user.env", ".env", "env.local"})


def persist_key(path_name: str, plaintext: bool) -> None:
    base = path_name.replace("\\", "/").rsplit("/", 1)[-1].lower()
    if base in ENV_BASENAMES:
        raise SpaceLeaveDenied(f"refuse env file {path_name}")
    if plaintext:
        raise SpaceLeaveDenied(f"refuse plaintext key write to {path_name}")


def resolve_login(*, openvault_ok: bool, scan_local_vault: bool) -> str:
    if openvault_ok:
        return "openvault"
    if scan_local_vault:
        raise SpaceLeaveDenied("no local vault scan")
    raise SpaceLeaveDenied("openvault login missing")
