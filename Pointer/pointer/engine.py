"""Run a gated intent: perceive -> (optional act) -> prove."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from . import cortex_client
from .executor import Executor, ExecutorError
from .gate import Gate
from .ledger import Ledger
from .protocol import Action, ActionResult, Intent, IntentResponse, SCHEMA


class Engine:
    def __init__(
        self,
        *,
        state_dir: Path,
        pair_token: str,
        approval_token: str,
        bind_is_loopback: bool,
        executor: Executor | None = None,
    ) -> None:
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.sandbox = self.state_dir / "sandbox"
        self.sandbox.mkdir(parents=True, exist_ok=True)
        self.bind_is_loopback = bind_is_loopback
        self.ledger = Ledger(self.state_dir / "ledger.jsonl")
        self.executor = executor or Executor(
            display=None, screenshot_dir=self.state_dir / "shots"
        )
        self.gate = Gate(
            state_dir=state_dir,
            pair_token=pair_token,
            cortex_reachable=cortex_client.ping(),
            approval_token=approval_token,
        )

    def refresh_cortex(self) -> None:
        self.gate.cortex_reachable = cortex_client.ping()

    def handle(self, intent: Intent, *, bearer: str | None) -> IntentResponse:
        self.refresh_cortex()
        decision = self.gate.decide(
            intent, bearer=bearer, bind_is_loopback=self.bind_is_loopback
        )
        if not decision.allowed:
            digest = self.ledger.append(
                {
                    "intent_id": intent.intent_id,
                    "verdict": decision.verdict,
                    "reason": decision.reason,
                    "goal": intent.goal,
                    "source": intent.source,
                }
            )
            return IntentResponse(
                schema=SCHEMA,
                intent_id=intent.intent_id,
                verdict=decision.verdict,
                reason=decision.reason,
                degraded=decision.degraded,
                ledger_hash=digest,
                actions=[],
            )

        results: list[ActionResult] = []
        shot: str | None = None
        try:
            for action in intent.actions:
                result, maybe_shot = self._run_action(action)
                results.append(result)
                if maybe_shot:
                    shot = maybe_shot
                if not result.ok:
                    raise ExecutorError(result.detail)
        except ExecutorError as exc:
            digest = self.ledger.append(
                {
                    "intent_id": intent.intent_id,
                    "verdict": "refused",
                    "reason": str(exc),
                    "goal": intent.goal,
                    "source": intent.source,
                    "results": [r.__dict__ for r in results],
                }
            )
            return IntentResponse(
                schema=SCHEMA,
                intent_id=intent.intent_id,
                verdict="refused",
                reason=str(exc),
                degraded=decision.degraded,
                ledger_hash=digest,
                actions=results,
                screenshot_path=shot,
            )

        digest = self.ledger.append(
            {
                "intent_id": intent.intent_id,
                "verdict": "executed",
                "reason": decision.reason,
                "goal": intent.goal,
                "source": intent.source,
                "degraded": decision.degraded,
                "results": [r.__dict__ for r in results],
            }
        )
        return IntentResponse(
            schema=SCHEMA,
            intent_id=intent.intent_id,
            verdict="executed",
            reason=decision.reason,
            degraded=decision.degraded,
            ledger_hash=digest,
            actions=results,
            screenshot_path=shot,
        )

    def _run_action(self, action: Action) -> tuple[ActionResult, str | None]:
        shot: str | None = None
        try:
            if action.type == "perceive":
                loc = self.executor.mouse_location()
                path = self.executor.screenshot(f"perceive-{uuid.uuid4().hex[:8]}.png")
                shot = str(path)
                return (
                    ActionResult(
                        "perceive",
                        True,
                        "screenshot and mouse location",
                        {"mouse": loc, "screenshot": shot, "bytes": path.stat().st_size},
                    ),
                    shot,
                )
            if action.type == "move":
                if action.x is None or action.y is None:
                    raise ExecutorError("move requires x and y")
                ev = self.executor.move(action.x, action.y)
                return ActionResult("move", True, "moved", ev), None
            if action.type == "click":
                if action.x is None or action.y is None:
                    raise ExecutorError("click requires x and y")
                ev = self.executor.click(action.x, action.y, action.button)
                return ActionResult("click", True, "clicked", ev), None
            if action.type == "type":
                if not action.text:
                    raise ExecutorError("type requires text")
                ev = self.executor.type_text(action.text)
                return ActionResult("type", True, "typed", ev), None
            if action.type == "hotkey":
                ev = self.executor.hotkey(action.keys or [])
                return ActionResult("hotkey", True, "hotkey", ev), None
            if action.type == "wait":
                ev = self.executor.wait(int(action.ms or 0))
                return ActionResult("wait", True, "waited", ev), None
            if action.type == "verify":
                loc = self.executor.mouse_location()
                needle = action.expect_contains
                if needle:
                    # OCR is not in this daemon yet. Fail closed rather than fake a pass.
                    raise ExecutorError(
                        "verify.expect_contains needs OCR; not shipped. Use mouse/screenshot evidence instead."
                    )
                return ActionResult("verify", True, "mouse location recorded", {"mouse": loc}), None
            if action.type == "file_write":
                dest = self._sandbox_path(action.path)
                dest.write_text(action.content or "", encoding="utf-8")
                return ActionResult("file_write", True, "wrote sandbox file", {"path": str(dest)}), None
            if action.type == "file_delete":
                dest = self._sandbox_path(action.path)
                if dest.exists():
                    dest.unlink()
                return ActionResult("file_delete", True, "deleted sandbox file", {"path": str(dest)}), None
            if action.type == "shell":
                raise ExecutorError("shell is parked; Pointer will not spawn a shell")
            raise ExecutorError(f"unknown action {action.type}")
        except ExecutorError as exc:
            return ActionResult(action.type, False, str(exc), {}), shot

    def _sandbox_path(self, path: str | None) -> Path:
        if not path:
            raise ExecutorError("path is required")
        raw = Path(path)
        dest = (self.sandbox / raw.name).resolve()
        sandbox = self.sandbox.resolve()
        if sandbox not in dest.parents and dest != sandbox:
            raise ExecutorError("file actions are contained to the Pointer sandbox")
        return dest

    def status(self) -> dict[str, Any]:
        self.refresh_cortex()
        loc = None
        loc_error = None
        try:
            loc = self.executor.mouse_location()
        except ExecutorError as exc:
            loc_error = str(exc)
        return {
            "killed": self.gate.killed(),
            "cortex_reachable": self.gate.cortex_reachable,
            "cortex_url": cortex_client.cortex_base(),
            "bind_is_loopback": self.bind_is_loopback,
            "mouse": loc,
            "mouse_error": loc_error,
            "ledger_hash": self.ledger.last_hash(),
            "sandbox": str(self.sandbox),
        }
