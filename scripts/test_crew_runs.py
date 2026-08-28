#!/usr/bin/env python3
"""Parent owns the task. python3 scripts/test_crew_runs.py"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crew_ov_gate import OpenVaultCrewGate
from crew_runs import CrewGraph, ParentDropped, WipDenied
from crew_tool_wrap import CortexDenied
from crew_verify import VerifyDenied


def _allow(url: str, body: dict[str, Any]) -> dict[str, Any]:
    return {"allowed": True, "found": True, "parent_run_id": body["parent_run_id"]}


def _deny(url: str, body: dict[str, Any]) -> dict[str, Any]:
    return {"allowed": False, "reason": "leave refused"}


def _graph(post=_allow) -> CrewGraph:
    return CrewGraph(ov=OpenVaultCrewGate("http://127.0.0.1:5000", post=post))


class CrewRunsTests(unittest.TestCase):
    def test_third_parent_is_wip_denied(self) -> None:
        g = _graph()
        g.open_parent("p1", "T1")
        g.open_parent("p2", "T2")
        with self.assertRaises(WipDenied):
            g.open_parent("p3", "T3")

    def test_child_without_deficit_does_not_spawn(self) -> None:
        g = _graph()
        g.open_parent("p1", "T1")
        with self.assertRaises(CortexDenied):
            g.spawn_child(parent_id="p1", child_id="c1", deficit="  ")
        self.assertEqual(list(g.runs), ["p1"])

    def test_ov_refuse_does_not_create_child(self) -> None:
        g = _graph(post=_deny)
        g.open_parent("p1", "T1")
        with self.assertRaises(CortexDenied):
            g.spawn_child(parent_id="p1", child_id="c1", deficit="need skill x")
        self.assertNotIn("c1", g.runs)
        self.assertEqual(g.runs["p1"].status, "open")

    def test_skill_kind_does_not_spawn(self) -> None:
        g = _graph()
        g.open_parent("p1", "T1")
        with self.assertRaises(CortexDenied) as ctx:
            g.spawn_child(
                parent_id="p1",
                child_id="c1",
                deficit="need x",
                kind="skill",
            )
        self.assertIn("no skill registered", str(ctx.exception))
        self.assertNotIn("c1", g.runs)

    def test_child_does_not_replace_parent(self) -> None:
        g = _graph()
        g.open_parent("p1", "T1")
        g.spawn_child(parent_id="p1", child_id="c1", deficit="need skill x")
        g.runs["c1"].transcript = "child ramble MUST-NOT-LEAK"
        idx = g.index()
        dumped = json.dumps(idx)
        self.assertEqual(g.runs["p1"].status, "open")
        self.assertEqual({r["id"] for r in idx["runs"]}, {"p1", "c1"})
        self.assertNotIn("MUST-NOT-LEAK", dumped)
        self.assertNotIn("need skill x", dumped)

    def test_cannot_finish_parent_with_open_child(self) -> None:
        g = _graph()
        g.open_parent("p1", "T1")
        g.spawn_child(parent_id="p1", child_id="c1", deficit="need skill x")
        with self.assertRaises(ParentDropped):
            g.finish_parent(
                "p1",
                implementer_run_id="run-a",
                verifier_run_id="run-b",
                evidence="ok",
            )

    def test_same_run_cannot_close_parent(self) -> None:
        g = _graph()
        g.open_parent("p1", "T1")
        with self.assertRaises(VerifyDenied):
            g.finish_parent(
                "p1",
                implementer_run_id="run-a",
                verifier_run_id="run-a",
                evidence="ok",
            )
        self.assertEqual(g.runs["p1"].status, "open")

    def test_finish_parent_after_child_and_other_run(self) -> None:
        g = _graph()
        g.open_parent("p1", "T1")
        g.spawn_child(parent_id="p1", child_id="c1", deficit="need skill x")
        g.finish_child("c1")
        out = g.finish_parent(
            "p1",
            implementer_run_id="run-a",
            verifier_run_id="run-b",
            evidence="rows match",
        )
        self.assertEqual(out.status, "done")


if __name__ == "__main__":
    unittest.main()
