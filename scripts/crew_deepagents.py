"""Depend Deep Agents (MIT) under the wrap. Never beside it.

create_deep_agent(tools=...) is additive: filesystem / execute / task stay
on unless a HarnessProfile excludes them. This module is the only legal
factory: wrap first, exclude builtins, no skills/memory/subagents, no
transcript checkpointer.

Do not vendor the deepagents tree. `pip install deepagents==0.7.9`.
"""

from __future__ import annotations

from typing import Any, Callable

from crew_tool_wrap import CortexDenied, CortexGate, DEEPAGENTS_DIRECT, require_wrapped, wrap_deepagents_tools

FORBIDDEN_FACTORY_KEYS = frozenset({"skills", "memory", "subagents", "store"})


def _model_key(model: Any) -> str:
    spec = (model if isinstance(model, str) else "") or ""
    spec = spec.strip()
    if not spec or ":" not in spec:
        raise CortexDenied("model spec required so HarnessProfile excluded_tools apply")
    return spec


def crew_harness_profile() -> Any:
    """Profile that strips Deep Agents builtins. Register under the model key."""
    try:
        from deepagents import GeneralPurposeSubagentProfile, HarnessProfile
    except ImportError as exc:
        raise CortexDenied("deepagents not installed") from exc
    return HarnessProfile(
        excluded_tools=frozenset(DEEPAGENTS_DIRECT),
        general_purpose_subagent=GeneralPurposeSubagentProfile(enabled=False),
    )


def bind_kwargs(
    gate: CortexGate,
    names: list[str],
    *,
    model: Any,
) -> dict[str, Any]:
    """Kwargs create_deep_agent must receive. Extra harness knobs refuse."""
    tools = require_wrapped(names, wrap_deepagents_tools(gate, names))
    _model_key(model)
    return {
        "model": model,
        "tools": tools,
        "subagents": None,
        "skills": None,
        "memory": None,
        "checkpointer": False,
    }


def bind_deep_agent(
    gate: CortexGate,
    names: list[str],
    *,
    model: Any,
    factory: Callable[..., Any] | None = None,
    register: Callable[[str, Any], None] | None = None,
    extra: dict[str, Any] | None = None,
) -> Any:
    """The only create_deep_agent call site. Builtins stay excluded."""
    bag = dict(extra or {})
    leak = FORBIDDEN_FACTORY_KEYS.intersection(bag)
    if leak:
        name = sorted(leak)[0]
        raise CortexDenied(f"{name} is not a Crew factory knob")
    kwargs = bind_kwargs(gate, names, model=model)
    spec = _model_key(model)
    if factory is None:
        try:
            from deepagents import create_deep_agent, register_harness_profile
        except ImportError as exc:
            raise CortexDenied("deepagents not installed") from exc
        factory = create_deep_agent
        register = register_harness_profile
    if register is not None:
        profile = crew_harness_profile()
        register(spec, profile)
        register(spec.split(":", 1)[0], profile)
    return factory(**kwargs)
