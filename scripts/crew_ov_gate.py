"""OpenVault crew/gate client. Fail closed. Never keep skill bodies.

Contract (OpenVault `docs/patches/openvault-crew-gate.patch` and PR #44 / DR-0012; neither is on OpenVault main yet):

    POST {openvault}/api/crew/gate
      {kind, id, intent, parent_run_id, child_id, deficit}
    -> location + allowed. No skill_body.

The focused patch fail-closes unknown kinds (including `skill` until a registry
row exists). The portable client refuses those kinds *before* POST so a mock
that returns allowed=true cannot greenwash `skill`. Missing URL, timeout, or a
body without allowed=true is a refusal.
Crew does not intercept credentials. The human already put the secret in the vault.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable

from crew_skills import SkillRegistry, register_skill
from crew_tool_wrap import CortexDenied

DROP_KEYS = frozenset({"skill_body", "prompt", "instructions", "transcript"})
# Same set as OpenVault ACCESS_KINDS. `skill` is not registered until a
# registry row exists (openvault-crew-gate.patch).
REGISTERED_KINDS = frozenset(
    {"memory", "api", "component", "runtime", "model", "service"}
)


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


def refuse_crew_gate(
    *,
    kind: str,
    id: str = "",
    skill_body: object | None = None,
    prompt: object | None = None,
    instructions: object | None = None,
    transcript: object | None = None,
    registry: SkillRegistry | None = None,
    skill_ids: list[str] | None = None,
) -> dict[str, str]:
    """OpenVault /api/crew/gate body check. Vault lookup stays in OpenVault."""
    if any(
        value is not None
        for value in (skill_body, prompt, instructions, transcript)
    ):
        raise CortexDenied("skill_body must never go to the gate")
    k = (kind or "").strip()
    sid = (id or "").strip()
    if k == "skill":
        if registry is None and skill_ids:
            registry = SkillRegistry()
            for listed in skill_ids:
                register_skill(registry, str(listed))
        if registry is None or not registry.has(sid):
            raise CortexDenied(f"no skill registered as '{sid}'")
        return {"status": "ok", "kind": k}
    if k not in REGISTERED_KINDS:
        raise CortexDenied(f"no {k or 'kind'} registered as '{id}'")
    return {"status": "ok", "kind": k}


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
        registry: SkillRegistry | None = None,
    ) -> None:
        self.base_url = (base_url or "").rstrip("/")
        self._post = post
        self.registry = registry

    def allow(self, ask: GateAsk) -> dict[str, Any]:
        if not self.base_url:
            raise CortexDenied("no OpenVault crew_gate")
        if self._post is None:
            raise CortexDenied("no OpenVault transport")
        refuse_crew_gate(kind=ask.kind, id=ask.id, registry=self.registry)
        payload = asdict(ask)
        if self.registry is not None:
            payload["skill_ids"] = [row["id"] for row in self.registry.index()]
        if has_bodies(payload):
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
