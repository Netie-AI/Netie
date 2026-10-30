#!/usr/bin/env python3
"""Crew resume is ids-only. python3 scripts/test_crew_durable.py"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crew_checkpoint import CheckpointDenied
from crew_durable import load_disk, persist, resume
from crew_ov_gate import OpenVaultCrewGate
from crew_runs import CrewGraph
from crew_skills import SkillRegistry, register_skill
from control_board import project_board


def _allow(url: str, body: dict[str, Any]) -> dict[str, Any]:
    return {"allowed": True, "found": True, "parent_run_id": body["parent_run_id"]}


class CrewDurableTests(unittest.TestCase):
    def test_process_death_restores_ids_not_prompt(self) -> None:
        ov = OpenVaultCrewGate("http://127.0.0.1:5000", post=_allow)
        live = CrewGraph(ov=ov)
        live.open_parent("p1", "T1")
        live.spawn_child(parent_id="p1", child_id="c1", deficit="need skill x")
        live.runs["c1"].transcript = "SECRET-TRANSCRIPT"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "crew.json"
            persist(path, live)
            dumped = path.read_text(encoding="utf-8")
            self.assertNotIn("SECRET-TRANSCRIPT", dumped)
            self.assertNotIn("need skill x", dumped)
            blob = load_disk(path)
        dead = CrewGraph(ov=OpenVaultCrewGate("http://127.0.0.1:5000", post=_allow))
        resume(dead, blob, tickets={"T1": "need skill x"})
        self.assertEqual({r.id for r in dead.runs.values()}, {"p1", "c1"})
        self.assertEqual(dead.runs["c1"].transcript, "")
        self.assertEqual(dead.runs["p1"].ticket_id, "T1")

    def test_resume_without_ticket_source_refuses(self) -> None:
        ov = OpenVaultCrewGate("http://127.0.0.1:5000", post=_allow)
        live = CrewGraph(ov=ov)
        live.open_parent("p1", "T1")
        live.spawn_child(parent_id="p1", child_id="c1", deficit="need skill x")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "crew.json"
            blob = persist(path, live)
        dead = CrewGraph(ov=OpenVaultCrewGate("http://127.0.0.1:5000", post=_allow))
        with self.assertRaises(CheckpointDenied):
            resume(dead, blob, tickets={})

    def test_disk_body_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "crew.json"
            path.write_text(
                json.dumps({"runs": [{"id": "p1", "status": "open", "prompt": "nope"}]}),
                encoding="utf-8",
            )
            with self.assertRaises(CheckpointDenied):
                load_disk(path)

    def test_resume_restores_skill_ids(self) -> None:
        live_reg = SkillRegistry()
        register_skill(live_reg, "S-0004")
        ov = OpenVaultCrewGate(
            "http://127.0.0.1:5000", post=_allow, registry=live_reg
        )
        live = CrewGraph(ov=ov)
        live.open_parent("p1", "T1")
        live.spawn_child(
            parent_id="p1",
            child_id="c1",
            deficit="need export",
            kind="skill",
            resource_id="S-0004",
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "crew.json"
            blob = persist(path, live, live_reg)
            dumped = path.read_text(encoding="utf-8")
        self.assertIn("S-0004", dumped)
        self.assertNotIn("skill_body", dumped)
        board = project_board(crew_index=blob, ledger_peek=[], refusals=[])
        skill = [c for c in board["cards"] if c["kind"] == "skill"][0]
        self.assertEqual(skill["id"], "S-0004")
        dead_reg = SkillRegistry()
        dead = CrewGraph(
            ov=OpenVaultCrewGate(
                "http://127.0.0.1:5000", post=_allow, registry=dead_reg
            )
        )
        resume(dead, blob, tickets={"T1": "need export"}, registry=dead_reg)
        self.assertTrue(dead_reg.has("S-0004"))
        child = dead.spawn_child(
            parent_id="p1",
            child_id="c2",
            deficit="need export again",
            kind="skill",
            resource_id="S-0004",
        )
        self.assertEqual(child.id, "c2")

    def test_persist_defaults_to_ov_registry(self) -> None:
        live_reg = SkillRegistry()
        register_skill(live_reg, "S-0004")
        live = CrewGraph(
            ov=OpenVaultCrewGate(
                "http://127.0.0.1:5000", post=_allow, registry=live_reg
            )
        )
        live.open_parent("p1", "T1")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "crew.json"
            blob = persist(path, live)
        self.assertEqual(blob["skills"], [{"id": "S-0004", "source": "netie-kb"}])
        dead_reg = SkillRegistry()
        dead = CrewGraph(
            ov=OpenVaultCrewGate(
                "http://127.0.0.1:5000", post=_allow, registry=dead_reg
            )
        )
        resume(dead, blob, tickets={"T1": "need export"})
        self.assertTrue(dead_reg.has("S-0004"))


if __name__ == "__main__":
    unittest.main()
