#!/usr/bin/env python3
"""Product repos import netie.*, not scripts/. python3 scripts/test_netie_api.py"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
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

    def test_pyproject_declares_editable_netie_package(self) -> None:
        text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('name = "netie"', text)
        self.assertIn('packages = ["netie"]', text)
        self.assertIn('crew = ["deepagents==0.7.9"]', text)
        self.assertNotIn("scripts*", text)

    def test_missing_scripts_tree_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = Path(tmp) / "netie"
            pkg.mkdir()
            (pkg / "_scripts.py").write_text(
                (ROOT / "netie" / "_scripts.py").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            spec = importlib.util.spec_from_file_location(
                "netie_scripts_probe_missing",
                pkg / "_scripts.py",
            )
            self.assertIsNotNone(spec)
            self.assertIsNotNone(spec.loader)
            mod = importlib.util.module_from_spec(spec)
            with self.assertRaises(ImportError) as ctx:
                spec.loader.exec_module(mod)
            self.assertIn("uv add --editable", str(ctx.exception))

    def test_editable_uv_install_imports_crew(self) -> None:
        if shutil.which("uv") is None:
            raise unittest.SkipTest("uv not on PATH")
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "Netie"
            shutil.copytree(ROOT / "netie", src / "netie")
            shutil.copytree(ROOT / "scripts", src / "scripts")
            shutil.copy(ROOT / "pyproject.toml", src / "pyproject.toml")
            shutil.copy(ROOT / "STATUS.md", src / "STATUS.md")
            venv = Path(tmp) / ".venv"
            created = subprocess.run(
                ["uv", "venv", str(venv)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            py = venv / "bin" / "python"
            installed = subprocess.run(
                [
                    "uv",
                    "pip",
                    "install",
                    "-e",
                    str(src),
                    "--python",
                    str(py),
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(installed.returncode, 0, installed.stderr + installed.stdout)
            probed = subprocess.run(
                [
                    str(py),
                    "-c",
                    "from netie.crew import bind_deep_agent; "
                    "from netie.cortex import run_question; "
                    "print('ok' if callable(bind_deep_agent) and callable(run_question) else 'no')",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(probed.returncode, 0, probed.stderr)
            self.assertEqual(probed.stdout.strip(), "ok")


if __name__ == "__main__":
    unittest.main()
