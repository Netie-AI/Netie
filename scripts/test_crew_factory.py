#!/usr/bin/env python3
"""Factory WIP and parent-update. python3 scripts/test_crew_factory.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crew_factory import Factory, FactoryDenied, SliceDenied
from crew_verify import VerifyDenied


class CrewFactoryTests(unittest.TestCase):
    def test_prd_without_out_of_scope_refuses(self) -> None:
        f = Factory()
        with self.assertRaises(SliceDenied):
            f.slice_prd(
                prd_id="PRD-001",
                out_of_scope="",
                success_assertion="WHEN x THE SYSTEM SHALL y",
                epics=[("E1", "acl", "boundary")],
            )

    def test_orders_by_irreversibility_not_excitement(self) -> None:
        f = Factory()
        made = f.slice_prd(
            prd_id="PRD-001",
            out_of_scope="no second cortex",
            success_assertion="WHEN two Spaces share a warehouse THE SYSTEM SHALL abstain outside ACL",
            epics=[
                ("E-demo", "demo", "demo"),
                ("E-acl", "acl", "boundary"),
                ("E-found", "manifest", "foundation"),
            ],
        )
        self.assertEqual([e.id for e in made], ["E-found", "E-acl", "E-demo"])

    def test_same_run_cannot_close_ticket(self) -> None:
        f = Factory()
        f.slice_prd(
            prd_id="PRD-001",
            out_of_scope="palantir",
            success_assertion="WHEN x THE SYSTEM SHALL y",
            epics=[("E1", "acl", "boundary")],
        )
        f.activate_epic("E1")
        f.file_ticket(epic_id="E1", ticket_id="T1", prompt="wire space acl")
        with self.assertRaises(VerifyDenied):
            f.close_ticket(
                "T1",
                implementer_run_id="run-a",
                verifier_run_id="run-a",
                evidence="ok",
            )
        self.assertEqual(f.epics["E1"].tasks["T1"], "open")

    def test_close_updates_epic_task_list(self) -> None:
        f = Factory()
        f.slice_prd(
            prd_id="PRD-001",
            out_of_scope="palantir",
            success_assertion="WHEN x THE SYSTEM SHALL y",
            epics=[("E1", "acl", "boundary")],
        )
        f.activate_epic("E1")
        f.file_ticket(epic_id="E1", ticket_id="T1", prompt="wire space acl")
        line = f.close_ticket(
            "T1",
            implementer_run_id="run-a",
            verifier_run_id="run-b",
            evidence="two spaces abstain",
        )
        self.assertTrue(line.startswith("DONE"))
        self.assertEqual(f.epics["E1"].tasks["T1"], "done")
        self.assertIn("all tickets verified", f.maybe_complete_epic("E1"))
        self.assertEqual(f.epics["E1"].status, "done")

    def test_ticket_without_prompt_denied(self) -> None:
        f = Factory()
        f.slice_prd(
            prd_id="PRD-001",
            out_of_scope="x",
            success_assertion="WHEN x THE SYSTEM SHALL y",
            epics=[("E1", "acl", "boundary")],
        )
        f.activate_epic("E1")
        with self.assertRaises(FactoryDenied):
            f.file_ticket(epic_id="E1", ticket_id="T1", prompt="  ")

    def test_third_open_epic_is_wip_denied(self) -> None:
        f = Factory()
        f.slice_prd(
            prd_id="PRD-001",
            out_of_scope="x",
            success_assertion="WHEN x THE SYSTEM SHALL y",
            epics=[
                ("E1", "a", "foundation"),
                ("E2", "b", "boundary"),
                ("E3", "c", "capability"),
            ],
        )
        f.activate_epic("E1")
        f.activate_epic("E2")
        with self.assertRaises(FactoryDenied):
            f.activate_epic("E3")

    def test_index_does_not_leak_prompt(self) -> None:
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
        idx = f.index()
        dumped = str(idx)
        self.assertNotIn("SECRET-PROMPT-XYZ", dumped)
        self.assertNotIn("prompt", dumped)
        self.assertEqual(idx["tickets"][0]["id"], "T1")
        self.assertEqual(idx["tickets"][0]["status"], "open")


if __name__ == "__main__":
    unittest.main()
