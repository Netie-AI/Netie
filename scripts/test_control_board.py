#!/usr/bin/env python3
"""Control is a view. python3 scripts/test_control_board.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from control_board import (
    ControlDenied,
    MAX_BOARD_CHARS,
    board_index,
    project_board,
    project_session,
    run_dag,
)
from crew_factory import Factory
from crew_skills import SkillRegistry, register_skill


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

    def test_kb_skill_index_is_a_card_without_body(self) -> None:
        board = project_board(
            crew_index={
                "runs": [],
                "skills": [{"id": "S-0004", "source": "netie-kb"}],
            },
            ledger_peek=[],
            refusals=[],
        )
        skill = [c for c in board["cards"] if c["kind"] == "skill"][0]
        self.assertEqual(skill["id"], "S-0004")
        self.assertEqual(skill["source"], "netie-kb")
        with self.assertRaises(ControlDenied):
            project_board(
                crew_index={
                    "skills": [
                        {"id": "S-0001", "source": "netie-kb", "skill_body": "SECRET"}
                    ]
                },
                ledger_peek=[],
                refusals=[],
            )

    def test_board_index_stitches_factory_and_skills(self) -> None:
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
        reg = SkillRegistry()
        register_skill(reg, "S-0004")
        idx = board_index(
            graph_index={"runs": [{"id": "p1", "status": "open", "ticket_id": "T1"}]},
            factory_index=f.index(),
            skills=reg.index(),
        )
        dumped = str(idx)
        self.assertNotIn("SECRET-PROMPT-XYZ", dumped)
        self.assertNotIn("prompt", dumped)
        self.assertNotIn("skill_body", dumped)
        board = project_board(crew_index=idx, ledger_peek=[], refusals=[])
        kinds = {c["kind"] for c in board["cards"]}
        self.assertEqual(kinds, {"run", "ticket", "epic", "skill"})
        with self.assertRaises(ControlDenied):
            board_index(
                skills=[{"id": "S-0001", "source": "netie-kb", "skill_body": "SECRET"}]
            )

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

    def test_session_has_no_transcript(self) -> None:
        session = project_session(
            run={"id": "p1", "status": "open", "ticket_id": "T1"},
            todos=[{"id": "todo-1", "status": "open"}],
            permissions=["warehouse.query"],
            handoff={"id": "h1"},
        )
        self.assertEqual(session["product"], "crew-session")
        self.assertEqual(session["run_id"], "p1")
        self.assertEqual(session["handoff_id"], "h1")
        self.assertEqual(session["permissions"], ["warehouse.query"])
        self.assertNotIn("transcript", str(session))
        with self.assertRaises(ControlDenied):
            project_session(
                run={
                    "id": "p1",
                    "status": "open",
                    "ticket_id": "T1",
                    "transcript": "secret",
                },
                todos=[],
                permissions=[],
            )

    def test_session_drops_builtin_permissions(self) -> None:
        session = project_session(
            run={"id": "p1", "status": "open", "ticket_id": "T1"},
            todos=[],
            permissions=["warehouse.query", "read_file", "grok-bot"],
        )
        self.assertEqual(session["permissions"], ["warehouse.query"])

    def test_rdp_card_is_not_guacamole(self) -> None:
        with self.assertRaises(ControlDenied) as ctx:
            project_board(
                crew_index={
                    "runs": [{"id": "p1", "status": "open", "kind": "rdp"}]
                },
                ledger_peek=[],
                refusals=[],
            )
        self.assertIn("Guacamole", str(ctx.exception))

    def test_ssh_card_is_guacamole_class(self) -> None:
        with self.assertRaises(ControlDenied) as ctx:
            project_board(
                crew_index={
                    "runs": [{"id": "p1", "status": "open", "kind": "ssh"}]
                },
                ledger_peek=[],
                refusals=[],
            )
        self.assertIn("Guacamole", str(ctx.exception))
        with self.assertRaises(ControlDenied):
            project_session(
                run={"id": "p1", "status": "open", "ticket_id": "T1", "kind": "telnet"},
                todos=[],
                permissions=[],
            )

    def test_over_budget_board_refuses(self) -> None:
        with self.assertRaises(ControlDenied) as ctx:
            project_board(
                crew_index={
                    "runs": [{"id": "p1", "status": "open", "ticket_id": "T1"}]
                },
                ledger_peek=[],
                refusals=[],
                max_chars=1,
            )
        self.assertIn("DitchContext", str(ctx.exception))
        with self.assertRaises(ControlDenied) as ctx:
            project_session(
                run={"id": "p1", "status": "open", "ticket_id": "T1"},
                todos=[],
                permissions=[],
                max_chars=1,
            )
        self.assertIn("DitchContext", str(ctx.exception))
        self.assertEqual(MAX_BOARD_CHARS, 12000)


if __name__ == "__main__":
    unittest.main()
