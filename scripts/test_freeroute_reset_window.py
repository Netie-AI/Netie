#!/usr/bin/env python3
"""reset-window ordering. python3 scripts/test_freeroute_reset_window.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from freeroute_reset_window import apply_reset_window


class ResetWindowTests(unittest.TestCase):
    def test_soonest_reset_first(self) -> None:
        ordered = apply_reset_window(
            ["a", "b", "c"], {"a": 60_000, "b": 5_000, "c": 30_000}
        )
        self.assertEqual(ordered, ["b", "c", "a"])

    def test_elapsed_collapses_to_zero(self) -> None:
        ordered = apply_reset_window(["a", "b"], {"a": 10_000, "b": -50})
        self.assertEqual(ordered[0], "b")

    def test_unknown_sorts_last(self) -> None:
        ordered = apply_reset_window(["a", "b", "c"], {"b": 1_000})
        self.assertEqual(ordered[0], "b")
        self.assertEqual(ordered[1:], ["a", "c"])

    def test_tie_keeps_input_order(self) -> None:
        ordered = apply_reset_window(
            ["a", "b"], {"a": 1000, "b": 1000}
        )
        self.assertEqual(ordered, ["a", "b"])

    def test_empty(self) -> None:
        self.assertEqual(apply_reset_window([], {}), [])


if __name__ == "__main__":
    unittest.main()
