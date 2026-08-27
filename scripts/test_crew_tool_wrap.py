#!/usr/bin/env python3
"""Crew wrap: denied tools never execute. Run: python3 scripts/test_crew_tool_wrap.py"""

from __future__ import annotations

import unittest
from typing import Any

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crew_tool_wrap import CortexDenied, Verdict, run_tool


class FakeGate:
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self.executed: list[str] = []

    def check(self, tool: str, payload: dict[str, Any]) -> Verdict:
        return Verdict(allowed=self.allowed, reason="manifest miss")

    def execute(self, tool: str, payload: dict[str, Any]) -> Any:
        self.executed.append(tool)
        return {"ok": True, "tool": tool}


class CrewWrapTests(unittest.TestCase):
    def test_refusal_does_not_execute(self) -> None:
        gate = FakeGate(False)
        with self.assertRaises(CortexDenied):
            run_tool(gate, "warehouse.query", {"sql": "select 1"})
        self.assertEqual(gate.executed, [])

    def test_allow_executes_once(self) -> None:
        gate = FakeGate(True)
        out = run_tool(gate, "export_pptx", {})
        self.assertEqual(out["tool"], "export_pptx")
        self.assertEqual(gate.executed, ["export_pptx"])

    def test_missing_gate_is_denied(self) -> None:
        with self.assertRaises(CortexDenied):
            run_tool(None, "anything", {})  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
