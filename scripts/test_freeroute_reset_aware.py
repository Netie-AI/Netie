#!/usr/bin/env python3
"""reset-aware scoring. python3 scripts/test_freeroute_reset_aware.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from freeroute_reset_aware import (
    SESSION_MS,
    WEEKLY_MS,
    apply_reset_aware,
    score_reset_aware,
)


class ResetAwareTests(unittest.TestCase):
    def test_more_remaining_first(self) -> None:
        ordered = apply_reset_aware(
            ["a", "b", "c"],
            {
                "a": (0.1, 0.1, False),
                "b": (0.9, 0.9, False),
                "c": (0.4, 0.4, False),
            },
        )
        self.assertEqual(ordered, ["b", "c", "a"])

    def test_limit_reached_sorts_last(self) -> None:
        ordered = apply_reset_aware(
            ["a", "b"],
            {"a": (0.9, 0.9, True), "b": (0.2, 0.2, False)},
        )
        self.assertEqual(ordered[-1], "a")
        self.assertEqual(ordered[0], "b")

    def test_soon_reset_empty_beats_full_far_reset(self) -> None:
        empty_soon = score_reset_aware(
            session_remaining=0.05,
            weekly_remaining=0.05,
            session_reset_ms=0,
            weekly_reset_ms=0,
        )
        full_far = score_reset_aware(
            session_remaining=0.9,
            weekly_remaining=0.9,
            session_reset_ms=SESSION_MS,
            weekly_reset_ms=WEEKLY_MS,
        )
        self.assertGreater(empty_soon, full_far)

    def test_exhaustion_guard_lowers_score_without_reset(self) -> None:
        healthy = score_reset_aware(session_remaining=0.5, weekly_remaining=0.5)
        exhausted = score_reset_aware(session_remaining=0.01, weekly_remaining=0.9)
        self.assertGreater(healthy, exhausted)

    def test_missing_remaining_is_mid(self) -> None:
        ordered = apply_reset_aware(
            ["a", "b"], {"b": (0.9, 0.9, False)}
        )
        self.assertEqual(ordered[0], "b")

    def test_empty(self) -> None:
        self.assertEqual(apply_reset_aware([], {}), [])


if __name__ == "__main__":
    unittest.main()
