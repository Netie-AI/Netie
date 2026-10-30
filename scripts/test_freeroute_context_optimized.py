#!/usr/bin/env python3
"""context-optimized ordering. python3 scripts/test_freeroute_context_optimized.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from freeroute_context_optimized import apply_context_optimized


class ContextOptimizedTests(unittest.TestCase):
    def test_largest_window_first(self) -> None:
        ordered = apply_context_optimized(
            ["a", "b", "c"], {"a": 8_000, "b": 128_000, "c": 32_000}
        )
        self.assertEqual(ordered, ["b", "c", "a"])

    def test_all_unknown_leaves_order(self) -> None:
        self.assertEqual(
            apply_context_optimized(["a", "b"], {"a": None, "b": None}),
            ["a", "b"],
        )

    def test_unknown_sorts_last(self) -> None:
        ordered = apply_context_optimized(["a", "b", "c"], {"b": 16_000})
        self.assertEqual(ordered[0], "b")
        self.assertEqual(ordered[1:], ["a", "c"])

    def test_empty(self) -> None:
        self.assertEqual(apply_context_optimized([], {}), [])


if __name__ == "__main__":
    unittest.main()
