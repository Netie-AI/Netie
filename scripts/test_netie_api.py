#!/usr/bin/env python3
"""Product repos import netie.*, not scripts/. python3 scripts/test_netie_api.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from netie.airgpt import retrieve_space, chunk_table
from netie.control import project_board, run_dag, ControlDenied
from netie.cortex import RouteDenied, run_question
from netie.crew import bind_deep_agent, load_den, CortexDenied
from netie.dms import answer_or_abstain
from netie.pointer import bind_computer, PointerDenied
from netie.route import compile_graph, host_switchyard, SwitchyardDenied
from netie.space import chat_preview


class NetieApiTests(unittest.TestCase):
    def test_crew_bind_is_the_factory(self) -> None:
        self.assertTrue(callable(bind_deep_agent))
        with self.assertRaises(CortexDenied) as ctx:
            load_den("ee/")
        self.assertIn("ee/", str(ctx.exception))

    def test_cortex_is_not_claude_code(self) -> None:
        with self.assertRaises(RouteDenied) as ctx:
            run_question("dag", tool="bash", via_tool_runner=True, verified=True)
        self.assertIn("Claude Code", str(ctx.exception))
        out = run_question("dag", verified=True)
        self.assertEqual(out["jepa"], "off-path")
        self.assertEqual(out["c7_sql"], "off")

    def test_named_analogues_refuse(self) -> None:
        with self.assertRaises(PointerDenied):
            bind_computer("e2b")
        with self.assertRaises(SwitchyardDenied):
            host_switchyard(ov_leave=True, vendor="llm-router")
        with self.assertRaises(ControlDenied):
            run_dag("x")
        compile_graph(engine="compileIR")
        self.assertTrue(callable(chunk_table))
        self.assertTrue(callable(retrieve_space))
        self.assertTrue(callable(answer_or_abstain))
        self.assertTrue(callable(project_board))
        self.assertTrue(callable(chat_preview))


if __name__ == "__main__":
    unittest.main()
