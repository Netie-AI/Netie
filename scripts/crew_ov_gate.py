"""OpenVault crew/gate client. Fail closed. Never keep skill bodies.

Contract (OpenVault `docs/patches/openvault-crew-gate.patch` and PR #44 / DR-0012; neither is on OpenVault main yet):

    POST {openvault}/api/crew/gate
      {kind, id, intent, parent_run_id, child_id, deficit}
    -> location + allowed. No skill_body.

The focused patch fail-closes unknown kinds (including `skill` until a registry
row exists). Missing URL, timeout, or a body without allowed=true is a refusal.
Crew does not intercept credentials. The human already put the secret in the vault.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable

from crew_tool_wrap import CortexDenied

DROP_KEYS = frozenset({"skill_body", "prompt", "instructions", "transcript"})


def strip_bodies(obj: Any) -> Any:
    """Token-cheap index: ids and status only. Matches OpenVault strip_skill_bodies."""
    if isinstance(obj, dict):
        return {k: strip_bodies(v) for k, v in obj.items() if k not in DROP_KEYS}
    if isinstance(obj, list):
        return [strip_bodies(x) for x in obj]
    return obj


def has_bodies(obj: Any) -> bool:
    """True if a child payload still carries a skill body or transcript."""
    if isinstance(obj, dict):
        if DROP_KEYS.intersection(obj.keys()):
            return True
        return any(has_bodies(v) for v in obj.values())
    if isinstance(obj, list):
        return any(has_bodies(x) for x in obj)
    return False


@dataclass(frozen=True)
class GateAsk:
    kind: str
    id: str
    intent: str
    parent_run_id: str
    child_id: str
    deficit: str = ""


class OpenVaultCrewGate:
    def __init__(
        self,
        base_url: str | None,
        post: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None,
    ) -> None:
        self.base_url = (base_url or "").rstrip("/")
        self._post = post

    def allow(self, ask: GateAsk) -> dict[str, Any]:
        if not self.base_url:
            raise CortexDenied("no OpenVault crew_gate")
        if self._post is None:
            raise CortexDenied("no OpenVault transport")
        payload = asdict(ask)
        if "skill_body" in payload:
            raise CortexDenied("skill_body must never go to the gate")
        url = f"{self.base_url}/api/crew/gate"
        try:
            raw = self._post(url, payload)
        except Exception as exc:  # transport failure is a refusal
            raise CortexDenied(f"crew_gate unreachable: {exc}") from exc
        body = strip_bodies(raw or {})
        if not isinstance(body, dict):
            raise CortexDenied("crew_gate returned non-object")
        if body.get("allowed") is not True:
            raise CortexDenied(body.get("reason") or "openvault refused")
        return body
