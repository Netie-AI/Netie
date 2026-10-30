#!/usr/bin/env python3
"""9th FreeRoute strategy. python3 scripts/test_freeroute_strict_random.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from freeroute_strict_random import apply_strict_random, reset_decks


class StrictRandomTests(unittest.TestCase):
    def test_cycle_uses_each_key_once(self) -> None:
        reset_decks()
        keys = ["a", "b", "c"]
        firsts = [
            apply_strict_random(keys, combo_name="c1")[0] for _ in range(3)
        ]
        self.assertEqual(sorted(firsts), ["a", "b", "c"])

    def test_remainder_is_a_permutation(self) -> None:
        reset_decks()
        keys = ["a", "b", "c", "d"]
        ordered = apply_strict_random(keys, combo_name="c2")
        self.assertEqual(sorted(ordered), sorted(keys))
        self.assertEqual(len(set(ordered)), 4)

    def test_empty(self) -> None:
        self.assertEqual(apply_strict_random([], combo_name="x"), [])


if __name__ == "__main__":
    unittest.main()
