"""NVIDIA Switchyard sits behind OpenVault. FreeRoute is not that job.

`NVIDIA-AI-Blueprints/llm-router` (Apache-2.0) is deprecated for NeMo
Switchyard. Switchyard classifies task/complexity (`llm_classifier` /
`stage_router`) and serves. FreeRoute classifies cost/quota/health and
picks a key. Host Switchyard as a leave-machine dependency. Do not vendor
the blueprint. Do not rewrite Triton. Score stays 2/10 until that host
exists. This module is the gate, not a serving engine.
"""

from __future__ import annotations

from crew_ov_gate import GateAsk, OpenVaultCrewGate
from crew_tool_wrap import CortexDenied

VENDOR_TREES = frozenset(
    {
        "llm-router",
        "llm_router",
        "nvidia-ai-blueprints/llm-router",
        "nvidia_llm_router",
    }
)
NOT_SWITCHYARD = frozenset(
    {
        "freeroute",
        "openvault",
        "cost-optimized",
        "least-used",
        "fill-first",
    }
)


class SwitchyardDenied(PermissionError):
    """Not Switchyard, or Switchyard without the leave-machine gate."""


def host_switchyard(
    *,
    ov_leave: bool,
    vendor: str | None = None,
    rewrite_triton: bool = False,
    claim: str | None = None,
    ov: OpenVaultCrewGate | None = None,
    parent_run_id: str = "",
    child_id: str = "",
) -> dict[str, str]:
    """Depend Apache-2.0 Switchyard behind OpenVault. Never rebrand FreeRoute."""
    tree = (vendor or "").strip().lower()
    if tree in VENDOR_TREES:
        raise SwitchyardDenied("do not vendor NVIDIA-AI-Blueprints/llm-router")
    if rewrite_triton:
        raise SwitchyardDenied("do not rewrite Triton")
    who = (claim or "").strip().lower()
    if who in NOT_SWITCHYARD:
        raise SwitchyardDenied(
            "FreeRoute is cost/quota/health key pick, not Switchyard"
        )
    if ov is not None:
        pid = (parent_run_id or "").strip()
        cid = (child_id or "").strip()
        if not pid or not cid:
            raise SwitchyardDenied("leave-machine needs parent and child run ids")
        try:
            ov.allow(
                GateAsk(
                    kind="service",
                    id="switchyard",
                    intent="leave",
                    parent_run_id=pid,
                    child_id=cid,
                )
            )
        except CortexDenied as exc:
            raise SwitchyardDenied(str(exc)) from exc
    elif not ov_leave:
        raise SwitchyardDenied("Switchyard leave-machine is OpenVault")
    return {
        "status": "hosted",
        "via": "openvault",
        "job": "llm_classifier",
        "score": "2/10",
        "license": "Apache-2.0",
    }
