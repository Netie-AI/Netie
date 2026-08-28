#!/usr/bin/env python3
"""JEPA is off the Cortex path. python3 scripts/test_cortex_path.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cortex_path import RouteDenied, auto_route, run_question


class CortexPathTests(unittest.TestCase):
    def test_jepa_candidate_is_refused(self) -> None:
        with self.assertRaises(RouteDenied):
            auto_route(cosine=0.9, winner_runs=9, candidates=["jepa", "minimal"])

    def test_gen_cfsm_candidate_is_refused(self) -> None:
        with self.assertRaises(RouteDenied):
            auto_route(cosine=0.9, winner_runs=9, candidates=["gen-cfsm"])

    def test_live_route_names_keyword_cascade(self) -> None:
        out = run_question("dag", write="export_pptx", actor="ops", verified=True)
        self.assertEqual(out["router"], "race_router.auto_route")
        self.assertEqual(out["dms"], "keyword_cascade")
        self.assertEqual(out["c7_sql"], "off")
        self.assertEqual(out["jepa"], "off-path")
        self.assertEqual(out["write"], "export_pptx")
        self.assertEqual(out["actor"], "ops")
        self.assertEqual(out["verified"], "true")

    def test_item_intake_is_a_governed_write(self) -> None:
        out = run_question("dag", write="item.intake", actor="ops", verified=True)
        self.assertEqual(out["write"], "item.intake")
        with self.assertRaises(RouteDenied) as ctx:
            run_question("dag", write="item.intake", verified=True)
        self.assertIn("actor", str(ctx.exception))

    def test_ungoverned_write_denied(self) -> None:
        with self.assertRaises(RouteDenied):
            run_question("dag", write="warehouse.delete", actor="ops", verified=True)

    def test_anonymous_write_denied(self) -> None:
        with self.assertRaises(RouteDenied) as ctx:
            run_question("dag", write="export_pptx", verified=True)
        self.assertIn("actor", str(ctx.exception))

    def test_unverified_answer_denied(self) -> None:
        with self.assertRaises(RouteDenied) as ctx:
            run_question("dag", actor="ops")
        self.assertIn("verified", str(ctx.exception))

    def test_a2a_is_dms_pack_only(self) -> None:
        with self.assertRaises(RouteDenied) as ctx:
            run_question("dag", verified=True, a2a=True)
        self.assertIn("dms-pack", str(ctx.exception))
        out = run_question("dag", verified=True, pack="dms", a2a=True)
        self.assertEqual(out["pack"], "dms")

    def test_web_tool_must_use_tool_runner(self) -> None:
        with self.assertRaises(RouteDenied) as ctx:
            run_question(
                "dag", tool="web_search", via_tool_runner=False, verified=True
            )
        self.assertIn("tool_runner", str(ctx.exception))
        out = run_question(
            "dag", tool="web_search", via_tool_runner=True, verified=True
        )
        self.assertEqual(out["tool"], "web_search")


if __name__ == "__main__":
    unittest.main()
