#!/usr/bin/env python3
"""Accessible product repos: sibling patches still apply. python3 scripts/test_sibling_patches.py

Constructor has no unit-test workflow on HEAD. This gate clones it, applies
docs/patches/constructor-compiler-tests.patch then constructor-empty-graph.patch
then constructor-ir-refuse.patch then constructor-ir-ids.patch then
constructor-ghost-refuse.patch then constructor-ir-emit.patch then
constructor-tool-action.patch then constructor-inspect-action.patch then constructor-inspect-object.patch then constructor-inspect-tier.patch then constructor-chat-object.patch then constructor-topo-leftover.patch then constructor-ir-entry.patch then constructor-ir-output.patch then constructor-ir-object.patch then constructor-ir-bind.patch then constructor-ir-action-allow.patch then constructor-ir-intake.patch, and runs
node --test (42 passed).
OpenVault patches apply on origin/main then `uv run pytest` on the routing+chat+crew-gate files (>= 90 passed).
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / "docs" / "patches"


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
            ):
                applied = _run(["git", "apply", str(patch)], cwd=dest)
                self.assertEqual(applied.returncode, 0, applied.stderr)
            tests = _run(["node", "--test", "tests/compiler.test.cjs"], cwd=dest)
            self.assertEqual(tests.returncode, 0, tests.stdout + tests.stderr)
            self.assertIn("pass 42", tests.stdout + tests.stderr)
            engine = (dest / "engine.js").read_text(encoding="utf-8")
            self.assertIn('WRITE_ACTIONS = ["export_pptx", "item.intake"]', engine)

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
            self.assertIn("crew_body_http", proxy)
            self.assertIn("hop_body_from_chat", budget)
            app_py = (dest / "OpenMW" / "openmw" / "openvault" / "app.py").read_text(
                encoding="utf-8"
            )
            self.assertIn('"/api/crew/gate"', app_py)
            if shutil.which("uv") is None:
                self.fail("uv required to run OpenVault routing tests")
            routed = _run(
                [
                    "uv",
                    "run",
                    "pytest",
                    "tests/test_route_strategies.py",
                    "tests/test_execution_shapes.py",
                    "tests/test_execution_chat.py",
                    "tests/test_freeroute_acceptance.py",
                    "tests/test_freeroute_metering.py",
                    "tests/test_crew_gate.py",
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


if __name__ == "__main__":
    unittest.main()
