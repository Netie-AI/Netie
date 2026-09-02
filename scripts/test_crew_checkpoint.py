#!/usr/bin/env python3
"""Checkpoints are ids-only. python3 scripts/test_crew_checkpoint.py"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crew_checkpoint import (
    CheckpointDenied,
    checkpoint_graph,
    load_checkpoint,
    save_checkpoint,
    summarise,
)
from crew_ov_gate import OpenVaultCrewGate
from crew_runs import CrewGraph


def _allow(url: str, body: dict[str, Any]) -> dict[str, Any]:
    return {"allowed": True, "found": True, "parent_run_id": body["parent_run_id"]}


class CrewCheckpointTests(unittest.TestCase):
    def test_checkpoint_drops_transcript(self) -> None:
        g = CrewGraph(ov=OpenVaultCrewGate("http://127.0.0.1:5000", post=_allow))
        g.open_parent("p1", "T1")
        g.spawn_child(parent_id="p1", child_id="c1", deficit="need skill x")
        g.runs["c1"].transcript = "SECRET-TRANSCRIPT-XYZ"
        blob = checkpoint_graph(g)
        dumped = json.dumps(blob)
        self.assertNotIn("SECRET-TRANSCRIPT-XYZ", dumped)
        self.assertNotIn("transcript", dumped)
        self.assertNotIn("need skill x", dumped)
        self.assertEqual({r["id"] for r in blob["runs"]}, {"p1", "c1"})
        self.assertEqual(blob["skills"], [])

    def test_checkpoint_keeps_skill_ids_not_bodies(self) -> None:
        from crew_skills import SkillRegistry, register_skill

        g = CrewGraph(ov=OpenVaultCrewGate("http://127.0.0.1:5000", post=_allow))
        g.open_parent("p1", "T1")
        reg = SkillRegistry()
        register_skill(reg, "S-0004")
        blob = checkpoint_graph(g, reg)
        self.assertEqual(blob["skills"], [{"id": "S-0004", "source": "netie-kb"}])
        self.assertNotIn("skill_body", json.dumps(blob))
        with self.assertRaises(CheckpointDenied):
            save_checkpoint(
                {
                    "runs": [{"id": "p1", "status": "open"}],
                    "skills": [
                        {"id": "S-0001", "source": "netie-kb", "skill_body": "SECRET"}
                    ],
                }
            )

    def test_load_refuses_a_body(self) -> None:
        with self.assertRaises(CheckpointDenied):
            load_checkpoint(
                {
                    "runs": [{"id": "p1", "status": "open", "transcript": "nope"}],
                    "todos": [],
                }
            )

    def test_summarise_is_counts_not_conversation(self) -> None:
        idx = {
            "runs": [
                {"id": "p1", "status": "open", "ticket_id": "T1"},
                {"id": "c1", "status": "done", "parent_id": "p1", "ticket_id": "T1"},
            ]
        }
        out = summarise(idx)
        self.assertEqual(out["open"], 1)
        self.assertEqual(out["done"], 1)
        self.assertEqual(out["tokens"], "ids-only")
        self.assertNotIn("transcript", json.dumps(out))
        with self.assertRaises(CheckpointDenied):
            summarise({"runs": [{"id": "p1", "prompt": "SECRET"}]})

    def test_save_refuses_todo_prompt(self) -> None:
        with self.assertRaises(CheckpointDenied):
            save_checkpoint(
                {"runs": [{"id": "p1", "status": "open"}]},
                todos=[{"id": "t1", "prompt": "SECRET"}],
            )


if __name__ == "__main__":
    unittest.main()
