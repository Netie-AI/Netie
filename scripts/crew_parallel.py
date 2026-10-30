"""Capped parallel Crew runners. Every job still goes through prepare_tool.

WIP law: in-flight is at most 2. Asking for more refuses unbounded spawn.
A batch without TokenBudget refuses unbounded spend. Refused jobs
(HITL, builtins, skill_body, Cortex deny) do not spend budget.
Leave-machine jobs POST skill ids via ov=; Cortex tools never hit
refuse_crew_gate. This is not a second engine and not infinite subagents.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any

from crew_budget import BudgetDenied, TokenBudget, estimate_tokens
from crew_ledger import HashLedger
from crew_ov_gate import OpenVaultCrewGate, has_bodies, strip_bodies
from crew_tool_wrap import CortexDenied, CortexGate, prepare_tool

MAX_IN_FLIGHT = 2


@dataclass(frozen=True)
class Job:
    id: str
    tool: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class JobResult:
    id: str
    status: str
    detail: str
    output: Any = None


def _one(
    gate: CortexGate,
    job: Job,
    budget: TokenBudget,
    ledger: HashLedger | None,
    ov: OpenVaultCrewGate | None,
    ov_allowed: bool,
    parent_run_id: str,
) -> JobResult:
    try:
        if has_bodies(job.payload):
            raise CortexDenied("skill_body must never go to a child job")
        from crew_capabilities import LEAVE_CAPS, _leave_machine

        name = (job.tool or "").strip()
        if name in LEAVE_CAPS:
            _leave_machine(
                name,
                ov_allowed=ov_allowed,
                ov=ov,
                parent_run_id=parent_run_id,
                child_id=(job.id or name).strip(),
            )
        name, body = prepare_tool(gate, job.tool, job.payload)
        budget.charge(estimate_tokens(strip_bodies(body)))
        out = gate.execute(name, body)
        result = JobResult(id=job.id, status="DONE", detail="ok", output=out)
    except (CortexDenied, BudgetDenied) as exc:
        result = JobResult(id=job.id, status="FAILED", detail=str(exc))
    if ledger is not None:
        ledger.append({"id": result.id, "status": result.status, "detail": result.detail})
    return result


def run_batch(
    gate: CortexGate,
    jobs: list[Job],
    *,
    max_in_flight: int = MAX_IN_FLIGHT,
    budget: TokenBudget | None = None,
    ledger: HashLedger | None = None,
    ov: OpenVaultCrewGate | None = None,
    ov_allowed: bool = False,
    parent_run_id: str = "",
) -> list[JobResult]:
    if max_in_flight < 1:
        raise ValueError("max_in_flight must be >= 1")
    if max_in_flight > MAX_IN_FLIGHT:
        raise ValueError(
            "max_in_flight > 2 refuses unbounded spawn; WIP law"
        )
    if budget is None:
        raise CortexDenied(
            "token budget required; Deep Agents default is unbounded spend"
        )
    if not jobs:
        return []
    by_id: dict[str, JobResult] = {}
    with ThreadPoolExecutor(max_workers=max_in_flight) as pool:
        futs = {
            pool.submit(
                _one, gate, job, budget, ledger, ov, ov_allowed, parent_run_id
            ): job.id
            for job in jobs
        }
        for fut in as_completed(futs):
            result = fut.result()
            by_id[result.id] = result
    return [by_id[j.id] for j in jobs]
