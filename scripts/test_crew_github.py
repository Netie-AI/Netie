#!/usr/bin/env python3
"""GitHub issue bodies stay out of child jobs. python3 scripts/test_crew_github.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crew_budget import TokenBudget
from crew_factory import Factory
from crew_github import IssueDenied, mint_issue, run_issue
from crew_tool_wrap import CortexDenied, CortexGate, Verdict


class _Gate:
    def check(self, tool: str, payload: dict) -> Verdict:
        if tool == "warehouse.query":
            return Verdict(False, "CortexDenied")
        return Verdict(True, "ok")

    def execute(self, tool: str, payload: dict) -> dict:
        return {"tool": tool}


class CrewGithubTests(unittest.TestCase):
    def _factory(self) -> Factory:
        f = Factory()
        f.slice_prd(
            prd_id="PRD-002",
            out_of_scope="openwork ee/",
            success_assertion="WHEN a ticket prompt leaks THE SYSTEM SHALL refuse",
            epics=[("E1", "runner", "boundary")],
        )
        f.activate_epic("E1")
        return f

    def test_mints_id_only_and_index_drops_title(self) -> None:
        f = self._factory()
        tid = mint_issue(
            f, epic_id="E1", number=61, title="acl wave", body="please wire space acl"
        )
        self.assertEqual(tid, "gh-61")
        idx = f.index()
        dumped = str(idx)
        self.assertNotIn("acl wave", dumped)
        self.assertNotIn("please wire", dumped)
        self.assertEqual(idx["tickets"][0]["id"], "gh-61")

    def test_skill_dump_issue_refuses(self) -> None:
        f = self._factory()
        with self.assertRaises(IssueDenied):
            mint_issue(
                f,
                epic_id="E1",
                number=2,
                title="skill",
                body="skill_body: SECRET",
            )

    def test_runner_does_not_copy_prompt_and_shows_refusal(self) -> None:
        f = self._factory()
        tid = mint_issue(f, epic_id="E1", number=7, title="export deck")
        gate: CortexGate = _Gate()
        budget = TokenBudget(max_tokens=10_000)
        with self.assertRaises(IssueDenied):
            run_issue(
                f,
                tid,
                gate=gate,
                tool="export_pptx",
                payload={"operator_confirm": True, "note": "export deck"},
                budget=budget,
            )
        failed = run_issue(
            f,
            tid,
            gate=gate,
            tool="warehouse.query",
            payload={"operator_confirm": True},
            budget=budget,
        )
        self.assertEqual(failed["status"], "FAILED")
        self.assertIn("CortexDenied", failed["refusal"])
        self.assertEqual(f.tickets[tid].status, "open")

    def test_payload_prompt_key_still_refuses(self) -> None:
        f = self._factory()
        tid = mint_issue(f, epic_id="E1", number=8, title="export deck")
        with self.assertRaises(CortexDenied):
            run_issue(
                f,
                tid,
                gate=_Gate(),
                tool="export_pptx",
                payload={"prompt": "do it", "operator_confirm": True},
                budget=TokenBudget(max_tokens=10_000),
            )


if __name__ == "__main__":
    unittest.main()
