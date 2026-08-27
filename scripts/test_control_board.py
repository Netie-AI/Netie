#!/usr/bin/env python3
"""Control is a view. python3 scripts/test_control_board.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from control_board import ControlDenied, project_board, run_dag
from crew_factory import Factory


class ControlBoardTests(unittest.TestCase):
    def test_projects_run_ledger_refusal(self) -> None:
        board = project_board(
            crew_index={"runs": [{"id": "p1", "status": "open", "ticket_id": "T1"}]},
            ledger_peek=[{"id": "L1", "status": "appended"}],
            refusals=[{"id": "R1", "reason": "manifest miss"}],
        )
        kinds = {c["kind"] for c in board["cards"]}
        self.assertEqual(kinds, {"run", "ledger", "refusal"})
        self.assertEqual(board["product"], "crew-board")

    def test_leaked_transcript_is_denied(self) -> None:
        with self.assertRaises(ControlDenied):
            project_board(
                crew_index={
                    "runs": [{"id": "p1", "status": "open", "transcript": "secret"}]
                },
                ledger_peek=[],
                refusals=[],
            )

    def test_no_dag_runner(self) -> None:
        with self.assertRaises(ControlDenied):
            run_dag("anything")

    def test_factory_index_projects_without_prompts(self) -> None:
        f = Factory()
        f.slice_prd(
            prd_id="PRD-001",
            out_of_scope="x",
            success_assertion="WHEN x THE SYSTEM SHALL y",
            epics=[("E1", "acl", "boundary")],
        )
        f.activate_epic("E1")
        f.file_ticket(
            epic_id="E1",
            ticket_id="T1",
            prompt="SECRET-PROMPT-XYZ wire space acl",
        )
        board = project_board(
            crew_index=f.index(),
            ledger_peek=[],
            refusals=[],
        )
        dumped = str(board)
        self.assertNotIn("SECRET-PROMPT-XYZ", dumped)
        self.assertNotIn("prompt", dumped)
        kinds = {c["kind"] for c in board["cards"]}
        self.assertEqual(kinds, {"epic", "ticket"})


if __name__ == "__main__":
    unittest.main()
