"""OpenWork-shaped capability MCP. Study the idea. Do not vendor ee/.

search_capabilities lists granted names only (ids, no prompts).
execute_capability runs one granted name through Cortex wrap.
Den-like policy: ungranted / Deep Agents builtin / billing-bypass /
skill_body refuse. Leave-machine names need OpenVault allow.

Not a second dag_runner. Not OpenWork's desktop.
"""

from __future__ import annotations

from typing import Any

from crew_budget import TokenBudget
from crew_ov_gate import GateAsk, OpenVaultCrewGate, has_bodies
from crew_parallel import Job, JobResult, MAX_IN_FLIGHT, run_batch
from crew_tool_wrap import CortexDenied, CortexGate, DEEPAGENTS_DIRECT, Verdict, run_tool
from seat_router import BYPASS_SEATS

LEAVE_CAPS = frozenset(
    {"open_url", "launch_app", "browser_navigate", "ocr_cloud", "leave"}
)


def _leave_machine(
    cap: str,
    *,
    ov_allowed: bool,
    ov: OpenVaultCrewGate | None,
    parent_run_id: str,
    child_id: str,
) -> None:
    """Boolean ov_allowed is the portable stand-in. `ov` POSTs crew/gate."""
    if cap not in LEAVE_CAPS:
        return
    if ov is not None:
        pid = (parent_run_id or "").strip()
        cid = (child_id or "").strip()
        if not pid or not cid:
            raise CortexDenied("leave-machine needs parent and child run ids")
        ov.allow(
            GateAsk(
                kind="service",
                id=cap,
                intent="leave",
                parent_run_id=pid,
                child_id=cid,
            )
        )
        return
    if not ov_allowed:
        raise CortexDenied("leave-machine is OpenVault")


def search_capabilities(granted: frozenset[str] | list[str] | tuple[str, ...]) -> list[str]:
    """Ids the session may call. Builtins and billing-bypass never list."""
    names: list[str] = []
    for raw in granted or []:
        name = (raw or "").strip()
        if not name:
            continue
        if name in DEEPAGENTS_DIRECT or name in BYPASS_SEATS:
            continue
        names.append(name)
    return sorted(set(names))


def execute_capability(
    gate: CortexGate,
    name: str,
    payload: dict[str, Any],
    *,
    granted: frozenset[str] | list[str] | tuple[str, ...],
    ov_allowed: bool = False,
    ov: OpenVaultCrewGate | None = None,
    parent_run_id: str = "",
    child_id: str = "",
    budget: TokenBudget | None = None,
) -> Any:
    """One granted capability through Cortex. Ungranted does not execute."""
    cap = (name or "").strip()
    if not cap:
        raise CortexDenied("empty capability")
    if cap in DEEPAGENTS_DIRECT:
        raise CortexDenied(f"Deep Agents builtin {cap} is not a Crew tool")
    if cap in BYPASS_SEATS:
        raise CortexDenied("billing-bypass product")
    allowed = search_capabilities(granted)
    if cap not in allowed:
        raise CortexDenied(f"capability {cap} not granted")
    if has_bodies(payload or {}):
        raise CortexDenied("skill_body must never go to a child job")
    _leave_machine(
        cap,
        ov_allowed=ov_allowed,
        ov=ov,
        parent_run_id=parent_run_id,
        child_id=child_id,
    )
    if budget is None:
        raise CortexDenied("token budget required; Deep Agents default is unbounded spend")
    return run_tool(gate, cap, payload, budget=budget)


class GrantedGate:
    """Den-like policy in front of Cortex. Ungranted names never execute."""

    def __init__(
        self,
        inner: CortexGate,
        granted: frozenset[str] | list[str] | tuple[str, ...],
        *,
        ov_allowed: bool = False,
        ov: OpenVaultCrewGate | None = None,
        parent_run_id: str = "",
        child_id: str = "",
    ) -> None:
        self.inner = inner
        self.granted = granted
        self.ov_allowed = ov_allowed
        self.ov = ov
        self.parent_run_id = parent_run_id
        self.child_id = child_id

    def check(self, tool: str, payload: dict[str, Any]) -> Verdict:
        cap = (tool or "").strip()
        if cap in BYPASS_SEATS:
            return Verdict(allowed=False, reason="billing-bypass product")
        if cap not in search_capabilities(self.granted):
            return Verdict(allowed=False, reason=f"capability {cap} not granted")
        try:
            _leave_machine(
                cap,
                ov_allowed=self.ov_allowed,
                ov=self.ov,
                parent_run_id=self.parent_run_id,
                child_id=self.child_id or cap,
            )
        except CortexDenied as exc:
            return Verdict(allowed=False, reason=str(exc))
        return self.inner.check(tool, payload)

    def execute(self, tool: str, payload: dict[str, Any]) -> Any:
        return self.inner.execute(tool, payload)


def load_den(source: str) -> dict[str, str]:
    """OpenWork ee/ is FSL. Crew's Den-like policy is this module."""
    blob = (source or "").strip().lower().replace("\\", "/")
    padded = f"/{blob.strip('/')}/"
    if (
        "openwork-ee" in blob
        or "openwork/ee" in blob
        or "/ee/" in padded
        or blob.rstrip("/").endswith("/ee")
        or blob in {"ee", "ee/"}
    ):
        raise CortexDenied("do not vendor OpenWork ee/")
    raise CortexDenied("Den-like policy is search_capabilities, not a second desktop")


def execute_capabilities(
    gate: CortexGate,
    jobs: list[Job],
    *,
    granted: frozenset[str] | list[str] | tuple[str, ...],
    ov_allowed: bool = False,
    ov: OpenVaultCrewGate | None = None,
    parent_run_id: str = "",
    max_in_flight: int = MAX_IN_FLIGHT,
    budget: TokenBudget | None = None,
) -> list[JobResult]:
    """Granted capabilities in parallel. Cap-2. Ungranted jobs fail closed."""
    if budget is None:
        raise CortexDenied("token budget required; Deep Agents default is unbounded spend")
    wrapped = GrantedGate(
        gate,
        granted,
        ov_allowed=ov_allowed,
        ov=ov,
        parent_run_id=parent_run_id,
    )
    return run_batch(wrapped, jobs, max_in_flight=max_in_flight, budget=budget)
