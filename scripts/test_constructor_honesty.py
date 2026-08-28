#!/usr/bin/env python3
"""xyflow is not compileIR. python3 scripts/test_constructor_honesty.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from constructor_honesty import CompileDenied, compile_graph


class ConstructorHonestyTests(unittest.TestCase):
    def test_xyflow_is_not_the_compiler(self) -> None:
        with self.assertRaises(CompileDenied) as ctx:
            compile_graph(engine="@xyflow/react")
        self.assertIn("editor", str(ctx.exception))

    def test_compileir_stays_ours(self) -> None:
        out = compile_graph(engine="compileIR")
        self.assertEqual(out["engine"], "compileIR")
        self.assertEqual(out["score_editor"], "2/10")
        self.assertEqual(out["score_compiler"], "4/10")


if __name__ == "__main__":
    unittest.main()
