#!/usr/bin/env python3
"""PRD-002: Cortex refusal on the board, ticket stays open."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from control_board import ControlDenied
from crew_budget import TokenBudget
from crew_factory import Factory
from crew_ov_gate import OpenVaultCrewGate
from crew_runner import board_from_runs, run_open_ticket
from crew_runs import CrewGraph
from crew_skills import SkillRegistry, register_skill
from crew_tool_wrap import CortexDenied, Verdict


ROOM = TokenBudget(max_tokens=10_000)


class Gate:
    def __init__(self) -> None:
        self.executed: list[str] = []

    def check(self, tool: str, payload: dict[str, Any]) -> Verdict:
        if tool == "warehouse.query":
            return Verdict(allowed=False, reason="manifest miss")
        return Verdict(allowed=True)

    def execute(self, tool: str, payload: dict[str, Any]) -> Any:
        self.executed.append(tool)
        return {"tool": tool}


def _factory() -> Factory:
    f = Factory()
    f.slice_prd(
        prd_id="PRD-001",
        out_of_scope="second cortex",
        success_assertion="WHEN x THE SYSTEM SHALL y",
        epics=[("E1", "acl", "boundary")],
    )
    f.activate_epic("E1")
    f.file_ticket(
        epic_id="E1",
        ticket_id="T1",
        prompt="SECRET-PROMPT-XYZ wire space acl",
    )
    return f


class CrewRunnerTests(unittest.TestCase):
    def test_cortex_refusal_on_board_ticket_stays_open(self) -> None:
        f = _factory()
        gate = Gate()
        result = run_open_ticket(
            f,
            "T1",
            gate=gate,
            tool="warehouse.query",
            payload={"sql": "select 1"},
            budget=ROOM,
        )
        self.assertEqual(result["status"], "FAILED")
        self.assertIn("manifest miss", result["refusal"])
        self.assertEqual(gate.executed, [])
        self.assertEqual(f.tickets["T1"].status, "open")
        board = board_from_runs(f, [result])
        dumped = str(board)
        self.assertNotIn("SECRET-PROMPT-XYZ", dumped)
        self.assertNotIn("prompt", dumped)
        reasons = [c.get("reason") for c in board["cards"] if c["kind"] == "refusal"]
        self.assertTrue(any("manifest miss" in str(r) for r in reasons))
        kinds = {c["kind"] for c in board["cards"]}
        self.assertIn("ticket", kinds)
        self.assertIn("epic", kinds)
        self.assertNotIn("skill", kinds)

    def test_write_without_hitl_does_not_execute(self) -> None:
        f = _factory()
        gate = Gate()
        result = run_open_ticket(
            f,
            "T1",
            gate=gate,
            tool="export_pptx",
            payload={},
            budget=ROOM,
        )
        self.assertEqual(result["status"], "FAILED")
        self.assertIn("HITL", result["refusal"])
        self.assertEqual(gate.executed, [])
        self.assertEqual(f.tickets["T1"].status, "open")

    def test_confirmed_write_still_leaves_ticket_open(self) -> None:
        f = _factory()
        gate = Gate()
        result = run_open_ticket(
            f,
            "T1",
            gate=gate,
            tool="export_pptx",
            payload={"operator_confirm": True},
            budget=ROOM,
        )
        self.assertEqual(result["status"], "DONE")
        self.assertEqual(gate.executed, ["export_pptx"])
        self.assertEqual(f.tickets["T1"].status, "open")

    def test_prompt_in_payload_refuses(self) -> None:
        f = _factory()
        gate = Gate()
        with self.assertRaises(CortexDenied):
            run_open_ticket(
                f,
                "T1",
                gate=gate,
                tool="warehouse.query",
                payload={"prompt": "SECRET-PROMPT-XYZ"},
            )
        self.assertEqual(gate.executed, [])

    def test_ticket_without_budget_refuses(self) -> None:
        f = _factory()
        gate = Gate()
        with self.assertRaises(CortexDenied) as ctx:
            run_open_ticket(
                f,
                "T1",
                gate=gate,
                tool="export_pptx",
                payload={"operator_confirm": True},
            )
        self.assertIn("token budget", str(ctx.exception))
        self.assertEqual(gate.executed, [])
        self.assertEqual(f.tickets["T1"].status, "open")

    def test_over_budget_ticket_stays_open(self) -> None:
        f = _factory()
        gate = Gate()
        budget = TokenBudget(max_tokens=40)
        ok = run_open_ticket(
            f,
            "T1",
            gate=gate,
            tool="export_pptx",
            payload={"operator_confirm": True, "blob": "x" * 80},
            budget=budget,
        )
        self.assertEqual(ok["status"], "DONE")
        second = run_open_ticket(
            f,
            "T1",
            gate=gate,
            tool="export_pptx",
            payload={"operator_confirm": True, "blob": "y" * 80},
            budget=budget,
        )
        self.assertEqual(second["status"], "FAILED")
        self.assertIn("budget", second["refusal"])
        self.assertEqual(gate.executed, ["export_pptx"])
        self.assertEqual(f.tickets["T1"].status, "open")

    def test_board_from_runs_projects_skill_ids(self) -> None:
        f = _factory()
        gate = Gate()
        result = run_open_ticket(
            f,
            "T1",
            gate=gate,
            tool="warehouse.query",
            payload={"sql": "select 1"},
            budget=ROOM,
        )
        reg = SkillRegistry()
        register_skill(reg, "S-0004")
        board = board_from_runs(f, [result], registry=reg)
        dumped = str(board)
        self.assertNotIn("SECRET-PROMPT-XYZ", dumped)
        self.assertNotIn("prompt", dumped)
        self.assertNotIn("skill_body", dumped)
        skill = [c for c in board["cards"] if c["kind"] == "skill"][0]
        self.assertEqual(skill["id"], "S-0004")
        self.assertEqual(skill["source"], "netie-kb")
        reasons = [c.get("reason") for c in board["cards"] if c["kind"] == "refusal"]
        self.assertTrue(any("manifest miss" in str(r) for r in reasons))

    def test_board_from_runs_defaults_to_ov_registry(self) -> None:
        f = _factory()
        live_reg = SkillRegistry()
        register_skill(live_reg, "S-0004")
        graph = CrewGraph(
            ov=OpenVaultCrewGate(
                "http://127.0.0.1:5000",
                post=lambda url, body: {"allowed": True},
                registry=live_reg,
            )
        )
        graph.open_parent("p1", "T1")
        board = board_from_runs(f, [], graph=graph)
        kinds = {c["kind"] for c in board["cards"]}
        self.assertEqual(kinds, {"run", "ticket", "epic", "skill"})
        skill = [c for c in board["cards"] if c["kind"] == "skill"][0]
        self.assertEqual(skill["id"], "S-0004")
        run = [c for c in board["cards"] if c["kind"] == "run"][0]
        self.assertEqual(run["id"], "p1")
        self.assertNotIn("SECRET-PROMPT-XYZ", str(board))

    def test_board_from_runs_refuses_a_skill_body(self) -> None:
        f = _factory()

        class Dirty:
            def index(self) -> list[dict[str, str]]:
                return [
                    {
                        "id": "S-0001",
                        "source": "netie-kb",
                        "skill_body": "SECRET",
                    }
                ]

        with self.assertRaises(ControlDenied):
            board_from_runs(f, [], registry=Dirty())  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
