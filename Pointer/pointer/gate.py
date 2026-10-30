"""Fail-closed gate. Irreversible work needs approval. Kill switch wins."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .protocol import REMOTE_NEEDS_APPROVAL, Intent


@dataclass
class GateDecision:
    allowed: bool
    verdict: str
    reason: str
    degraded: list[str]


class Gate:
    def __init__(
        self,
        *,
        state_dir: Path,
        pair_token: str,
        cortex_reachable: bool,
        approval_token: str,
    ) -> None:
        self.state_dir = state_dir
        self.pair_token = pair_token
        self.cortex_reachable = cortex_reachable
        self.approval_token = approval_token

    def kill_path(self) -> Path:
        return self.state_dir / "KILL"

    def killed(self) -> bool:
        return self.kill_path().exists()

    def arm_kill(self) -> None:
        self.kill_path().write_text("killed\n", encoding="utf-8")

    def clear_kill(self) -> None:
        p = self.kill_path()
        if p.exists():
            p.unlink()

    def decide(self, intent: Intent, *, bearer: str | None, bind_is_loopback: bool) -> GateDecision:
        degraded: list[str] = []
        if self.killed():
            return GateDecision(False, "refused", "kill switch is armed", degraded)

        if intent.source == "remote-paired":
            if not bearer or bearer != self.pair_token:
                return GateDecision(False, "refused", "remote intent requires the pair token", degraded)
            if not bind_is_loopback and bearer != self.pair_token:
                return GateDecision(False, "refused", "pair token mismatch", degraded)

        if intent.source == "remote-paired":
            if any(a.type in REMOTE_NEEDS_APPROVAL for a in intent.actions):
                if intent.approval_token != self.approval_token:
                    return GateDecision(
                        False,
                        "needs_approval",
                        "remote act needs the approval token; perceive-only is allowed without it",
                        degraded,
                    )

        if intent.irreversible or any(a.is_irreversible() for a in intent.actions):
            if intent.approval_token != self.approval_token:
                return GateDecision(
                    False,
                    "needs_approval",
                    "irreversible actions need the approval token",
                    degraded,
                )

        needs_act = any(a.type != "perceive" for a in intent.actions)
        if needs_act and not self.cortex_reachable:
            if intent.source == "local-test" or intent.allow_local_act:
                degraded.append("local_act_without_cortex")
            else:
                return GateDecision(
                    False,
                    "refused",
                    "Cortex is unreachable; Pointer will not act without a plan (set allow_local_act for an explicit degraded local test)",
                    degraded,
                )

        if intent.source == "cortex" and not self.cortex_reachable:
            return GateDecision(False, "refused", "source=cortex but Cortex is unreachable", degraded)

        return GateDecision(True, "executed", "gate open", degraded)
