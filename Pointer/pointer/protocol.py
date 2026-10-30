"""Pointer backend payloads. Frozen contract; tests lock the shape."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

SCHEMA = "pointer.intent/v1"

ActionType = Literal[
    "perceive",
    "move",
    "click",
    "type",
    "hotkey",
    "wait",
    "verify",
    "shell",
    "file_write",
    "file_delete",
]

IRREVERSIBLE = frozenset({"shell", "file_write", "file_delete"})
REMOTE_NEEDS_APPROVAL = frozenset(
    {"move", "click", "type", "hotkey", "shell", "file_write", "file_delete"}
)


@dataclass
class Action:
    type: str
    x: int | None = None
    y: int | None = None
    button: str = "left"
    text: str | None = None
    keys: list[str] | None = None
    ms: int | None = None
    expect_contains: str | None = None
    path: str | None = None
    content: str | None = None
    command: str | None = None

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Action":
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        data = {k: v for k, v in raw.items() if k in known}
        if "type" not in data or not isinstance(data["type"], str):
            raise ValueError("action.type is required")
        return cls(**data)

    def is_irreversible(self) -> bool:
        return self.type in IRREVERSIBLE


@dataclass
class Intent:
    schema: str
    intent_id: str
    source: str
    goal: str
    actions: list[Action]
    irreversible: bool = False
    approval_token: str | None = None
    allow_local_act: bool = False

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Intent":
        if not isinstance(raw, dict):
            raise ValueError("intent must be an object")
        actions_raw = raw.get("actions")
        if not isinstance(actions_raw, list) or not actions_raw:
            raise ValueError("intent.actions must be a non-empty list")
        actions = [Action.from_dict(a) if isinstance(a, dict) else None for a in actions_raw]
        if any(a is None for a in actions):
            raise ValueError("each action must be an object")
        schema = str(raw.get("schema") or SCHEMA)
        intent_id = str(raw.get("intent_id") or "").strip()
        source = str(raw.get("source") or "").strip()
        goal = str(raw.get("goal") or "").strip()
        if schema != SCHEMA:
            raise ValueError(f"unsupported schema {schema}")
        if not intent_id:
            raise ValueError("intent_id is required")
        if source not in {"human", "cortex", "remote-paired", "local-test"}:
            raise ValueError("source must be human|cortex|remote-paired|local-test")
        if not goal:
            raise ValueError("goal is required")
        irreversible = bool(raw.get("irreversible")) or any(a.is_irreversible() for a in actions)
        return cls(
            schema=schema,
            intent_id=intent_id,
            source=source,
            goal=goal,
            actions=actions,
            irreversible=irreversible,
            approval_token=raw.get("approval_token"),
            allow_local_act=bool(raw.get("allow_local_act")),
        )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d


@dataclass
class ActionResult:
    type: str
    ok: bool
    detail: str
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class IntentResponse:
    schema: str
    intent_id: str
    verdict: str
    reason: str
    degraded: list[str]
    ledger_hash: str | None
    actions: list[ActionResult]
    screenshot_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "intent_id": self.intent_id,
            "verdict": self.verdict,
            "reason": self.reason,
            "degraded": self.degraded,
            "ledger_hash": self.ledger_hash,
            "screenshot_path": self.screenshot_path,
            "actions": [asdict(a) for a in self.actions],
        }
