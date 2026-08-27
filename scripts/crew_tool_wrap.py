"""Fail-closed Crew tool wrap. Deep Agents may sit under this, never beside it.

A tool call that cannot show a Cortex allow verdict does not run.
No keys, no leave-machine, no second dag_runner.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class CortexDenied(PermissionError):
    """Crew saw a Cortex refusal. The ticket stays open."""


@dataclass(frozen=True)
class Verdict:
    allowed: bool
    reason: str = ""


class CortexGate(Protocol):
    def check(self, tool: str, payload: dict[str, Any]) -> Verdict: ...

    def execute(self, tool: str, payload: dict[str, Any]) -> Any: ...


def run_tool(gate: CortexGate, tool: str, payload: dict[str, Any]) -> Any:
    """The only Crew write/read path. Parallel runners share this function."""
    if gate is None:
        raise CortexDenied("no Cortex gate")
    verdict = gate.check(tool, payload)
    if not verdict.allowed:
        raise CortexDenied(verdict.reason or "cortex refused")
    return gate.execute(tool, payload)
