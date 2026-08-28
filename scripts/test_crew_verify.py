#!/usr/bin/env python3
"""Different-run verify. python3 scripts/test_crew_verify.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crew_verify import VerifyDenied, close_ticket


class CrewVerifyTests(unittest.TestCase):
    def test_same_run_cannot_close(self) -> None:
        with self.assertRaises(VerifyDenied):
            close_ticket(
                ticket_id="T1",
                implementer_run_id="run-a",
                verifier_run_id="run-a",
                evidence="looks good",
            )

    def test_missing_evidence_stays_open(self) -> None:
        with self.assertRaises(VerifyDenied):
            close_ticket(
                ticket_id="T1",
                implementer_run_id="run-a",
                verifier_run_id="run-b",
                evidence="  ",
            )

    def test_two_runs_close(self) -> None:
        out = close_ticket(
            ticket_id="T1",
            implementer_run_id="run-a",
            verifier_run_id="run-b",
            evidence="rows match SQL",
        )
        self.assertEqual(out.status, "DONE")
        self.assertEqual(out.verified_by, "run-b")


if __name__ == "__main__":
    unittest.main()
