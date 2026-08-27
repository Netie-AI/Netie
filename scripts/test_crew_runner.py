#!/usr/bin/env python3
"""PRD-002: Cortex refusal on the board, ticket stays open."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crew_factory import Factory
from crew_runner import board_from_runs, run_open_ticket
from crew_tool_wrap import CortexDenied, Verdict


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

    def test_write_without_hitl_does_not_execute(self) -> None:
        f = _factory()
        gate = Gate()
        result = run_open_ticket(
            f,
            "T1",
            gate=gate,
            tool="export_pptx",
            payload={},
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


if __name__ == "__main__":
    unittest.main()
