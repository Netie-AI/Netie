#!/usr/bin/env python3
"""Accessible product repos: sibling patches still apply. python3 scripts/test_sibling_patches.py

Constructor has no unit-test workflow on HEAD. This gate clones it, applies
docs/patches/constructor-compiler-tests.patch then constructor-empty-graph.patch
then constructor-ir-refuse.patch then constructor-ir-ids.patch then
constructor-ghost-refuse.patch then constructor-ir-emit.patch then
constructor-tool-action.patch then constructor-inspect-action.patch then constructor-inspect-object.patch then constructor-inspect-tier.patch then constructor-chat-object.patch then constructor-topo-leftover.patch then constructor-ir-entry.patch then constructor-ir-output.patch then constructor-ir-object.patch then constructor-ir-bind.patch then constructor-ir-action-allow.patch then constructor-ir-intake.patch then constructor-ir-hitl.patch then constructor-ir-connected.patch then constructor-ir-note.patch then constructor-ir-cortex-post.patch then constructor-object-pick.patch then constructor-engine-order.patch then constructor-ir-post.patch then constructor-ir-kahn-nodes.patch, and runs
node --test (62 passed). Extra `constructor-ir-4896ddd.patch` /
`constructor-inspect-4896ddd.patch` are a thinner alternate stack (do not mix
with the 26). Portable Python IR is `scripts/constructor_ir.py`.
OpenVault patches apply on origin/main then `uv run pytest` on the routing+chat+crew-gate+ship-claim+free-pool files (>= 90 passed). The 28th patch (`openvault-crew-netie.patch`) makes `/api/crew/gate` call `from netie.crew import refuse_crew_gate` when Netie is installed. Then `openvault-free-pool.patch` + `openvault-free-pool-route.patch` add `POST /api/route/free`.
Cortex `cortex-netie-path.patch` applies on origin/main (do not uv-add Netie.git). `cortex-web-via-runner.patch` applies on origin/main (`default_broker` no web/discovery skip). `cortex-role-execute.patch` applies after those (`require_role` on execute modules). `cortex-observe-guard.patch` applies after those (`computer.observe` through guard_observe). dms `dms-netie-acl.patch` applies on origin/main (`live_ask` / browse through `netie.dms` when installed). Pointer `pointer-netie-hands.patch` then `pointer-observe-guard.patch` apply on origin/main (UACC search drops planner/clipboard/window dump; native observe stays DR-0005; governed:true is opt-in). Control `control-netie-board.patch` applies on origin/main (`guard_issue_board` / Guacamole 405s). Founder apply-all: `scripts/apply_product_patches.py` (does not push).
"""

from __future__ import annotations

import os
import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / "docs" / "patches"
_LOCAL_BIN = str(Path.home() / ".local" / "bin")
os.environ["PATH"] = _LOCAL_BIN + os.pathsep + os.environ.get("PATH", "")


