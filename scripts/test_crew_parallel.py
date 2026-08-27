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
            Job("a", "export_pptx", {}),
            Job("b", "warehouse.query", {"sql": "select 1"}),
            Job("c", "export_pptx", {}),
        ]
        results = run_batch(gate, jobs, max_in_flight=2)
        self.assertEqual([r.status for r in results], ["DONE", "FAILED", "DONE"])
        self.assertEqual(gate.executed, ["export_pptx", "export_pptx"])
        self.assertIn("manifest miss", results[1].detail)

    def test_cap_is_respected(self) -> None:
        gate = CountingGate({"t"})
        jobs = [Job(str(i), "t", {}) for i in range(5)]
        run_batch(gate, jobs, max_in_flight=2)
        self.assertLessEqual(gate.peak, 2)
        self.assertEqual(len(gate.executed), 5)

    def test_reject_zero_workers(self) -> None:
        gate = CountingGate(set())
        with self.assertRaises(ValueError):
            run_batch(gate, [Job("x", "t", {})], max_in_flight=0)

    def test_missing_gate_fails_closed(self) -> None:
        with self.assertRaises(CortexDenied):
            from crew_tool_wrap import run_tool

            run_tool(None, "t", {})  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
