#!/usr/bin/env python3
"""netie_init stamps uv-addable product callers. python3 scripts/test_netie_init.py"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from netie_init import CALLERS, stamp


class NetieInitTests(unittest.TestCase):
    def test_stamps_dms_product_caller(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "dms"
            root.mkdir()
            stamp(root, "DMS")
            text = (root / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn(
                "uv add --editable git+https://github.com/Netie-AI/Netie.git",
                text,
            )
            self.assertIn(CALLERS["DMS"], text)
            self.assertIn("Do not clone Grok Bot reconstructed", text)
            self.assertIn("OpenWork", text)

    def test_stamps_crew_and_cortex_callers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            crew = Path(tmp) / "crew"
            cortex = Path(tmp) / "cortex"
            crew.mkdir()
            cortex.mkdir()
            stamp(crew, "Crew")
            stamp(cortex, "Cortex")
            crew_text = (crew / "CLAUDE.md").read_text(encoding="utf-8")
            cortex_text = (cortex / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn(CALLERS["Crew"], crew_text)
            self.assertIn("crew_harness_profile", crew_text)
            self.assertIn("TokenBudget", crew_text)
            self.assertIn(CALLERS["Cortex"], cortex_text)
            self.assertIn("WRITE_ACTIONS", cortex_text)
            self.assertIn("not Claude Code", cortex_text)

    def test_stamps_control_product_caller(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "netie-control"
            root.mkdir()
            stamp(root, "Control")
            text = (root / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn(CALLERS["Control"], text)
            self.assertIn("MAX_BOARD_CHARS", text)
            self.assertIn("project_board", text)


if __name__ == "__main__":
    unittest.main()
