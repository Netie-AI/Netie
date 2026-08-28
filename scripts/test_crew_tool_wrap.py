#!/usr/bin/env python3
"""Crew wrap: denied tools never execute. Run: python3 scripts/test_crew_tool_wrap.py"""

from __future__ import annotations

import unittest
from typing import Any

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crew_tool_wrap import CortexDenied, Verdict, run_tool, wrap_deepagents_tools, require_wrapped


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
        out = run_tool(gate, "export_pptx", {"operator_confirm": True})
        self.assertEqual(out["tool"], "export_pptx")
        self.assertEqual(gate.executed, ["export_pptx"])

    def test_missing_gate_is_denied(self) -> None:
        with self.assertRaises(CortexDenied):
            run_tool(None, "anything", {})  # type: ignore[arg-type]

    def test_deepagents_wrap_never_bypasses(self) -> None:
        gate = FakeGate(False)
        tools = wrap_deepagents_tools(gate, ["web_search"])
        with self.assertRaises(CortexDenied):
            tools["web_search"](q="secret")
        self.assertEqual(gate.executed, [])

    def test_empty_wrap_refuses_trust_the_llm(self) -> None:
        gate = FakeGate(True)
        with self.assertRaises(CortexDenied) as ctx:
            wrap_deepagents_tools(gate, [])
        self.assertIn("trust-the-LLM", str(ctx.exception))

    def test_blank_tool_name_refuses(self) -> None:
        gate = FakeGate(True)
        with self.assertRaises(CortexDenied):
            wrap_deepagents_tools(gate, ["  "])

    def test_require_wrapped_refuses_extras(self) -> None:
        gate = FakeGate(True)
        wrapped = wrap_deepagents_tools(gate, ["export_pptx"])
        with self.assertRaises(CortexDenied) as ctx:
            require_wrapped(["export_pptx", "web_search"], wrapped)
        self.assertIn("unwrapped tools", str(ctx.exception))
        tools = require_wrapped(["export_pptx"], wrapped)
        self.assertEqual(len(tools), 1)

    def test_write_without_hitl_does_not_execute(self) -> None:
        gate = FakeGate(True)
        with self.assertRaises(CortexDenied) as ctx:
            run_tool(gate, "export_pptx", {})
        self.assertIn("HITL", str(ctx.exception))
        self.assertEqual(gate.executed, [])

    def test_item_intake_needs_hitl(self) -> None:
        gate = FakeGate(True)
        with self.assertRaises(CortexDenied) as ctx:
            run_tool(gate, "item.intake", {"sku": "A-1"})
        self.assertIn("HITL", str(ctx.exception))
        self.assertEqual(gate.executed, [])
        out = run_tool(gate, "item.intake", {"sku": "A-1", "operator_confirm": True})
        self.assertEqual(out["tool"], "item.intake")
        self.assertEqual(gate.executed, ["item.intake"])

    def test_deepagents_filesystem_is_not_a_crew_tool(self) -> None:
        gate = FakeGate(True)
        with self.assertRaises(CortexDenied) as ctx:
            wrap_deepagents_tools(gate, ["read_file"])
        self.assertIn("not a Crew tool", str(ctx.exception))
        self.assertEqual(gate.executed, [])
        with self.assertRaises(CortexDenied):
            run_tool(gate, "ls", {})
        self.assertEqual(gate.executed, [])

    def test_deepagents_task_is_not_ungoverned_fanout(self) -> None:
        gate = FakeGate(True)
        with self.assertRaises(CortexDenied) as ctx:
            wrap_deepagents_tools(gate, ["export_pptx", "task"])
        self.assertIn("task", str(ctx.exception))
        self.assertEqual(gate.executed, [])

    def test_deepagents_write_todos_is_not_a_transcript(self) -> None:
        gate = FakeGate(True)
        with self.assertRaises(CortexDenied):
            run_tool(gate, "write_todos", {"todos": [{"prompt": "SECRET"}]})
        self.assertEqual(gate.executed, [])

    def test_deepagents_glob_grep_delete_are_not_crew_tools(self) -> None:
        gate = FakeGate(True)
        for name in ("glob", "grep", "delete"):
            with self.assertRaises(CortexDenied) as ctx:
                wrap_deepagents_tools(gate, ["export_pptx", name])
            self.assertIn("not a Crew tool", str(ctx.exception))
        self.assertEqual(gate.executed, [])


if __name__ == "__main__":
    unittest.main()
