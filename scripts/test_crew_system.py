#!/usr/bin/env python3
"""Factory + wrap + cap-2 parallel + verify compose. python3 scripts/test_crew_system.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crew_factory import Factory
from crew_ov_gate import OpenVaultCrewGate
from crew_parallel import Job, run_batch
from crew_runs import CrewGraph
from crew_tool_wrap import Verdict, wrap_deepagents_tools
from crew_verify import VerifyDenied


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


def _ov_allow(url: str, body: dict[str, Any]) -> dict[str, Any]:
    return {"allowed": True, "found": True}


class CrewSystemTests(unittest.TestCase):
    def test_composed_loop_stays_fail_closed(self) -> None:
        factory = Factory()
        factory.slice_prd(
            prd_id="PRD-001",
            out_of_scope="second cortex",
            success_assertion="WHEN two Spaces share a warehouse THE SYSTEM SHALL abstain",
            epics=[("E1", "acl", "boundary")],
        )
        factory.activate_epic("E1")
        factory.file_ticket(epic_id="E1", ticket_id="T1", prompt="wire space acl")

        ov = OpenVaultCrewGate("http://127.0.0.1:5000", post=_ov_allow)
        graph = CrewGraph(ov=ov)
        graph.open_parent("p1", "T1")
        graph.spawn_child(parent_id="p1", child_id="c1", deficit="need skill space.acl")

        gate = Gate()
        tools = wrap_deepagents_tools(gate, ["export_pptx", "warehouse.query"])
        with self.assertRaises(Exception):
            tools["warehouse.query"](sql="select 1")
        jobs = [
            Job("j1", "export_pptx", {}),
            Job("j2", "warehouse.query", {"sql": "select 1"}),
        ]
        results = run_batch(gate, jobs, max_in_flight=2)
        self.assertEqual([r.status for r in results], ["DONE", "FAILED"])
        self.assertEqual(gate.executed, ["export_pptx"])

        with self.assertRaises(VerifyDenied):
            factory.close_ticket(
                "T1",
                implementer_run_id="p1",
                verifier_run_id="p1",
                evidence="nope",
            )
        line = factory.close_ticket(
            "T1",
            implementer_run_id="p1",
            verifier_run_id="v1",
            evidence="acl holds",
        )
        self.assertTrue(line.startswith("DONE"))
        self.assertEqual(factory.epics["E1"].tasks["T1"], "done")


if __name__ == "__main__":
    unittest.main()