def _run(
    cmd: list[str],
    cwd: Path | None = None,
    *,
    timeout: int = 120,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


class SiblingPatchTests(unittest.TestCase):
    def test_constructor_compiler_tests_on_patched_head(self) -> None:
        first = PATCHES / "constructor-compiler-tests.patch"
        second = PATCHES / "constructor-empty-graph.patch"
        third = PATCHES / "constructor-ir-refuse.patch"
        fourth = PATCHES / "constructor-ir-ids.patch"
        fifth = PATCHES / "constructor-ghost-refuse.patch"
        sixth = PATCHES / "constructor-ir-emit.patch"
        seventh = PATCHES / "constructor-tool-action.patch"
        eighth = PATCHES / "constructor-inspect-action.patch"
        ninth = PATCHES / "constructor-inspect-object.patch"
        tenth = PATCHES / "constructor-inspect-tier.patch"
        eleventh = PATCHES / "constructor-chat-object.patch"
        twelfth = PATCHES / "constructor-topo-leftover.patch"
        thirteenth = PATCHES / "constructor-ir-entry.patch"
        fourteenth = PATCHES / "constructor-ir-output.patch"
        fifteenth = PATCHES / "constructor-ir-object.patch"
        sixteenth = PATCHES / "constructor-ir-bind.patch"
        seventeenth = PATCHES / "constructor-ir-action-allow.patch"
        eighteenth = PATCHES / "constructor-ir-intake.patch"
        nineteenth = PATCHES / "constructor-ir-hitl.patch"
        twentieth = PATCHES / "constructor-ir-connected.patch"
        twenty_first = PATCHES / "constructor-ir-note.patch"
        twenty_second = PATCHES / "constructor-ir-cortex-post.patch"
        twenty_third = PATCHES / "constructor-object-pick.patch"
        twenty_fourth = PATCHES / "constructor-engine-order.patch"
        twenty_fifth = PATCHES / "constructor-ir-post.patch"
        twenty_sixth = PATCHES / "constructor-ir-kahn-nodes.patch"
        self.assertTrue(
            first.is_file()
            and second.is_file()
            and third.is_file()
            and fourth.is_file()
            and fifth.is_file()
            and sixth.is_file()
            and seventh.is_file()
            and eighth.is_file()
            and ninth.is_file()
            and tenth.is_file()
            and eleventh.is_file()
            and twelfth.is_file()
            and thirteenth.is_file()
            and fourteenth.is_file()
            and fifteenth.is_file()
            and sixteenth.is_file()
            and seventeenth.is_file()
            and eighteenth.is_file()
            and nineteenth.is_file()
            and twentieth.is_file()
            and twenty_first.is_file()
            and twenty_second.is_file()
            and twenty_third.is_file()
            and twenty_fourth.is_file()
            and twenty_fifth.is_file()
            and twenty_sixth.is_file()
        )
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "constructor"
            clone = _run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    "landing-9-first-path",
                    "https://github.com/Netie-AI/constructor.git",
                    str(dest),
                ]
            )
            self.assertEqual(clone.returncode, 0, clone.stderr)
            for patch in (
                first,
                second,
                third,
                fourth,
                fifth,
                sixth,
                seventh,
                eighth,
                ninth,
                tenth,
                eleventh,
                twelfth,
                thirteenth,
                fourteenth,
                fifteenth,
                sixteenth,
                seventeenth,
                eighteenth,
                nineteenth,
                twentieth,
                twenty_first,
                twenty_second,
                twenty_third,
                twenty_fourth,
                twenty_fifth,
                twenty_sixth,
            ):
                applied = _run(["git", "apply", str(patch)], cwd=dest)
                self.assertEqual(applied.returncode, 0, applied.stderr)
            tests = _run(["node", "--test", "tests/compiler.test.cjs"], cwd=dest)
            self.assertEqual(tests.returncode, 0, tests.stdout + tests.stderr)
            self.assertIn("pass 62", tests.stdout + tests.stderr)
            engine = (dest / "engine.js").read_text(encoding="utf-8")
            self.assertIn(
                'WRITE_ACTIONS = ["export_pptx", "item.intake", "amend.apply", "call_action"]',
                engine,
            )
            self.assertIn("NOTE_LEAK", engine)
            self.assertIn("function cortexPayload", engine)
            self.assertIn("nodes: ir.nodes", engine)
            self.assertIn("compiledById", engine)
            self.assertIn("function applyObjectType", engine)
            self.assertIn("function bindWhenReady", engine)
            app = (dest / "app.js").read_text(encoding="utf-8")
            self.assertNotIn("Object.keys(OBJECTS[value].points)[0]", app)
            self.assertIn("applyObjectType(node, value, OBJECTS)", app)
            html = (dest / "index.html").read_text(encoding="utf-8")
            self.assertGreater(html.find("engine.js"), -1)
            self.assertGreater(html.find("app.js"), html.find("engine.js"))

    def test_openvault_patches_apply_on_main(self) -> None:
        detect = PATCHES / "openvault-detect-stacks.patch"
        strict = PATCHES / "openvault-strict-random.patch"
        lkgp = PATCHES / "openvault-lkgp.patch"
        self.assertTrue(detect.is_file() and strict.is_file() and lkgp.is_file())
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "OpenVault"
            clone = _run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    "main",
                    "https://github.com/Netie-AI/OpenVault.git",
                    str(dest),
                ]
            )
            self.assertEqual(clone.returncode, 0, clone.stderr)
            # lkgp must follow strict-random (both edit StrategyName).
            # crew-gate is independent of routing files.
            crew = PATCHES / "openvault-crew-gate.patch"
            ctx = PATCHES / "openvault-context-headroom.patch"
            reset = PATCHES / "openvault-reset-window.patch"
            aware = PATCHES / "openvault-reset-aware.patch"
            cache = PATCHES / "openvault-cache-optimized.patch"
            shapes = PATCHES / "openvault-execution-shapes.patch"
            chat = PATCHES / "openvault-chat-dispatch.patch"
            hop = PATCHES / "openvault-hop-walk.patch"
            failover = PATCHES / "openvault-hop-failover.patch"
            park = PATCHES / "openvault-hop-park.patch"
            stream = PATCHES / "openvault-hop-stream.patch"
            relay = PATCHES / "openvault-hop-relay.patch"
            trace = PATCHES / "openvault-hop-trace.patch"
            usage = PATCHES / "openvault-hop-usage.patch"
            persist = PATCHES / "openvault-hop-persist.patch"
            anth = PATCHES / "openvault-hop-anthropic.patch"
            scope = PATCHES / "openvault-hop-scope.patch"
            serve = PATCHES / "openvault-hop-serve.patch"
            bound = PATCHES / "openvault-hop-bound.patch"
            catalog = PATCHES / "openvault-hop-catalog.patch"
            quota = PATCHES / "openvault-quota-share.patch"
            strip = PATCHES / "openvault-hop-strip.patch"
            sidecar = PATCHES / "openvault-hop-sidecar.patch"
            ship = PATCHES / "openvault-ship-netie.patch"
            crew_netie = PATCHES / "openvault-crew-netie.patch"
            free_pool = PATCHES / "openvault-free-pool.patch"
            free_route = PATCHES / "openvault-free-pool-route.patch"
            self.assertTrue(
                crew.is_file()
                and ctx.is_file()
                and reset.is_file()
                and aware.is_file()
                and cache.is_file()
                and shapes.is_file()
                and chat.is_file()
                and hop.is_file()
                and failover.is_file()
                and park.is_file()
                and stream.is_file()
                and relay.is_file()
                and trace.is_file()
                and usage.is_file()
                and persist.is_file()
                and anth.is_file()
                and scope.is_file()
                and serve.is_file()
                and bound.is_file()
                and catalog.is_file()
                and quota.is_file()
                and strip.is_file()
                and sidecar.is_file()
                and ship.is_file()
                and crew_netie.is_file()
                and free_pool.is_file()
                and free_route.is_file()
            )
            for patch in (
                detect,
                strict,
                lkgp,
                crew,
                ctx,
                reset,
                aware,
                cache,
                shapes,
                chat,
                hop,
                failover,
                park,
                stream,
                relay,
                trace,
                usage,
                persist,
                anth,
                scope,
                serve,
                bound,
                catalog,
                quota,
                strip,
                sidecar,
                ship,
                crew_netie,
                free_pool,
                free_route,
            ):
                check = _run(["git", "apply", "--check", str(patch)], cwd=dest)
                self.assertEqual(check.returncode, 0, f"{patch.name}: {check.stderr}")
                applied = _run(["git", "apply", str(patch)], cwd=dest)
                self.assertEqual(applied.returncode, 0, f"{patch.name}: {applied.stderr}")
            strategies = (
                dest / "OpenMW" / "openmw" / "openvault" / "route" / "strategies.py"
            ).read_text(encoding="utf-8")
            self.assertIn('if strategy == "lkgp":', strategies)
            self.assertIn('if strategy == "context-optimized":', strategies)
            self.assertIn('if strategy == "headroom":', strategies)
            self.assertIn('if strategy == "reset-window":', strategies)
            self.assertIn('if strategy == "reset-aware":', strategies)
            self.assertIn('if strategy == "cache-optimized":', strategies)
            self.assertIn("StrategyNotASort", strategies)
            execution = (
                dest / "OpenMW" / "openmw" / "openvault" / "route" / "execution.py"
            ).read_text(encoding="utf-8")
            self.assertIn("def plan_fusion", execution)
            self.assertIn("def run_pipeline", execution)
            self.assertIn("def resolve_auto", execution)
            self.assertIn("def dispatch_combo", execution)
            self.assertIn("def chat_shape_refusal", execution)
            self.assertIn("def hop_call_model", execution)
            self.assertIn("def pick_hop", execution)
            self.assertIn("def hops_for_model", execution)
            proxy = (
                dest / "OpenMW" / "openmw" / "openvault" / "vault" / "proxy.py"
            ).read_text(encoding="utf-8")
            self.assertIn("chat_shape_refusal", proxy)
            self.assertIn("_run_execution_shape", proxy)
            self.assertIn("Execution-shape posts use the same classify_attempt", proxy)
            self.assertIn("sse_wrap_text", execution)
            self.assertIn("def relay_available_from_body", execution)
            self.assertIn("Last hop may SSE", proxy)
            self.assertIn("relay_handoff_from_body", proxy)
            self.assertIn("Last successful hop, not", proxy)
            self.assertIn("Last hop usage only", proxy)
            self.assertIn("remember_relay_handoff", execution)
            self.assertIn("resolve_relay_handoff", proxy)
            self.assertIn("In-process caller handoff store", proxy)
            self.assertIn("anthropic chat not via /v1 proxy yet", execution)
            self.assertIn("scoped by tenant", proxy)
            self.assertIn("no hop can serve model", execution)
            self.assertIn("MAX_RELAY_PER_SCOPE", execution)
            self.assertIn("def hop_serves_listed", execution)
            self.assertIn("Catalog membership, not resolve_model", proxy)
            self.assertIn("quota-share is OmniRoute-internal", execution)
            self.assertIn("parallel quorum-grace not ported", execution)
            self.assertIn("unported_http", proxy)
            budget = (
                dest / "OpenMW" / "openmw" / "openvault" / "vault" / "budget.py"
            ).read_text(encoding="utf-8")
            self.assertIn("def hop_body_from_chat", execution)
            self.assertIn("CREW_SIDECARS", execution)
            self.assertIn("crew_body_http", proxy)
            self.assertIn("hop_body_from_chat", budget)
            app_py = (dest / "OpenMW" / "openmw" / "openvault" / "app.py").read_text(
                encoding="utf-8"
            )
            self.assertIn('"/api/crew/gate"', app_py)
            self.assertIn('"/api/route/free"', app_py)
            self.assertIn("from openmw.openvault.crew_netie import check_crew_gate", app_py)
            crew_mod = (
                dest / "OpenMW" / "openmw" / "openvault" / "crew_netie.py"
            ).read_text(encoding="utf-8")
            self.assertIn("from netie.crew import refuse_crew_gate", crew_mod)
            self.assertIn("def check_crew_gate", crew_mod)
            free_mod = (
                dest / "OpenMW" / "openmw" / "openvault" / "route" / "free_pool.py"
            ).read_text(encoding="utf-8")
            self.assertIn("from netie.route import assist_free_pool", free_mod)
            self.assertIn("def pick_free_pool", free_mod)
            claim = (
                dest / "OpenMW" / "openmw" / "openvault" / "ship" / "netie_claim.py"
            ).read_text(encoding="utf-8")
            self.assertIn("from netie.route import report_deploy", claim)
            self.assertIn("def claim_deploy", claim)
            engine = (
                dest / "OpenMW" / "openmw" / "openvault" / "ship" / "engine.py"
            ).read_text(encoding="utf-8")
            self.assertIn("claim_deploy", engine)
            if shutil.which("uv") is None:
                self.fail("uv required to run OpenVault routing tests")
            routed = _run(
                [
                    "uv",
                    "run",
                    "--with",
                    str(ROOT),
                    "pytest",
                    "tests/test_route_strategies.py",
                    "tests/test_execution_shapes.py",
                    "tests/test_execution_chat.py",
                    "tests/test_freeroute_acceptance.py",
                    "tests/test_freeroute_metering.py",
                    "tests/test_crew_gate.py",
                    "tests/test_crew_netie_gate.py",
                    "tests/test_ship_netie_claim.py",
                    "tests/test_free_pool.py",
                    "tests/test_free_pool_route.py",
                    "-q",
                    "--tb=line",
                ],
                cwd=dest / "OpenMW",
                timeout=180,
            )
            blob = routed.stdout + routed.stderr
            self.assertEqual(routed.returncode, 0, blob[-4000:])
            found = re.search(r"(\d+) passed", blob)
            self.assertIsNotNone(found, blob[-500:])
            self.assertGreaterEqual(int(found.group(1)), 90)

    def test_cortex_netie_path_applies_on_main(self) -> None:
        patch = PATCHES / "cortex-netie-path.patch"
        self.assertTrue(patch.is_file())
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "Cortex"
            clone = _run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    "main",
                    "https://github.com/Netie-AI/Cortex.git",
                    str(dest),
                ],
                timeout=180,
            )
            self.assertEqual(clone.returncode, 0, clone.stderr)
            applied = _run(["git", "apply", str(patch)], cwd=dest)
            self.assertEqual(applied.returncode, 0, applied.stderr)
            path_py = dest / "CortexOS" / "constitution" / "cortex_path.py"
            self.assertTrue(path_py.is_file())
            blob = path_py.read_text(encoding="utf-8")
            self.assertIn("CODING_TOOLS", blob)
            self.assertIn("package name", blob)
            query = (dest / "CortexOS" / "api" / "dms_query.py").read_text(
                encoding="utf-8"
            )
            self.assertIn(
                "from CortexOS.constitution.cortex_path import RouteDenied, run_question",
                query,
            )
            runner = (dest / "CortexOS" / "execution" / "tool_runner.py").read_text(
                encoding="utf-8"
            )
            self.assertIn("CODING_TOOLS", runner)
            a2a = (dest / "CortexOS" / "api" / "a2a_routes.py").read_text(
                encoding="utf-8"
            )
            self.assertIn("a2a=True", a2a)
            probed = _run(
                [
                    sys.executable,
                    "-c",
                    "import sys; sys.path.insert(0, '.'); "
                    "from CortexOS.constitution.cortex_path import RouteDenied, run_question; "
                    "raised = False\n"
                    "try:\n"
                    "    run_question('minimal')\n"
                    "except RouteDenied as exc:\n"
                    "    raised = 'verified' in str(exc)\n"
                    "print('ok' if raised else 'no')",
                ],
                cwd=dest,
            )
            self.assertEqual(probed.returncode, 0, probed.stderr + probed.stdout)
            self.assertEqual(probed.stdout.strip(), "ok")

    def test_dms_demo_acl_resolve_applies_on_head(self) -> None:
        patch = PATCHES / "dms-demo-acl-resolve.patch"
        self.assertTrue(patch.is_file())
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "dms"
            clone = _run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "https://github.com/Netie-AI/dms.git",
                    str(dest),
                ]
            )
            self.assertEqual(clone.returncode, 0, clone.stderr)
            applied = _run(["git", "apply", str(patch)], cwd=dest)
            self.assertEqual(applied.returncode, 0, applied.stderr)
            src = (
                dest / "packages" / "executor" / "dms_executor" / "__init__.py"
            ).read_text(encoding="utf-8")
            self.assertIn("return resolve_session_acl(", src)
            self.assertIn("acl = self.demo_acl(", src)
            self.assertNotIn('row_predicates={t: "TRUE" for t in readable}', src)

    def test_dms_netie_acl_applies_on_main(self) -> None:
        patch = PATCHES / "dms-netie-acl.patch"
        self.assertTrue(patch.is_file())
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "dms"
            clone = _run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    "main",
                    "https://github.com/Netie-AI/dms.git",
                    str(dest),
                ],
                timeout=180,
            )
            self.assertEqual(clone.returncode, 0, clone.stderr)
            applied = _run(["git", "apply", str(patch)], cwd=dest)
            self.assertEqual(applied.returncode, 0, applied.stderr)
            mod = dest / "packages" / "executor" / "dms_executor" / "netie_acl.py"
            self.assertTrue(mod.is_file())
            blob = mod.read_text(encoding="utf-8")
            self.assertIn("from netie.dms import", blob)
            live = (
                dest / "packages" / "executor" / "dms_executor" / "__init__.py"
            ).read_text(encoding="utf-8")
            self.assertIn("_apply_netie_acl", live)
            spec = importlib.util.spec_from_file_location("netie_acl", mod)
            self.assertIsNotNone(spec)
            loaded = importlib.util.module_from_spec(spec)
            assert spec is not None and spec.loader is not None
            spec.loader.exec_module(loaded)
            out = loaded.answer_or_abstain(
                {"space-ops": frozenset({"inventory"})},
                "space-ops",
                "invoices",
                [{"id": 1}],
                warehouse_id="default",
                binds={"space-ops": "default"},
                sql="SELECT id FROM invoices",
            )
            self.assertEqual(out["status"], "ABSTAIN")
            chat = loaded.answer_or_abstain(
                {"space-ops": frozenset({"inventory"})},
                "space-ops",
                "inventory",
                [{"sku": "A"}],
                warehouse_id="default",
                binds={"space-ops": "default"},
                sql="SELECT sku FROM inventory",
                chat_mode=True,
            )
            self.assertEqual(chat["status"], "ABSTAIN")

    def test_pointer_netie_hands_applies_on_main(self) -> None:
        hands = PATCHES / "pointer-netie-hands.patch"
        observe = PATCHES / "pointer-observe-guard.patch"
        self.assertTrue(hands.is_file() and observe.is_file())
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "Pointer"
            clone = _run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    "main",
                    "https://github.com/Netie-AI/Pointer.git",
                    str(dest),
                ],
                timeout=180,
            )
            self.assertEqual(clone.returncode, 0, clone.stderr)
            for patch in (hands, observe):
                applied = _run(["git", "apply", str(patch)], cwd=dest)
                self.assertEqual(
                    applied.returncode, 0, f"{patch.name}: {applied.stderr}"
                )
            blob = (dest / "electron" / "netie" / "netie_hands.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("bindComputer", blob)
            self.assertIn("hosted computer", blob)
            self.assertIn("guardObserve", blob)
            uacc = (dest / "electron" / "netie" / "uacc.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("filterExecutableSkills", uacc)
            self.assertIn("governed", uacc)
            probed = _run(["node", "test/netie-hands.test.js"], cwd=dest, timeout=60)
            self.assertEqual(probed.returncode, 0, probed.stdout + probed.stderr)
            self.assertIn("ok 6 passed", probed.stdout + probed.stderr)
            obs = _run(["node", "test/netie-observe.test.js"], cwd=dest, timeout=60)
            self.assertEqual(obs.returncode, 0, obs.stdout + obs.stderr)
            self.assertIn("ok 5 passed", obs.stdout + obs.stderr)
            native = _run(["node", "test/uacc.test.js"], cwd=dest, timeout=60)
            self.assertEqual(native.returncode, 0, native.stdout + native.stderr)
            self.assertIn("16 passed", native.stdout + native.stderr)

    def test_control_netie_board_applies_on_main(self) -> None:
        patch = PATCHES / "control-netie-board.patch"
        self.assertTrue(patch.is_file())
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "netie-control"
            clone = _run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    "main",
                    "https://github.com/Netie-AI/netie-control.git",
                    str(dest),
                ],
                timeout=180,
            )
            self.assertEqual(clone.returncode, 0, clone.stderr)
            applied = _run(["git", "apply", str(patch)], cwd=dest)
            self.assertEqual(applied.returncode, 0, applied.stderr)
            mod = dest / "netie_control" / "netie_board.py"
            self.assertTrue(mod.is_file())
            blob = mod.read_text(encoding="utf-8")
            self.assertIn("from netie.control import", blob)
            app = (dest / "netie_control" / "app.py").read_text(encoding="utf-8")
            self.assertIn('"/v1/guacamole"', app)
            sources = (dest / "netie_control" / "sources.py").read_text(
                encoding="utf-8"
            )
            self.assertIn("guard_issue_board", sources)
            spec = importlib.util.spec_from_file_location("netie_board", mod)
            self.assertIsNotNone(spec)
            loaded = importlib.util.module_from_spec(spec)
            assert spec is not None and spec.loader is not None
            spec.loader.exec_module(loaded)
            with self.assertRaises(loaded.ControlDenied):
                loaded.guard_issue_board(
                    {"items": [{"id": "x", "kind": "rdp"}], "unreachable": []}
                )
            kept = loaded.guard_issue_board(
                {
                    "items": [
                        {
                            "repo": "Netie-AI/dms",
                            "number": 1,
                            "title": "acl wave",
                            "is_epic": True,
                            "blocked": False,
                        }
                    ],
                    "unreachable": [],
                }
            )
            self.assertEqual(kept["items"][0]["title"], "acl wave")

    def test_cortex_web_via_runner_applies_on_main(self) -> None:
        patch = PATCHES / "cortex-web-via-runner.patch"
        self.assertTrue(patch.is_file())
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "Cortex"
            clone = _run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    "main",
                    "https://github.com/Netie-AI/Cortex.git",
                    str(dest),
                ],
                timeout=180,
            )
            self.assertEqual(clone.returncode, 0, clone.stderr)
            applied = _run(["git", "apply", str(patch)], cwd=dest)
            self.assertEqual(applied.returncode, 0, applied.stderr)
            broker = (dest / "CortexOS" / "execution" / "agent_task.py").read_text(
                encoding="utf-8"
            )
            start = broker.index("def default_broker")
            end = broker.index("\ndef ", start + 1)
            body = broker[start:end]
            self.assertNotIn("WEB_TOOLS", body)
            self.assertNotIn("DISCOVERY_TOOLS", body)
            self.assertIn("run_tool_call", body)
            test_py = dest / "tests" / "dms" / "test_broker_no_skip.py"
            self.assertTrue(test_py.is_file())
            src = test_py.read_text(encoding="utf-8")
            self.assertIn("WEB_TOOLS", src)
            self.assertIn("default_broker", src)

    def test_cortex_role_execute_applies_on_main(self) -> None:
        patch = PATCHES / "cortex-role-execute.patch"
        self.assertTrue(patch.is_file())
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "Cortex"
            clone = _run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    "main",
                    "https://github.com/Netie-AI/Cortex.git",
                    str(dest),
                ],
                timeout=180,
            )
            self.assertEqual(clone.returncode, 0, clone.stderr)
            for prior in (
                PATCHES / "cortex-netie-path.patch",
                PATCHES / "cortex-web-via-runner.patch",
                patch,
                PATCHES / "cortex-observe-guard.patch",
            ):
                applied = _run(["git", "apply", str(prior)], cwd=dest)
                self.assertEqual(applied.returncode, 0, f"{prior.name}: {applied.stderr}")
            query = (dest / "CortexOS" / "api" / "dms_query.py").read_text(
                encoding="utf-8"
            )
            self.assertIn('require_role("viewer")', query)
            dag = (dest / "CortexOS" / "api" / "dag_run.py").read_text(encoding="utf-8")
            self.assertIn('require_role("steward")', dag)
            apps = (dest / "CortexOS" / "api" / "app_routes.py").read_text(
                encoding="utf-8"
            )
            self.assertIn('require_role("steward")', apps)
            chat = (dest / "CortexOS" / "api" / "chat_routes.py").read_text(
                encoding="utf-8"
            )
            self.assertIn('require_role("steward")', chat)
            f7 = (dest / "tests" / "dms" / "test_f7_rbac.py").read_text(encoding="utf-8")
            self.assertIn("execute_modules_require_a_key", f7)
            path_py = (dest / "CortexOS" / "constitution" / "cortex_path.py").read_text(
                encoding="utf-8"
            )
            self.assertIn("OBSERVE_TOOLS", path_py)
            self.assertIn("guard_observe", path_py)
            runner = (dest / "CortexOS" / "execution" / "tool_runner.py").read_text(
                encoding="utf-8"
            )
            self.assertIn("OBSERVE_TOOLS", runner)


if __name__ == "__main__":
    unittest.main()
