#!/usr/bin/env python3
"""Licensed-seat router. python3 scripts/test_seat_router.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from seat_router import SeatDenied, dispatch_seat


class SeatRouterTests(unittest.TestCase):
    def test_unknown_product_denied(self) -> None:
        with self.assertRaises(SeatDenied):
            dispatch_seat(
                ticket_id="T1",
                seat="grok-bot-reconstructed",
                operator_logged_in=True,
            )

    def test_no_login_denied(self) -> None:
        with self.assertRaises(SeatDenied):
            dispatch_seat(ticket_id="T1", seat="cursor", operator_logged_in=False)

    def test_cursor_seat_queues(self) -> None:
        out = dispatch_seat(ticket_id="T1", seat="cursor", operator_logged_in=True)
        self.assertEqual(out.status, "queued")
        self.assertEqual(out.seat, "cursor")

    def test_source_has_no_browser_drive(self) -> None:
        src = Path(__file__).resolve().parent.joinpath("seat_router.py").read_text(
            encoding="utf-8"
        )
        for needle in ("playwright", "puppeteer"):
            self.assertNotIn(needle, src.lower())


if __name__ == "__main__":
    unittest.main()
