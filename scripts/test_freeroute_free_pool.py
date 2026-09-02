#!/usr/bin/env python3
"""Free pool does not invent keys. python3 scripts/test_freeroute_free_pool.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from freeroute_execution import ExecutionRefused
from freeroute_free_pool import FreePoolRefused, assist_free_pool


class FreePoolTests(unittest.TestCase):
    def test_free_tier_is_the_pool(self) -> None:
        out = assist_free_pool(
            [
                {"id": "groq-free", "tier": "free", "register_url": "https://console.groq.com"},
                {"id": "paid-box", "tier": "paid"},
            ]
        )
        self.assertEqual(out["pool"], [{"id": "groq-free", "tier": "free"}])
        self.assertFalse(out["used_paid"])

    def test_empty_free_is_503_with_register_help(self) -> None:
        with self.assertRaises(FreePoolRefused) as ctx:
            assist_free_pool(
                [{"id": "paid-box", "tier": "paid", "register_url": "https://example/keys"}]
            )
        self.assertEqual(ctx.exception.code, 503)
        self.assertEqual(ctx.exception.help[0]["register_url"], "https://example/keys")
        self.assertNotIn("api_key", ctx.exception.help[0])

    def test_paid_fallback_is_opt_in(self) -> None:
        out = assist_free_pool(
            [{"id": "paid-box", "tier": "paid"}],
            allow_paid=True,
        )
        self.assertTrue(out["used_paid"])
        self.assertEqual(out["pool"][0]["id"], "paid-box")

    def test_quota_fetch_stays_501(self) -> None:
        with self.assertRaises(ExecutionRefused) as ctx:
            assist_free_pool(
                [{"id": "groq-free", "tier": "free"}],
                fetch_quota=True,
            )
        self.assertEqual(ctx.exception.code, 501)

    def test_catalog_secret_field_refuses(self) -> None:
        with self.assertRaises(ExecutionRefused):
            assist_free_pool([{"id": "x", "tier": "free", "api_key": "nope"}])


if __name__ == "__main__":
    unittest.main()
