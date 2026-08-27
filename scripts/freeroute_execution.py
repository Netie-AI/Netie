"""The last 4 OmniRoute user-facing names are execution shapes, not sorts.

OmniRoute `ROUTING_STRATEGY_VALUES` has 19 names. FreeRoute's `apply_strategy`
ports 15 of them as target permutations. These four are *not* permutations:

- fusion: fan the prompt to a panel, then a judge synthesizes (or answer
  directly on 1 model / tool-bearing requests).
- pipeline: run steps in order; thread output into the next; return only the
  last response. Intermediate failure fails the chain.
- context-relay: first available target; skip unavailable; persist a handoff
  blob when quota is in the warning band. No Codex quota fetch here.
- auto: meta-router. Caller must resolve to a *sort* strategy. We do not port
  OmniRoute autoCombo scoring / mode packs.

`apply_strategy` must refuse these four. Call `plan_*` / `run_*` instead.
quota-share stays internal and is not ported.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal
import json

SORT_STRATEGIES: tuple[str, ...] = (
    "priority",
    "weighted",
    "fill-first",
    "round-robin",
    "p2c",
    "random",
    "least-used",
    "cost-optimized",
    "strict-random",
    "lkgp",
    "context-optimized",
    "headroom",
    "reset-window",
    "reset-aware",
    "cache-optimized",
)

EXECUTION_SHAPES: tuple[str, ...] = (
    "fusion",
    "pipeline",
    "context-relay",
    "auto",
)

FUSION_MAX_PANEL = 40
HANDOFF_WARNING = 0.85
HANDOFF_EXHAUSTION = 0.95
DEFAULT_HANDOFF_PROVIDERS: tuple[str, ...] = ("codex",)


class StrategyNotASort(ValueError):
    """Raised when a caller asks apply_strategy to permute an execution shape."""


class ExecutionRefused(ValueError):
    """Plan or run cannot proceed. `.code` is an HTTP-like status."""

    def __init__(self, code: int, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def refuse_as_sort(strategy: str) -> None:
    name = (strategy or "").strip().lower().replace("_", "-")
    if name in EXECUTION_SHAPES:
        raise StrategyNotASort(
            f"{name} is an execution shape, not a target permutation"
        )


def is_tool_bearing(tools: Any, tool_choice: Any) -> bool:
    if not isinstance(tools, list) or not tools:
        return False
    return tool_choice != "none"


# --- fusion -----------------------------------------------------------------

FusionMode = Literal["direct", "fanout"]


@dataclass(frozen=True)
class FusionPlan:
    panel: tuple[str, ...]
    judge: str
    mode: FusionMode
    explicit_judge: bool
    tool_bearing: bool


def plan_fusion(
    models: list[str],
    *,
    judge_model: str | None = None,
    max_panel: int = FUSION_MAX_PANEL,
    tools: Any = None,
    tool_choice: Any = None,
) -> FusionPlan:
    panel = tuple(m for m in models if m)
    if not panel:
        raise ExecutionRefused(400, "Fusion combo has no models")
    if len(panel) > max_panel:
        raise ExecutionRefused(
            400,
            f"Fusion panel too large ({len(panel)} models, max {max_panel})",
        )
    explicit = bool((judge_model or "").strip())
    judge = (judge_model or "").strip() or panel[0]
    tool_bearing = is_tool_bearing(tools, tool_choice)
    if len(panel) == 1 or tool_bearing:
        return FusionPlan(
            panel=panel,
            judge=judge,
            mode="direct",
            explicit_judge=explicit,
            tool_bearing=tool_bearing,
        )
    return FusionPlan(
        panel=panel,
        judge=judge,
        mode="fanout",
        explicit_judge=explicit,
        tool_bearing=False,
    )


def build_judge_prompt(answers: list[str]) -> str:
    """Anonymize panel text as Source N. Judge must not name the models."""
    panel = "\n\n".join(
        f"[Source {i}]\n{text}" for i, text in enumerate(answers, 1)
    )
    return (
        "You are the JUDGE in a model-fusion panel. "
        f"{len(answers)} experts answered independently. "
        "Do NOT mention that multiple models were used, and do NOT refer to "
        "the sources. Produce ONE final answer for the user. "
        "You are not a vote-counter. Override a wrong consensus.\n\n"
        "=== PANEL RESPONSES ===\n"
        f"{panel}\n"
        "=== END PANEL RESPONSES ===\n\n"
        "Now write the final answer to the user's original request."
    )


CallModel = Callable[..., str]


def run_fusion(
    plan: FusionPlan,
    call_model: CallModel,
    *,
    user_text: str,
    stream: bool = False,
    tools: Any = None,
    tool_choice: Any = None,
) -> str:
    """Sync fusion. Quorum-grace timers and admission lanes are not ported."""
    if plan.mode == "direct":
        target = plan.judge if plan.tool_bearing else plan.panel[0]
        return call_model(
            target,
            user_text=user_text,
            stream=stream,
            tools=tools,
            tool_choice=tool_choice,
        )
    answers: list[str] = []
    for member in plan.panel:
        text = call_model(
            member,
            user_text=user_text,
            stream=False,
            tools=None,
            tool_choice=None,
        )
        if text and str(text).strip():
            answers.append(str(text))
    if not answers:
        raise ExecutionRefused(503, "All fusion panel models failed")
    if len(answers) == 1 and not plan.explicit_judge:
        return answers[0]
    return call_model(
        plan.judge,
        user_text=build_judge_prompt(answers),
        stream=stream,
        tools=tools,
        tool_choice=tool_choice,
    )


# --- pipeline --------------------------------------------------------------


@dataclass(frozen=True)
class PipelineStep:
    model: str
    prompt: str | None = None
    hidden: bool = False


def visible_pipeline_steps(steps: list[PipelineStep]) -> list[PipelineStep]:
    return [s for s in steps if s.model and not s.hidden]


def run_pipeline(
    steps: list[PipelineStep],
    call_model: CallModel,
    *,
    user_text: str,
    stream: bool = False,
    tools: Any = None,
    tool_choice: Any = None,
) -> str:
    """Sequential chain. Intermediate 400/empty fails the whole pipeline.

    Transient retries (429/502/503/504) are not ported: the caller retries.
    """
    chain = visible_pipeline_steps(steps)
    if not chain:
        raise ExecutionRefused(400, "Pipeline combo has no models")
    if len(chain) == 1:
        return call_model(
            chain[0].model,
            user_text=user_text,
            stream=stream,
            tools=tools,
            tool_choice=tool_choice,
            system=chain[0].prompt,
        )
    prev = user_text
    last_index = len(chain) - 1
    for i, step in enumerate(chain):
        final = i == last_index
        text = call_model(
            step.model,
            user_text=prev,
            stream=stream if final else False,
            tools=tools if final else None,
            tool_choice=tool_choice if final else None,
            system=step.prompt,
        )
        if not final:
            if not text or not str(text).strip():
                raise ExecutionRefused(
                    502,
                    f"Pipeline step {i + 1} ({step.model}) returned empty output",
                )
            prev = str(text)
        else:
            return str(text)
    raise ExecutionRefused(500, "Pipeline produced no final response")


# --- context-relay ---------------------------------------------------------


@dataclass
class RelayHandoff:
    session_id: str
    combo_name: str
    summary: str
    from_account: str


@dataclass
class RelayStore:
    """In-memory stand-in for OmniRoute contextHandoffs. No SQLite."""

    by_session: dict[tuple[str, str], RelayHandoff] = field(default_factory=dict)

    def get(self, session_id: str, combo_name: str) -> RelayHandoff | None:
        return self.by_session.get((session_id, combo_name))

    def put(self, handoff: RelayHandoff) -> None:
        self.by_session[(handoff.session_id, handoff.combo_name)] = handoff


def resolve_handoff_providers(explicit: list[str] | None) -> list[str]:
    if explicit is None:
        return list(DEFAULT_HANDOFF_PROVIDERS)
    return [p.strip().lower() for p in explicit if p and p.strip()]


def pick_relay_target(
    models: list[str],
    *,
    available: dict[str, bool] | None = None,
) -> str | None:
    """First available in list order. Unavailable is a skip, not a reorder."""
    flags = available or {}
    for model in models:
        if not model:
            continue
        if flags.get(model, True):
            return model
    return None


def should_generate_handoff(
    *,
    provider: str,
    percent_used: float,
    handoff_providers: list[str] | None = None,
    threshold: float = HANDOFF_WARNING,
    already_active: bool = False,
    session_id: str | None = None,
    connection_id: str | None = None,
) -> bool:
    """Warning-band persist. We do not fetch Codex quota or call a summarizer."""
    if already_active:
        return False
    if not session_id or not connection_id:
        return False
    providers = resolve_handoff_providers(handoff_providers)
    if not providers:
        return False
    if provider.strip().lower() not in providers:
        return False
    if percent_used < threshold:
        return False
    if percent_used >= HANDOFF_EXHAUSTION:
        return False
    return True


def inject_handoff(user_text: str, handoff: RelayHandoff | None) -> str:
    if handoff is None:
        return user_text
    blob = (
        "<context_handoff>\n"
        "<transfer_reason>Account quota transfer - continuing from previous session"
        "</transfer_reason>\n"
        f"<session_summary>{handoff.summary}</session_summary>\n"
        "</context_handoff>\n\n"
    )
    return blob + user_text


# --- auto ------------------------------------------------------------------


def resolve_auto(resolved: str | None) -> str:
    """auto is a meta-router. Caller must already have picked a sort strategy.

    OmniRoute autoCombo (intent classify, mode packs, complexity scoring) is
    not ported. pipeline_enabled on auto/smart is not implied.
    """
    name = (resolved or "").strip().lower().replace("_", "-")
    if not name:
        raise ExecutionRefused(
            400, "auto is a meta-router; caller must pass a concrete sort strategy"
        )
    if name in EXECUTION_SHAPES:
        raise ExecutionRefused(
            400,
            f"auto cannot resolve to {name}; that shape needs its own dispatcher",
        )
    if name not in SORT_STRATEGIES:
        raise ExecutionRefused(400, f"auto cannot resolve to unknown strategy {name!r}")
    return name


# --- dispatch / chat body ---------------------------------------------------

# OpenVault /v1 default model is "auto" (catalog pick). That is NOT OmniRoute auto.
MODEL_SHAPES: tuple[str, ...] = ("fusion", "pipeline", "context-relay")


class StrategyIsASort(ValueError):
    """dispatch_combo was given a sort name; caller should apply_strategy."""

    def __init__(self, strategy: str) -> None:
        super().__init__(f"{strategy} is a sort; use apply_strategy")
        self.strategy = strategy


def _norm_name(value: Any) -> str:
    return str(value or "").strip().lower().replace("_", "-")


def shape_from_chat_body(body: dict[str, Any] | None) -> str | None:
    """Which execution shape this OpenAI-shaped body asked for, if any.

    `model: auto` is OpenVault's catalog alias, never OmniRoute auto.
    """
    if not isinstance(body, dict):
        return None
    combo = body.get("combo")
    if isinstance(combo, dict):
        name = _norm_name(combo.get("strategy"))
        if name in EXECUTION_SHAPES:
            return name
    name = _norm_name(body.get("strategy"))
    if name in EXECUTION_SHAPES:
        return name
    name = _norm_name(body.get("model"))
    if name in MODEL_SHAPES:
        return name
    return None


def combo_models_from_body(body: dict[str, Any] | None) -> list[Any]:
    if not isinstance(body, dict):
        return []
    combo = body.get("combo")
    if isinstance(combo, dict) and isinstance(combo.get("models"), list):
        return list(combo["models"])
    return []


def relay_available_from_body(body: dict[str, Any] | None) -> dict[str, bool] | None:
    """Caller-supplied availability. Missing keys default available. No quota fetch."""
    if not isinstance(body, dict):
        return None
    combo = body.get("combo")
    if not isinstance(combo, dict):
        return None
    raw = combo.get("available")
    if not isinstance(raw, dict) or not raw:
        return None
    out: dict[str, bool] = {}
    for key, value in raw.items():
        if isinstance(value, bool):
            out[str(key)] = value
    return out or None


def relay_handoff_from_body(body: dict[str, Any] | None) -> RelayHandoff | None:
    """Caller-supplied handoff blob. Not OmniRoute SQLite contextHandoffs."""
    if not isinstance(body, dict):
        return None
    combo = body.get("combo")
    if not isinstance(combo, dict):
        return None
    raw = combo.get("handoff") or combo.get("contextHandoff")
    if not isinstance(raw, dict):
        return None
    session_id = str(raw.get("session_id") or raw.get("sessionId") or "").strip()
    summary = str(raw.get("summary") or "").strip()
    if not session_id or not summary:
        return None
    combo_name = str(raw.get("combo_name") or raw.get("comboName") or "").strip()
    from_account = str(raw.get("from_account") or raw.get("fromAccount") or "").strip()
    return RelayHandoff(session_id, combo_name, summary, from_account)


def user_text_from_body(body: dict[str, Any] | None) -> str:
    if not isinstance(body, dict):
        return ""
    messages = body.get("messages")
    if not isinstance(messages, list):
        return ""
    for msg in reversed(messages):
        if not isinstance(msg, dict) or msg.get("role") != "user":
            continue
        content = msg.get("content")
        if isinstance(content, str):
            return content
    return ""


def extract_assistant_text(payload: Any) -> str:
    if not isinstance(payload, dict):
        return ""
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0]
    if not isinstance(first, dict):
        return ""
    msg = first.get("message") or first.get("delta") or {}
    if isinstance(msg, dict) and isinstance(msg.get("content"), str):
        return msg["content"]
    if isinstance(first.get("text"), str):
        return first["text"]
    return ""


def chat_shape_refusal(body: dict[str, Any] | None) -> dict[str, Any] | None:
    """400 when a shape is named but combo.models is missing.

    With models, the caller should run dispatch_combo via a hop-walk
    call_model. /v1 must not treat vault keys as a fusion panel.
    """
    shape = shape_from_chat_body(body)
    if shape is None:
        return None
    if combo_models_from_body(body):
        return None
    return {
        "error": {
            "message": (
                f"{shape} is an execution shape, not a vault-key walk. "
                "Call dispatch_combo with combo.models; /v1 does not fan-out keys "
                "as a panel."
            ),
            "type": "openvault_execution_shape",
        }
    }


def steps_from_models(models: list[Any]) -> list[PipelineStep]:
    out: list[PipelineStep] = []
    for item in models:
        if isinstance(item, PipelineStep):
            out.append(item)
        elif isinstance(item, str):
            out.append(PipelineStep(item))
        elif isinstance(item, dict):
            out.append(
                PipelineStep(
                    model=str(item.get("model") or item.get("execution_key") or ""),
                    prompt=item.get("prompt") if isinstance(item.get("prompt"), str) else None,
                    hidden=bool(item.get("hidden") or item.get("isHidden")),
                )
            )
    return out


def dispatch_combo(
    strategy: str,
    models: list[Any],
    call_model: CallModel,
    *,
    user_text: str = "",
    stream: bool = False,
    tools: Any = None,
    tool_choice: Any = None,
    judge_model: str | None = None,
    resolved: str | None = None,
    available: dict[str, bool] | None = None,
    handoff: RelayHandoff | None = None,
) -> str:
    """Run an execution shape. Sort names raise StrategyIsASort."""
    name = _norm_name(strategy)
    if name in SORT_STRATEGIES:
        raise StrategyIsASort(name)
    if name == "auto":
        raise StrategyIsASort(resolve_auto(resolved))
    if name == "fusion":
        ids = [s.model for s in steps_from_models(models)]
        plan = plan_fusion(
            ids, judge_model=judge_model, tools=tools, tool_choice=tool_choice
        )
        return run_fusion(
            plan,
            call_model,
            user_text=user_text,
            stream=stream,
            tools=tools,
            tool_choice=tool_choice,
        )
    if name == "pipeline":
        return run_pipeline(
            steps_from_models(models),
            call_model,
            user_text=user_text,
            stream=stream,
            tools=tools,
            tool_choice=tool_choice,
        )
    if name == "context-relay":
        ids = [s.model for s in steps_from_models(models) if not s.hidden]
        picked = pick_relay_target(ids, available=available)
        if picked is None:
            raise ExecutionRefused(503, "no available relay target")
        return call_model(
            picked,
            user_text=inject_handoff(user_text, handoff),
            stream=stream,
            tools=tools,
            tool_choice=tool_choice,
        )
    raise ExecutionRefused(400, f"unknown execution shape {name!r}")


# --- hop walk --------------------------------------------------------------

# Status-only subset of OpenVault classify_attempt. No body-text credits /
# oauth / context parse. Callers that need those reasons use OpenVault.
TRIP_STATUS_CODES: frozenset[int] = frozenset({408, 500, 502, 503, 504})


@dataclass(frozen=True)
class HopOutcome:
    attempt_class: str
    candidate: str
    job: str
    trip_provider_breaker: bool
    counts_as_hard_fail: bool


def classify_hop_status(status: int | None) -> HopOutcome:
    """Status-only hop policy. 429 parks; 5xx trips; 401 quarantines; 400 dead.

    Matches OpenVault classify_attempt axes for numeric status. Does not read
    Retry-After, credits_exhausted, or 'input is too long'.
    """
    if status is not None and 200 <= status < 300:
        return HopOutcome("success", "keep", "done", False, False)
    if status is None:
        return HopOutcome("hard_fail", "keep", "continue_chain", True, True)
    if status == 429:
        return HopOutcome("rate_limit", "park", "continue_chain", False, False)
    if status in TRIP_STATUS_CODES:
        return HopOutcome("hard_fail", "keep", "continue_chain", True, True)
    if status in (401, 403):
        return HopOutcome("auth_fail", "quarantine_key", "continue_chain", False, False)
    if status in (400, 404, 422):
        return HopOutcome("non_retryable", "keep", "dead", False, False)
    return HopOutcome("hard_fail", "keep", "continue_chain", False, True)


@dataclass(frozen=True)
class Hop:
    execution_key: str
    model_str: str
    provider: str = ""
    healthy: bool = True


def hops_for_model(
    hops: list[Hop],
    model: str,
    *,
    serves: Callable[[Hop, str], bool] | None = None,
) -> list[Hop]:
    """Healthy hops that can serve this model, in list order."""
    want = (model or "").strip()
    if not want:
        return []
    out: list[Hop] = []
    for hop in hops:
        if not hop.healthy:
            continue
        if hop.model_str == want or hop.execution_key == want:
            out.append(hop)
        elif serves is not None and serves(hop, want):
            out.append(hop)
    return out


def pick_hop(
    hops: list[Hop],
    model: str,
    *,
    serves: Callable[[Hop, str], bool] | None = None,
) -> Hop | None:
    """First healthy hop that matches model_str / execution_key, or serves()."""
    found = hops_for_model(hops, model, serves=serves)
    return found[0] if found else None


def hop_call_model(
    hops: list[Hop],
    post: Callable[..., str],
    *,
    serves: Callable[[Hop, str], bool] | None = None,
) -> CallModel:
    """Bind dispatch_combo's call_model to a hop list.

    Tries every matching hop until one returns non-empty text. Empty is a
    miss, not a permutation of fusion. ExecutionRefused from post (job=dead)
    is not swallowed -- same as OpenVault classify_attempt job=dead.
    """

    def call(model: str, **kwargs: Any) -> str:
        for hop in hops_for_model(hops, model, serves=serves):
            text = post(hop, model=model, **kwargs)
            if text and str(text).strip():
                return str(text)
        return ""

    return call


def sse_wrap_text(text: str) -> tuple[bytes, bytes]:
    """SSE pair for a buffered last hop (one-survivor skip, not a second call).

    Real last-hop streaming is OpenVault's httpx stream. This wrap is only
    when the client asked for stream but dispatch already holds the text.
    """
    payload = json.dumps({"choices": [{"delta": {"content": str(text)}}]})
    return f"data: {payload}\n\n".encode("utf-8"), b"data: [DONE]\n\n"

