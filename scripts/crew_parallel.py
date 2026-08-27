"""Capped parallel Crew runners. Every job still goes through run_tool.

Default in-flight is 2 (WIP law). Raising it is a config, not a second engine.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any

from crew_budget import BudgetDenied, TokenBudget, estimate_tokens
from crew_ledger import HashLedger
from crew_tool_wrap import CortexDenied, CortexGate, run_tool

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
    budget: TokenBudget | None,
    ledger: HashLedger | None,
) -> JobResult:
    try:
        if gate is None:
            raise CortexDenied("no Cortex gate")
        verdict = gate.check(job.tool, job.payload)
        if not verdict.allowed:
            raise CortexDenied(verdict.reason or "cortex refused")
        if budget is not None:
            budget.charge(estimate_tokens(job.payload))
        out = run_tool(gate, job.tool, job.payload)
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
) -> list[JobResult]:
    if max_in_flight < 1:
        raise ValueError("max_in_flight must be >= 1")
    if not jobs:
        return []
    by_id: dict[str, JobResult] = {}
    with ThreadPoolExecutor(max_workers=max_in_flight) as pool:
        futs = {
            pool.submit(_one, gate, job, budget, ledger): job.id for job in jobs
        }
        for fut in as_completed(futs):
            result = fut.result()
            by_id[result.id] = result
    return [by_id[j.id] for j in jobs]
