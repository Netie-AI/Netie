"""Fail-closed Crew tool wrap. Deep Agents may sit under this, never beside it.

A tool call that cannot show a Cortex allow verdict does not run.
No keys, no leave-machine, no second dag_runner.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable
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


def wrap_deepagents_tools(
    gate: CortexGate, names: list[str]
) -> dict[str, Callable[..., Any]]:
    """Deep Agents (MIT) sits under this wrap. Their default is trust-the-LLM.

    Empty or blank names refuse. An empty wrap would let create_deep_agent
    run its built-in tools ungoverned.
    """
    if gate is None:
        raise CortexDenied("no Cortex gate")
    cleaned: list[str] = []
    seen: set[str] = set()
    for raw in names or []:
        name = (raw or "").strip()
        if not name:
            raise CortexDenied("empty tool name")
        if name in seen:
            continue
        seen.add(name)
        cleaned.append(name)
    if not cleaned:
        raise CortexDenied("no tools to wrap; Deep Agents default is trust-the-LLM")

    def bind(tool: str) -> Callable[..., Any]:
        def tool_fn(**payload: Any) -> Any:
            return run_tool(gate, tool, payload)

        tool_fn.__name__ = tool
        return tool_fn

    return {name: bind(name) for name in cleaned}


def require_wrapped(
    requested: list[str],
    wrapped: dict[str, Callable[..., Any]],
) -> list[Callable[..., Any]]:
    """create_deep_agent may only receive callables already under the wrap.

    Extra names that are not in `wrapped` refuse. Empty requested refuses
    (Deep Agents built-ins would otherwise run ungoverned).
    """
    req = [(n or "").strip() for n in (requested or [])]
    if not req or any(not n for n in req):
        raise CortexDenied("no tools to wrap; Deep Agents default is trust-the-LLM")
    missing = [n for n in req if n not in wrapped]
    if missing:
        raise CortexDenied("unwrapped tools: " + ", ".join(missing))
    return [wrapped[n] for n in req]
