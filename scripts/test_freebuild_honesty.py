#!/usr/bin/env python3
"""Never fake a FreeBuild URL. python3 scripts/test_freebuild_honesty.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from freebuild_honesty import ShipDenied, parse_observed_url, report_deploy


class FreebuildHonestyTests(unittest.TestCase):
    def test_constructed_pages_dev_is_denied(self) -> None:
        with self.assertRaises(ShipDenied):
            report_deploy(
                simulated=False,
                observed_url=None,
                constructed_url="https://demo.pages.dev",
            )

    def test_simulated_is_not_ht1(self) -> None:
        with self.assertRaises(ShipDenied):
            report_deploy(
                simulated=True,
                observed_url="https://demo.pages.dev",
                constructed_url=None,
            )

    def test_zero_exit_without_url_fails(self) -> None:
        with self.assertRaises(ShipDenied):
            parse_observed_url("done", exit_code=0)

    def test_wrangler_url_is_live(self) -> None:
        url = parse_observed_url(
            "Uploaded!\nhttps://demo.pages.dev\n", exit_code=0
        )
        out = report_deploy(
            simulated=False, observed_url=url, constructed_url=None
        )
        self.assertEqual(out["status"], "LIVE")
        self.assertEqual(out["ht1"], "observed")


if __name__ == "__main__":
    unittest.main()
