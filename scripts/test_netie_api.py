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

from netie.airgpt import ChunkDenied, MAX_RETRIEVE_CHARS, chunk_table, retrieve_space
from netie.control import ControlDenied, project_board, project_session, run_dag
from netie.cortex import RouteDenied, WRITE_ACTIONS, run_question
from netie.crew import (
    CortexDenied,
    Factory,
    Job,
    SeatDenied,
    TokenBudget,
    Verdict,
    bind_deep_agent,
    dispatch_seat,
    load_den,
    run_batch,
)
from netie.dms import SpaceDenied, answer_or_abstain, browse_or_abstain, mint_manifest
from netie.pointer import PointerDenied, bind_computer, click, invoke_hand
from netie.route import (
    CompileDenied,
    ShipDenied,
    SwitchyardDenied,
    compile_graph,
    host_switchyard,
    report_deploy,
)
from netie.space import MAX_CHAT_EXCERPT, SpaceLeaveDenied, chat_preview, ocr_cloud, persist_key


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
                    "from netie.crew import bind_deep_agent, TokenBudget, dispatch_seat; "
                    "from netie.cortex import run_question; "
                    "print('ok' if callable(bind_deep_agent) and callable(TokenBudget) "
                    "and callable(dispatch_seat) and callable(run_question) else 'no')",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(probed.returncode, 0, probed.stderr)
            self.assertEqual(probed.stdout.strip(), "ok")

    def test_crew_product_caller_public_api(self) -> None:
        """Cortex-Crew shape: import netie.crew only, not scripts/."""

        class Gate:
            def check(self, tool: str, payload: dict) -> Verdict:
                return Verdict(allowed=True)

            def execute(self, tool: str, payload: dict) -> dict:
                return {"tool": tool}

        with self.assertRaises(ValueError) as cap:
            run_batch(Gate(), [Job("a", "echo", {})], max_in_flight=3)
        self.assertIn("unbounded spawn", str(cap.exception))

        budget = TokenBudget(max_tokens=40)
        results = run_batch(
            Gate(),
            [
                Job("a", "echo", {"blob": "x" * 80}),
                Job("b", "echo", {"blob": "y" * 80}),
            ],
            max_in_flight=1,
            budget=budget,
        )
        self.assertEqual(results[0].status, "DONE")
        self.assertEqual(results[1].status, "FAILED")
        self.assertIn("budget", results[1].detail)

        with self.assertRaises(SeatDenied) as seat:
            dispatch_seat(
                ticket_id="T1",
                seat="grok-bot-reconstructed",
                operator_logged_in=True,
            )
        self.assertIn("billing-bypass", str(seat.exception))

        factory = Factory()
        factory.slice_prd(
            prd_id="PRD-002",
            out_of_scope="no second cortex",
            success_assertion=(
                "WHEN a tool Cortex would refuse THE SYSTEM SHALL "
                "leave the ticket open"
            ),
            epics=[("E1", "wrap", "foundation")],
        )
        factory.activate_epic("E1")
        factory.file_ticket(
            epic_id="E1",
            ticket_id="T-secret",
            prompt="SECRET PROMPT DO NOT INDEX",
        )
        dumped = str(factory.index())
        self.assertNotIn("SECRET PROMPT", dumped)
        with self.assertRaises(CortexDenied):
            load_den("ee/")

    def test_dms_product_caller_public_api(self) -> None:
        """PRD-001 shape: import netie.dms only, not scripts/."""
        acl = {
            "space-ops": frozenset({"inventory", "shipments"}),
            "space-finance": frozenset({"invoices"}),
        }
        binds = {"space-ops": "dms-demo", "space-finance": "dms-demo"}
        rows = [{"sku": "A"}]
        ok = answer_or_abstain(
            acl,
            "space-ops",
            "inventory",
            rows,
            warehouse_id="dms-demo",
            binds=binds,
            sql="SELECT sku FROM inventory",
        )
        self.assertEqual(ok["status"], "OK")
        ok["rows"][0]["sku"] = "LEAK"
        self.assertEqual(rows[0]["sku"], "A")

        other = answer_or_abstain(
            acl,
            "space-ops",
            "invoices",
            [{"id": 1}],
            warehouse_id="dms-demo",
            binds=binds,
            sql="SELECT id FROM invoices",
        )
        self.assertEqual(other["status"], "ABSTAIN")

        join = answer_or_abstain(
            acl,
            "space-ops",
            "inventory",
            [{"sku": "A"}],
            warehouse_id="dms-demo",
            binds=binds,
            sql="SELECT sku FROM inventory JOIN hr_notes ON true",
        )
        self.assertEqual(join["status"], "ABSTAIN")

        duck = answer_or_abstain(
            acl,
            "space-ops",
            "inventory",
            [{"sku": "A"}],
            warehouse_id="cortex-duckdb",
            binds=binds,
            sql="SELECT sku FROM inventory",
        )
        self.assertEqual(duck["status"], "ABSTAIN")

        chat = answer_or_abstain(
            acl,
            "space-ops",
            "inventory",
            [{"sku": "A"}],
            warehouse_id="dms-demo",
            binds=binds,
            sql="SELECT sku FROM inventory",
            chat_mode=True,
        )
        self.assertEqual(chat["status"], "ABSTAIN")
        self.assertIn("AnythingLLM", chat["reason"])

        bronze = browse_or_abstain(acl, "space-ops", "invoices", tier="bronze")
        self.assertEqual(bronze["status"], "ABSTAIN")
        self.assertEqual(
            mint_manifest(acl, "space-finance"),
            ("invoices",),
        )
        with self.assertRaises(SpaceDenied):
            mint_manifest(acl, "space-missing")

    def test_cortex_product_caller_public_api(self) -> None:
        """Cortex shape: import netie.cortex only. Not Claude Code, no C7."""
        self.assertIn("item.intake", WRITE_ACTIONS)
        with self.assertRaises(RouteDenied) as actor:
            run_question("dag", write="item.intake", verified=True)
        self.assertIn("actor", str(actor.exception))
        with self.assertRaises(RouteDenied) as c7:
            run_question("dag", verified=True, c7_sql=True)
        self.assertIn("C7", str(c7.exception))
        with self.assertRaises(RouteDenied) as a2a:
            run_question("dag", verified=True, a2a=True, pack="default")
        self.assertIn("dms-pack", str(a2a.exception))
        with self.assertRaises(RouteDenied) as bash:
            run_question("dag", tool="bash", via_tool_runner=True, verified=True)
        self.assertIn("Claude Code", str(bash.exception))
        out = run_question("dag", write="item.intake", actor="ops", verified=True)
        self.assertEqual(out["jepa"], "off-path")
        self.assertEqual(out["c7_sql"], "off")
        self.assertEqual(out["write"], "item.intake")

    def test_airgpt_product_caller_public_api(self) -> None:
        """AirGPT RAG: owned table splitter, not ChatGPT memory, not NVIDIA_RAG_EVAL."""
        with self.assertRaises(ChunkDenied) as denied:
            chunk_table("sku,qty\nA,1", splitter="nvidia_rag_eval")
        self.assertIn("NVIDIA_RAG_EVAL", str(denied.exception))
        table = "# warehouse: north\nsku,qty\nA,1\n# warehouse: south\nsku,qty\nB,2\n"
        chunks = chunk_table(table)
        north = retrieve_space(chunks, space="north", query="A")
        self.assertEqual(north["status"], "OK")
        south = retrieve_space(chunks, space="north", query="B")
        self.assertEqual(south["status"], "ABSTAIN")
        mem = retrieve_space(chunks, space="north", query="A", cross_chat_memory=True)
        self.assertEqual(mem["status"], "ABSTAIN")
        self.assertIn("ChatGPT", mem["reason"])
        fat = retrieve_space(chunks, space="north", query="A", max_chars=1)
        self.assertEqual(fat["status"], "ABSTAIN")
        self.assertIn("DitchContext", fat["reason"])
        self.assertEqual(MAX_RETRIEVE_CHARS, 12000)

    def test_space_product_caller_public_api(self) -> None:
        """Peek never POSTs the file. Secrets stay closed. DitchContext 12k."""
        with self.assertRaises(SpaceLeaveDenied) as leave:
            chat_preview("notes.txt", "hello", ov_allowed=False)
        self.assertIn("OpenVault", str(leave.exception))
        with self.assertRaises(SpaceLeaveDenied) as secret:
            chat_preview(".env", "hello", ov_allowed=True)
        self.assertIn("secret", str(secret.exception))
        with self.assertRaises(SpaceLeaveDenied) as budget:
            chat_preview("notes.txt", "x" * (MAX_CHAT_EXCERPT + 1), ov_allowed=True)
        self.assertIn("DitchContext", str(budget.exception))
        with self.assertRaises(SpaceLeaveDenied):
            persist_key("id_rsa", False)
        with self.assertRaises(SpaceLeaveDenied) as ocr:
            ocr_cloud("scan.png", ov_allowed=False, local_chars=3)
        self.assertIn("OCR", str(ocr.exception))

    def test_pointer_product_caller_public_api(self) -> None:
        """Local tray. Not e2b / Perplexity Computer. UACC brains stay out."""
        with self.assertRaises(PointerDenied):
            bind_computer("e2b")
        with self.assertRaises(PointerDenied):
            bind_computer("perplexity-computer")
        self.assertEqual(bind_computer("uacc")["where"], "local")
        with self.assertRaises(PointerDenied):
            click({"role": "button"}, cortex_intent="go")
        with self.assertRaises(PointerDenied):
            click(
                {"name": "password", "role": "textbox", "type": "password"},
                cortex_intent="go",
            )
        with self.assertRaises(PointerDenied) as shot:
            invoke_hand("screenshot", cortex_allowed=True, cortex_intent="see")
        self.assertIn("uncropped", str(shot.exception))
        with self.assertRaises(PointerDenied) as proc:
            invoke_hand("list_processes", cortex_allowed=True, cortex_intent="see")
        self.assertIn("process_list", str(proc.exception))
        with self.assertRaises(PointerDenied) as js:
            invoke_hand("browser_execute_js", cortex_allowed=True, cortex_intent="run")
        self.assertIn("script", str(js.exception))

    def test_control_product_caller_public_api(self) -> None:
        """Crew board view. Not Guacamole. No dag_runner. No transcript."""
        with self.assertRaises(ControlDenied):
            run_dag("x")
        with self.assertRaises(ControlDenied) as rdp:
            project_board(
                crew_index={"runs": [{"id": "r1", "kind": "rdp"}]},
                ledger_peek=[],
                refusals=[],
            )
        self.assertIn("Guacamole", str(rdp.exception))
        with self.assertRaises(ControlDenied):
            project_session(
                run={"id": "r1", "transcript": "SECRET"},
                todos=[],
                permissions=[],
            )
        board = project_board(
            crew_index={"runs": [{"id": "r1", "status": "FAILED", "ticket_id": "T1"}]},
            ledger_peek=[],
            refusals=[{"id": "T1", "reason": "CortexDenied"}],
        )
        self.assertEqual(board["product"], "crew-board")
        kinds = {c["kind"] for c in board["cards"]}
        self.assertIn("run", kinds)
        self.assertIn("refusal", kinds)

    def test_route_product_caller_public_api(self) -> None:
        """Switchyard behind OV. Simulated is not HT1. xyflow is not compileIR."""
        with self.assertRaises(SwitchyardDenied):
            host_switchyard(ov_leave=True, vendor="llm-router")
        hosted = host_switchyard(ov_leave=True)
        self.assertEqual(hosted["score"], "2/10")
        with self.assertRaises(ShipDenied):
            report_deploy(simulated=True, observed_url=None, constructed_url=None)
        with self.assertRaises(ShipDenied):
            report_deploy(
                simulated=False,
                observed_url=None,
                constructed_url="https://x.pages.dev",
            )
        with self.assertRaises(CompileDenied):
            compile_graph(engine="@xyflow/react")
        ir = compile_graph(engine="compileIR")
        self.assertEqual(ir["score_compiler"], "4/10")


if __name__ == "__main__":
    unittest.main()
