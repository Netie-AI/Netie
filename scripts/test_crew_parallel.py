#!/usr/bin/env python3
"""Parallel Crew runner stays fail-closed and capped. python3 scripts/test_crew_parallel.py"""

from __future__ import annotations

import sys
import threading
import time
import unittest
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crew_budget import TokenBudget
from crew_parallel import Job, run_batch
from crew_tool_wrap import CortexDenied, Verdict


class CountingGate:
    def __init__(self, allow_tools: set[str]) -> None:
        self.allow_tools = allow_tools
        self.executed: list[str] = []
        self._lock = threading.Lock()
        self._in_flight = 0
        self.peak = 0

    def check(self, tool: str, payload: dict[str, Any]) -> Verdict:
        if tool in self.allow_tools:
            return Verdict(allowed=True)
        return Verdict(allowed=False, reason="manifest miss")

    def execute(self, tool: str, payload: dict[str, Any]) -> Any:
        with self._lock:
            self._in_flight += 1
            self.peak = max(self.peak, self._in_flight)
        try:
            time.sleep(0.05)
            with self._lock:
                self.executed.append(tool)
            return {"tool": tool}
        finally:
            with self._lock:
                self._in_flight -= 1


class CrewParallelTests(unittest.TestCase):
    def test_denied_jobs_do_not_execute(self) -> None:
        gate = CountingGate({"export_pptx"})
        jobs = [
            Job("a", "export_pptx", {"operator_confirm": True}),
            Job("b", "warehouse.query", {"sql": "select 1"}),
            Job("c", "export_pptx", {"operator_confirm": True}),
        ]
        results = run_batch(
            gate, jobs, max_in_flight=2, budget=TokenBudget(max_tokens=10_000)
        )
        self.assertEqual([r.status for r in results], ["DONE", "FAILED", "DONE"])
        self.assertEqual(gate.executed, ["export_pptx", "export_pptx"])
        self.assertIn("manifest miss", results[1].detail)

    def test_cap_is_respected(self) -> None:
        gate = CountingGate({"t"})
        jobs = [Job(str(i), "t", {}) for i in range(5)]
        run_batch(
            gate, jobs, max_in_flight=2, budget=TokenBudget(max_tokens=10_000)
        )
        self.assertLessEqual(gate.peak, 2)
        self.assertEqual(len(gate.executed), 5)

    def test_reject_zero_workers(self) -> None:
        gate = CountingGate(set())
        with self.assertRaises(ValueError):
            run_batch(gate, [Job("x", "t", {})], max_in_flight=0)

    def test_reject_unbounded_spawn(self) -> None:
        gate = CountingGate({"t"})
        with self.assertRaises(ValueError) as ctx:
            run_batch(gate, [Job("x", "t", {})], max_in_flight=3)
        self.assertIn("WIP law", str(ctx.exception))
        self.assertEqual(gate.executed, [])

    def test_missing_gate_fails_closed(self) -> None:
        with self.assertRaises(CortexDenied):
            from crew_tool_wrap import run_tool

            run_tool(None, "t", {})  # type: ignore[arg-type]

    def test_missing_budget_does_not_execute(self) -> None:
        gate = CountingGate({"t"})
        with self.assertRaises(CortexDenied) as ctx:
            run_batch(gate, [Job("x", "t", {})], max_in_flight=1)
        self.assertIn("token budget required", str(ctx.exception))
        self.assertEqual(gate.executed, [])

    def test_skill_body_job_does_not_run(self) -> None:
        gate = CountingGate({"t"})
        jobs = [Job("a", "t", {"skill_body": "SECRET prompt"})]
        results = run_batch(
            gate, jobs, max_in_flight=1, budget=TokenBudget(max_tokens=10_000)
        )
        self.assertEqual(results[0].status, "FAILED")
        self.assertIn("skill_body", results[0].detail)
        self.assertEqual(gate.executed, [])

    def test_leave_machine_batch_posts_skill_ids(self) -> None:
        from crew_ov_gate import OpenVaultCrewGate
        from crew_skills import SkillRegistry, register_skill

        gate = CountingGate({"open_url", "warehouse.query"})
        seen: list[dict[str, Any]] = []

        def post(url: str, body: dict[str, Any]) -> dict[str, Any]:
            seen.append(body)
            return {"allowed": True}

        def deny(url: str, body: dict[str, Any]) -> dict[str, Any]:
            return {"allowed": False, "reason": "vault miss"}

        reg = SkillRegistry()
        register_skill(reg, "S-0004")
        ov = OpenVaultCrewGate("http://127.0.0.1:5000", post=post, registry=reg)
        blocked = run_batch(
            gate,
            [Job("a", "open_url", {})],
            max_in_flight=1,
            budget=TokenBudget(max_tokens=10_000),
        )
        self.assertEqual(blocked[0].status, "FAILED")
        self.assertIn("OpenVault", blocked[0].detail)
        self.assertEqual(gate.executed, [])
        cortex = run_batch(
            gate,
            [Job("q", "warehouse.query", {"sql": "select 1"})],
            max_in_flight=1,
            budget=TokenBudget(max_tokens=10_000),
            ov=ov,
            parent_run_id="p1",
        )
        self.assertEqual(cortex[0].status, "DONE")
        self.assertEqual(seen, [])
        missing = run_batch(
            gate,
            [Job("a", "open_url", {})],
            max_in_flight=1,
            budget=TokenBudget(max_tokens=10_000),
            ov=ov,
        )
        self.assertEqual(missing[0].status, "FAILED")
        self.assertIn("parent and child", missing[0].detail)
        self.assertEqual(seen, [])
        ok = run_batch(
            gate,
            [Job("a", "open_url", {})],
            max_in_flight=1,
            budget=TokenBudget(max_tokens=10_000),
            ov=ov,
            parent_run_id="p1",
        )
        self.assertEqual(ok[0].status, "DONE")
        self.assertEqual(gate.executed, ["warehouse.query", "open_url"])
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0]["skill_ids"], ["S-0004"])
        self.assertEqual(seen[0]["id"], "open_url")
        self.assertNotIn("skill_body", str(seen[0]))
        vault = OpenVaultCrewGate("http://127.0.0.1:5000", post=deny)
        refused = run_batch(
            gate,
            [Job("a", "open_url", {})],
            max_in_flight=1,
            budget=TokenBudget(max_tokens=10_000),
            ov=vault,
            parent_run_id="p1",
        )
        self.assertEqual(refused[0].status, "FAILED")
        self.assertIn("vault miss", refused[0].detail)
        self.assertEqual(gate.executed, ["warehouse.query", "open_url"])


if __name__ == "__main__":
    unittest.main()
