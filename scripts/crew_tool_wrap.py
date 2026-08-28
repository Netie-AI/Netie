"""Fail-closed Crew tool wrap. Deep Agents may sit under this, never beside it.

A tool call that cannot show a Cortex allow verdict does not run.
No keys, no leave-machine, no second dag_runner.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable
from typing import Any, Protocol

# Same write as Cortex path, plus the two DMS writes that are not invocable yet.
HITL_WRITES = frozenset({"export_pptx", "amend.apply", "call_action"})
# Deep Agents 0.7.9 builtins. Filesystem/shell skip Cortex. `task` is ungoverned
# fan-out (use crew_parallel cap-2). `write_todos` stores prompt text (use factory index).
# 0.7 also ships glob / grep / delete on FilesystemMiddleware.
DEEPAGENTS_DIRECT = frozenset(
    {
        "ls",
        "read_file",
        "write_file",
        "edit_file",
        "delete",
        "glob",
        "grep",
        "execute",
        "bash",
        "shell",
        "task",
        "write_todos",
    }
)


class CortexDenied(PermissionError):
    """Crew saw a Cortex refusal. The ticket stays open."""


@dataclass(frozen=True)
class Verdict:
    allowed: bool
    reason: str = ""


class CortexGate(Protocol):
    def check(self, tool: str, payload: dict[str, Any]) -> Verdict: ...

    def execute(self, tool: str, payload: dict[str, Any]) -> Any: ...


def prepare_tool(
    gate: CortexGate, tool: str, payload: dict[str, Any]
) -> tuple[str, dict[str, Any]]:
    """HITL + builtin + Cortex check. Does not execute and does not spend budget."""
    if gate is None:
        raise CortexDenied("no Cortex gate")
    name = (tool or "").strip()
    if not name:
        raise CortexDenied("empty tool name")
    if name in DEEPAGENTS_DIRECT:
        raise CortexDenied(f"Deep Agents builtin {name} is not a Crew tool")
    body = dict(payload or {})
    confirm = body.pop("operator_confirm", None)
    if name in HITL_WRITES and confirm is not True:
        raise CortexDenied("HITL: write needs operator_confirm")
    verdict = gate.check(name, body)
    if not verdict.allowed:
        raise CortexDenied(verdict.reason or "cortex refused")
    return name, body


def run_tool(gate: CortexGate, tool: str, payload: dict[str, Any]) -> Any:
    """The only Crew write/read path. Parallel runners share this function.

    Known writes need operator_confirm=True (HITL). Deep Agents default is
    trust-the-LLM; this is the opposite. Refusals do not execute.
    """
    name, body = prepare_tool(gate, tool, payload)
    return gate.execute(name, body)


def wrap_deepagents_tools(
    gate: CortexGate, names: list[str]
) -> dict[str, Callable[..., Any]]:
    """Deep Agents (MIT) sits under this wrap. Their default is trust-the-LLM.

    Empty or blank names refuse. An empty wrap would let create_deep_agent
    run its built-in tools ungoverned. Known writes still need
    operator_confirm=True at call time (HITL).
    """
    if gate is None:
        raise CortexDenied("no Cortex gate")
    cleaned: list[str] = []
    seen: set[str] = set()
    for raw in names or []:
        name = (raw or "").strip()
        if not name:
            raise CortexDenied("empty tool name")
        if name in DEEPAGENTS_DIRECT:
            raise CortexDenied(f"Deep Agents builtin {name} is not a Crew tool")
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
