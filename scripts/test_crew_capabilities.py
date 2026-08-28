#!/usr/bin/env python3
"""OpenWork capability MCP: ungranted never runs. python3 scripts/test_crew_capabilities.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crew_capabilities import execute_capability, search_capabilities
from crew_tool_wrap import CortexDenied, Verdict


class FakeGate:
    def __init__(self, allowed: bool = True) -> None:
        self.allowed = allowed
        self.executed: list[str] = []

    def check(self, tool: str, payload: dict[str, Any]) -> Verdict:
        return Verdict(allowed=self.allowed, reason="manifest miss")

    def execute(self, tool: str, payload: dict[str, Any]) -> Any:
        self.executed.append(tool)
        return {"ok": True, "tool": tool}


class CrewCapabilityTests(unittest.TestCase):
    def test_search_lists_granted_ids_only(self) -> None:
        out = search_capabilities(["warehouse.query", "export_pptx", "read_file"])
        self.assertEqual(out, ["export_pptx", "warehouse.query"])
        self.assertNotIn("read_file", out)

    def test_ungranted_does_not_execute(self) -> None:
        gate = FakeGate()
        with self.assertRaises(CortexDenied) as ctx:
            execute_capability(
                gate, "warehouse.delete", {}, granted=["warehouse.query"]
            )
        self.assertIn("not granted", str(ctx.exception))
        self.assertEqual(gate.executed, [])

    def test_granted_write_needs_hitl(self) -> None:
        gate = FakeGate()
        with self.assertRaises(CortexDenied) as ctx:
            execute_capability(
                gate, "item.intake", {"sku": "A"}, granted=["item.intake"]
            )
        self.assertIn("HITL", str(ctx.exception))
        self.assertEqual(gate.executed, [])
        out = execute_capability(
            gate,
            "item.intake",
            {"sku": "A", "operator_confirm": True},
            granted=["item.intake"],
        )
        self.assertEqual(out["tool"], "item.intake")
        self.assertEqual(gate.executed, ["item.intake"])

    def test_builtin_and_bypass_never_list_or_run(self) -> None:
        gate = FakeGate()
        self.assertEqual(search_capabilities(["task", "grok-bot", "cursor-ui"]), [])
        with self.assertRaises(CortexDenied) as ctx:
            execute_capability(gate, "task", {}, granted=["task"])
        self.assertIn("not a Crew tool", str(ctx.exception))
        with self.assertRaises(CortexDenied) as ctx:
            execute_capability(gate, "pointer-drive", {}, granted=["pointer-drive"])
        self.assertIn("billing-bypass", str(ctx.exception))
        self.assertEqual(gate.executed, [])

    def test_skill_body_does_not_execute(self) -> None:
        gate = FakeGate()
        with self.assertRaises(CortexDenied):
            execute_capability(
                gate,
                "warehouse.query",
                {"skill_body": "SECRET"},
                granted=["warehouse.query"],
            )
        self.assertEqual(gate.executed, [])

    def test_leave_machine_needs_openvault(self) -> None:
        gate = FakeGate()
        with self.assertRaises(CortexDenied) as ctx:
            execute_capability(
                gate, "open_url", {}, granted=["open_url"], ov_allowed=False
            )
        self.assertIn("OpenVault", str(ctx.exception))
        self.assertEqual(gate.executed, [])
        out = execute_capability(
            gate, "open_url", {}, granted=["open_url"], ov_allowed=True
        )
        self.assertEqual(out["tool"], "open_url")


if __name__ == "__main__":
    unittest.main()
