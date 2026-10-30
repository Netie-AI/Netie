#!/usr/bin/env python3
"""cache-optimized rendezvous. python3 scripts/test_freeroute_cache_optimized.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from freeroute_cache_optimized import apply_cache_optimized


class CacheOptimizedTests(unittest.TestCase):
    def test_empty_key_leaves_order(self) -> None:
        self.assertEqual(apply_cache_optimized(["a", "b", "c"], ""), ["a", "b", "c"])
        self.assertEqual(apply_cache_optimized(["a", "b"], None), ["a", "b"])

    def test_same_key_is_stable(self) -> None:
        keys = ["a", "b", "c", "d"]
        first = apply_cache_optimized(keys, "conv-1")
        second = apply_cache_optimized(list(reversed(keys)), "conv-1")
        self.assertEqual(first[0], second[0])

    def test_is_permutation(self) -> None:
        keys = ["a", "b", "c"]
        ordered = apply_cache_optimized(keys, "prompt-x")
        self.assertEqual(sorted(ordered), keys)

    def test_empty_targets(self) -> None:
        self.assertEqual(apply_cache_optimized([], "x"), [])


if __name__ == "__main__":
    unittest.main()
