#!/usr/bin/env python3
"""headroom ranking. python3 scripts/test_freeroute_headroom.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from freeroute_headroom import apply_headroom, compute_headroom


class HeadroomTests(unittest.TestCase):
    def test_most_free_capacity_first(self) -> None:
        ordered = apply_headroom(
            ["a", "b", "c"],
            {"a": (0.9, 0.1), "b": (0.1, 0.1), "c": (0.5, 0.8)},
        )
        self.assertEqual(ordered, ["b", "c", "a"])

    def test_missing_sat_is_full_headroom(self) -> None:
        ordered = apply_headroom(["a", "b"], {"a": (0.5, 0.5)})
        self.assertEqual(ordered[0], "b")

    def test_tie_keeps_input_order(self) -> None:
        ordered = apply_headroom(
            ["a", "b"], {"a": (0.2, 0.2), "b": (0.2, 0.2)}
        )
        self.assertEqual(ordered, ["a", "b"])

    def test_compute_clamps(self) -> None:
        self.assertEqual(compute_headroom(None, None), 1.0)
        self.assertEqual(compute_headroom(2.0, -1.0), 0.0)


if __name__ == "__main__":
    unittest.main()
