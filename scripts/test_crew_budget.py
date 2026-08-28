#!/usr/bin/env python3
"""Budget, ledger, OV gate. python3 scripts/test_crew_budget.py"""

from __future__ import annotations

import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crew_budget import BudgetDenied, TokenBudget, estimate_tokens
from crew_ledger import HashLedger, LedgerBroken, LedgerDenied
from crew_ov_gate import GateAsk, OpenVaultCrewGate, strip_bodies
from crew_parallel import Job, run_batch
from crew_tool_wrap import CortexDenied, Verdict


class CountingGate:
    def __init__(self, allow_tools: set[str]) -> None:
        self.allow_tools = allow_tools
        self.executed: list[str] = []
        self._lock = threading.Lock()

    def check(self, tool: str, payload: dict[str, Any]) -> Verdict:
        if tool in self.allow_tools:
            return Verdict(allowed=True)
        return Verdict(allowed=False, reason="manifest miss")

    def execute(self, tool: str, payload: dict[str, Any]) -> Any:
        with self._lock:
            self.executed.append(tool)
        return {"tool": tool}


class BudgetLedgerGateTests(unittest.TestCase):
    def test_over_budget_does_not_execute(self) -> None:
        gate = CountingGate({"t"})
        budget = TokenBudget(max_tokens=40)
        jobs = [Job("a", "t", {"blob": "x" * 80}), Job("b", "t", {"blob": "y" * 80})]
        results = run_batch(gate, jobs, max_in_flight=1, budget=budget)
        self.assertEqual(results[0].status, "DONE")
        self.assertEqual(results[1].status, "FAILED")
        self.assertIn("budget", results[1].detail)
        self.assertEqual(gate.executed, ["t"])

    def test_denied_does_not_charge(self) -> None:
        gate = CountingGate(set())
        budget = TokenBudget(max_tokens=100)
        run_batch(gate, [Job("a", "t", {})], budget=budget)
        self.assertEqual(budget.spent, 0)

    def test_skill_body_does_not_charge(self) -> None:
        gate = CountingGate({"t"})
        budget = TokenBudget(max_tokens=100)
        run_batch(
            gate,
            [Job("a", "t", {"skill_body": "x" * 400})],
            budget=budget,
        )
        self.assertEqual(budget.spent, 0)
        self.assertEqual(gate.executed, [])

    def test_hitl_refuse_does_not_charge(self) -> None:
        gate = CountingGate({"export_pptx"})
        budget = TokenBudget(max_tokens=100)
        results = run_batch(
            gate, [Job("a", "export_pptx", {})], budget=budget
        )
        self.assertEqual(results[0].status, "FAILED")
        self.assertIn("HITL", results[0].detail)
        self.assertEqual(budget.spent, 0)
        self.assertEqual(gate.executed, [])

    def test_deepagents_builtin_does_not_charge(self) -> None:
        gate = CountingGate({"read_file"})
        budget = TokenBudget(max_tokens=100)
        results = run_batch(
            gate, [Job("a", "read_file", {})], budget=budget
        )
        self.assertEqual(results[0].status, "FAILED")
        self.assertIn("not a Crew tool", results[0].detail)
        self.assertEqual(budget.spent, 0)
        self.assertEqual(gate.executed, [])

    def test_ledger_detects_tamper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "crew.jsonl"
            log = HashLedger(path)
            log.append({"id": "a", "status": "DONE"})
            log.append({"id": "b", "status": "FAILED"})
            self.assertEqual(log.verify(), 2)
            lines = path.read_text(encoding="utf-8").splitlines()
            row = json.loads(lines[0])
            row["record"]["status"] = "FORGED"
            path.write_text(json.dumps(row) + "\n" + lines[1] + "\n", encoding="utf-8")
            with self.assertRaises(LedgerBroken):
                log.verify()

    def test_ledger_refuses_skill_body(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "crew.jsonl"
            log = HashLedger(path)
            with self.assertRaises(LedgerDenied):
                log.append({"id": "a", "skill_body": "SECRET"})
            self.assertFalse(path.is_file())
            log.append({"id": "a", "status": "DONE"})
            dumped = path.read_text(encoding="utf-8")
            self.assertNotIn("SECRET", dumped)

    def test_strip_bodies_drops_prompts(self) -> None:
        cleaned = strip_bodies(
            {
                "skills": [{"id": "x", "skill_body": "SECRET", "prompt": "no"}],
                "transcript": "child ramble",
            }
        )
        dumped = json.dumps(cleaned)
        self.assertNotIn("SECRET", dumped)
        self.assertNotIn("child ramble", dumped)
        self.assertEqual(cleaned["skills"][0]["id"], "x")

    def test_has_bodies_nested(self) -> None:
        from crew_ov_gate import has_bodies

        self.assertTrue(has_bodies({"child": {"transcript": "x"}}))
        self.assertFalse(has_bodies({"id": "t1", "status": "open"}))

    def test_missing_ov_url_is_denied(self) -> None:
        gate = OpenVaultCrewGate(base_url=None, post=lambda u, b: {"allowed": True})
        with self.assertRaises(CortexDenied):
            gate.allow(
                GateAsk("skill", "netie-kb.skills", "invoke", "p1", "c1", "need x")
            )

    def test_ov_without_allowed_is_denied(self) -> None:
        def post(url: str, body: dict[str, Any]) -> dict[str, Any]:
            self.assertTrue(url.endswith("/api/crew/gate"))
            self.assertNotIn("skill_body", body)
            return {"found": True, "owner": "netie-kb"}

        gate = OpenVaultCrewGate("http://127.0.0.1:5000", post=post)
        with self.assertRaises(CortexDenied):
            gate.allow(GateAsk("service", "space.ai", "leave", "p1", "c1"))

    def test_ov_allowed_returns_stripped(self) -> None:
        def post(url: str, body: dict[str, Any]) -> dict[str, Any]:
            return {
                "allowed": True,
                "found": True,
                "skill_body": "MUST-NOT-LEAK",
                "parent_run_id": body["parent_run_id"],
            }

        gate = OpenVaultCrewGate("http://127.0.0.1:5000", post=post)
        out = gate.allow(GateAsk("service", "space.ai", "invoke", "p1", "c1"))
        self.assertTrue(out["allowed"])
        self.assertNotIn("skill_body", out)

    def test_skill_kind_refuses_before_transport(self) -> None:
        seen: list[str] = []

        def post(url: str, body: dict[str, Any]) -> dict[str, Any]:
            seen.append(url)
            return {"allowed": True, "found": True}

        gate = OpenVaultCrewGate("http://127.0.0.1:5000", post=post)
        with self.assertRaises(CortexDenied) as ctx:
            gate.allow(GateAsk("skill", "netie-kb.skills", "invoke", "p1", "c1"))
        self.assertIn("no skill registered", str(ctx.exception))
        self.assertEqual(seen, [])

    def test_estimate_is_at_least_one(self) -> None:
        self.assertGreaterEqual(estimate_tokens({}), 1)

    def test_zero_budget_rejected(self) -> None:
        with self.assertRaises(ValueError):
            TokenBudget(0)


if __name__ == "__main__":
    unittest.main()
