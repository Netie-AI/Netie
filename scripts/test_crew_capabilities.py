#!/usr/bin/env python3
"""OpenWork capability MCP: ungranted never runs. python3 scripts/test_crew_capabilities.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crew_budget import BudgetDenied, TokenBudget
from crew_capabilities import (
    execute_capabilities,
    execute_capability,
    load_den,
    search_capabilities,
)
from crew_parallel import Job
from crew_tool_wrap import CortexDenied, Verdict


ROOM = TokenBudget(max_tokens=10_000)


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
                gate, "item.intake", {"sku": "A"}, granted=["item.intake"], budget=ROOM
            )
        self.assertIn("HITL", str(ctx.exception))
        self.assertEqual(gate.executed, [])
        out = execute_capability(
            gate,
            "item.intake",
            {"sku": "A", "operator_confirm": True},
            granted=["item.intake"],
            budget=ROOM,
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
            gate, "open_url", {}, granted=["open_url"], ov_allowed=True, budget=ROOM
        )
        self.assertEqual(out["tool"], "open_url")

    def test_leave_machine_ov_posts_skill_ids(self) -> None:
        from crew_ov_gate import OpenVaultCrewGate
        from crew_skills import SkillRegistry, register_skill

        gate = FakeGate()
        seen: list[dict[str, Any]] = []

        def post(url: str, body: dict[str, Any]) -> dict[str, Any]:
            seen.append(body)
            return {"allowed": True}

        reg = SkillRegistry()
        register_skill(reg, "S-0004")
        ov = OpenVaultCrewGate("http://127.0.0.1:5000", post=post, registry=reg)
        with self.assertRaises(CortexDenied) as missing:
            execute_capability(
                gate,
                "open_url",
                {},
                granted=["open_url"],
                ov=ov,
                budget=ROOM,
            )
        self.assertIn("parent and child", str(missing.exception))
        self.assertEqual(seen, [])
        self.assertEqual(gate.executed, [])
        out = execute_capability(
            gate,
            "open_url",
            {},
            granted=["open_url"],
            ov=ov,
            parent_run_id="p1",
            child_id="c1",
            budget=ROOM,
        )
        self.assertEqual(out["tool"], "open_url")
        self.assertEqual(seen[0]["skill_ids"], ["S-0004"])
        self.assertEqual(seen[0]["kind"], "service")
        self.assertNotIn("skill_body", str(seen[0]))

    def test_leave_machine_ov_refuse_does_not_execute(self) -> None:
        from crew_ov_gate import OpenVaultCrewGate

        gate = FakeGate()

        def post(url: str, body: dict[str, Any]) -> dict[str, Any]:
            return {"allowed": False, "reason": "vault miss"}

        ov = OpenVaultCrewGate("http://127.0.0.1:5000", post=post)
        with self.assertRaises(CortexDenied) as ctx:
            execute_capability(
                gate,
                "open_url",
                {},
                granted=["open_url"],
                ov=ov,
                parent_run_id="p1",
                child_id="c1",
                budget=ROOM,
            )
        self.assertIn("vault miss", str(ctx.exception))
        self.assertEqual(gate.executed, [])

    def test_granted_without_budget_refuses(self) -> None:
        gate = FakeGate()
        with self.assertRaises(CortexDenied) as ctx:
            execute_capability(
                gate, "warehouse.query", {}, granted=["warehouse.query"]
            )
        self.assertIn("token budget", str(ctx.exception))
        self.assertEqual(gate.executed, [])

    def test_over_budget_capability_does_not_execute(self) -> None:
        gate = FakeGate()
        budget = TokenBudget(max_tokens=40)
        execute_capability(
            gate,
            "warehouse.query",
            {"blob": "x" * 80},
            granted=["warehouse.query"],
            budget=budget,
        )
        with self.assertRaises(BudgetDenied):
            execute_capability(
                gate,
                "warehouse.query",
                {"blob": "y" * 80},
                granted=["warehouse.query"],
                budget=budget,
            )
        self.assertEqual(gate.executed, ["warehouse.query"])

    def test_batch_caps_at_two_and_ungranted_does_not_execute(self) -> None:
        gate = FakeGate()
        with self.assertRaises(ValueError):
            execute_capabilities(
                gate,
                [Job("a", "warehouse.query", {})],
                granted=["warehouse.query"],
                max_in_flight=3,
                budget=ROOM,
            )
        jobs = [
            Job("a", "warehouse.query", {}),
            Job("b", "warehouse.delete", {}),
            Job("c", "export_pptx", {"operator_confirm": True}),
        ]
        results = execute_capabilities(
            gate,
            jobs,
            granted=["warehouse.query", "export_pptx"],
            max_in_flight=1,
            budget=ROOM,
        )
        self.assertEqual([r.status for r in results], ["DONE", "FAILED", "DONE"])
        self.assertIn("not granted", results[1].detail)
        self.assertEqual(gate.executed, ["warehouse.query", "export_pptx"])

    def test_openwork_ee_is_not_a_den(self) -> None:
        with self.assertRaises(CortexDenied) as ctx:
            load_den("different-ai/openwork/ee/")
        self.assertIn("ee/", str(ctx.exception))
        with self.assertRaises(CortexDenied) as ctx:
            load_den("crew_capabilities")
        self.assertIn("search_capabilities", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
