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
        out = run_question("dag", write="export_pptx")
        self.assertEqual(out["router"], "race_router.auto_route")
        self.assertEqual(out["dms"], "keyword_cascade")
        self.assertEqual(out["c7_sql"], "off")
        self.assertEqual(out["jepa"], "off-path")
        self.assertEqual(out["write"], "export_pptx")

    def test_ungoverned_write_denied(self) -> None:
        with self.assertRaises(RouteDenied):
            run_question("dag", write="warehouse.delete")


if __name__ == "__main__":
    unittest.main()
