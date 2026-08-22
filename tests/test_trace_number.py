"""Behavior gates for the buyer-facing source trace helper."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "trace_number.py"
FIXTURE = ROOT / "docs" / "fixtures" / "sample-outbound.xlsx"
CSV_FIXTURE = ROOT / "docs" / "fixtures" / "sample-outbound.csv"


def run_trace(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class TraceNumberTests(unittest.TestCase):
    def test_simple_sum_reports_inputs_and_recomputes(self) -> None:
        result = run_trace(str(FIXTURE), "WK32!F4")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Formula: =SUM(C4:E4)", result.stdout)
        self.assertIn("- WK32!C4 = 2100", result.stdout)
        self.assertIn("Recomputed from inputs: 6480 (matches cached value)", result.stdout)
        self.assertIn("Verdict: Traced", result.stdout)

    def test_shared_formula_and_sheet_name_are_resolved(self) -> None:
        result = run_trace(str(FIXTURE), "'wk32'!F5")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Formula: =SUM(C5:E5)", result.stdout)
        self.assertIn("Recomputed from inputs: 400 (matches cached value)", result.stdout)

    def test_typed_figure_refuses_with_nonzero_exit(self) -> None:
        result = run_trace(str(FIXTURE), "WK32!F7")

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("Verdict: Cannot be traced", result.stdout)
        self.assertIn("Reason: Selected cell has no formula.", result.stdout)

    def test_csv_refuses_instead_of_claiming_a_formula(self) -> None:
        result = run_trace(str(CSV_FIXTURE), "F4")

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("Reason: CSV cells do not contain formulas.", result.stdout)

    def test_cached_value_disagreement_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workbook = Path(temporary_directory) / "stale-cache.xlsx"
            with zipfile.ZipFile(FIXTURE) as source, zipfile.ZipFile(workbook, "w") as destination:
                for member in source.infolist():
                    content = source.read(member.filename)
                    if member.filename == "xl/worksheets/sheet1.xml":
                        content = content.replace(b"<v>6480</v>", b"<v>9999</v>", 1)
                    destination.writestr(member, content)

            result = run_trace(str(workbook), "WK32!F4")

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("Cached value disagrees with recomputed value (6480).", result.stdout)

    def test_bad_xlsx_has_no_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            invalid_workbook = Path(temporary_directory) / "not-a-workbook.xlsx"
            invalid_workbook.write_text("not a zip", encoding="utf-8")
            result = run_trace(str(invalid_workbook), "A1")

        self.assertEqual(result.returncode, 65)
        self.assertIn("not a readable xlsx workbook", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_bad_reference_is_a_usage_error(self) -> None:
        result = run_trace(str(FIXTURE), "F4A")

        self.assertEqual(result.returncode, 64)
        self.assertIn("Use a cell like F14 or Sheet1!F14", result.stderr)

    def test_json_output_is_machine_readable(self) -> None:
        result = run_trace(str(FIXTURE), "WK32!F4", "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["verdict"], "Traced")
        self.assertEqual(payload["inputs"][0]["cell"], "WK32!C4")
        self.assertEqual(payload["recomputed_from_inputs"], "6480 (matches cached value)")


if __name__ == "__main__":
    unittest.main()
