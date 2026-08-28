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
KEY_BASENAMES = frozenset(
    {
        "id_rsa",
        "id_ed25519",
        "id_ecdsa",
        "id_dsa",
        "credentials.json",
        ".netrc",
        ".npmrc",
        ".git-credentials",
        "authorized_keys",
    }
)
KEY_SUFFIXES = frozenset({".pem", ".key", ".p12", ".pfx", ".ppk"})


def _base(path_name: str) -> str:
    return path_name.replace("\\", "/").rsplit("/", 1)[-1].lower()


def _is_secret_path(path_name: str) -> bool:
    base = _base(path_name)
    lower = path_name.replace("\\", "/").lower()
    if base in ENV_BASENAMES or base in KEY_BASENAMES:
        return True
    return any(lower.endswith(suf) for suf in KEY_SUFFIXES)


def persist_key(path_name: str, plaintext: bool) -> None:
    if _is_secret_path(path_name):
        raise SpaceLeaveDenied(f"refuse secret write {path_name}")
    if plaintext:
        raise SpaceLeaveDenied(f"refuse plaintext key write to {path_name}")


def may_preview(
    path_name: str,
    *,
    leave_machine: bool = False,
    ov_allowed: bool = False,
) -> str:
    """Peek-class preview. Secrets stay closed. Cloud/OCR needs OpenVault."""
    if _is_secret_path(path_name):
        raise SpaceLeaveDenied(f"refuse secret preview {path_name}")
    if leave_machine and not ov_allowed:
        raise SpaceLeaveDenied("leave-machine is OpenVault")
    return "preview"


def ocr_cloud(path_name: str, *, ov_allowed: bool, local_chars: int) -> str:
    """Poor local OCR is not a leave-machine grant (Baidu path)."""
    if local_chars < 20 and not ov_allowed:
        raise SpaceLeaveDenied("poor local OCR is not a leave-machine grant")
    may_preview(path_name, leave_machine=True, ov_allowed=ov_allowed)
    return "cloud"


def resolve_login(*, openvault_ok: bool, scan_local_vault: bool) -> str:
    if openvault_ok:
        return "openvault"
    if scan_local_vault:
        raise SpaceLeaveDenied("no local vault scan")
    raise SpaceLeaveDenied("openvault login missing")
