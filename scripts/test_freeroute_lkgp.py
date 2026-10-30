#!/usr/bin/env python3
"""LKGP sticky + fail-clears-pin. python3 scripts/test_freeroute_lkgp.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from freeroute_lkgp import LkgpState, apply_lkgp


class LkgpTests(unittest.TestCase):
    def test_last_success_moves_first(self) -> None:
        self.assertEqual(apply_lkgp(["a", "b", "c"], "c"), ["c", "a", "b"])

    def test_unknown_success_leaves_order(self) -> None:
        self.assertEqual(apply_lkgp(["a", "b"], "z"), ["a", "b"])

    def test_none_leaves_order(self) -> None:
        self.assertEqual(apply_lkgp(["a", "b"], None), ["a", "b"])

    def test_empty(self) -> None:
        self.assertEqual(apply_lkgp([], "a"), [])

    def test_record_success_then_order(self) -> None:
        state = LkgpState()
        state.record("b", success=True)
        self.assertEqual(apply_lkgp(["a", "b", "c"], state.last_success_key), ["b", "a", "c"])

    def test_failure_of_sticky_clears_pin(self) -> None:
        state = LkgpState()
        state.record("b", success=True)
        state.record("b", success=False)
        self.assertIsNone(state.last_success_key)
        self.assertEqual(apply_lkgp(["a", "b"], state.last_success_key), ["a", "b"])

    def test_failure_of_other_key_keeps_pin(self) -> None:
        state = LkgpState()
        state.record("b", success=True)
        state.record("a", success=False)
        self.assertEqual(state.last_success_key, "b")
