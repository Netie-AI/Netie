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


if __name__ == "__main__":
    unittest.main()
