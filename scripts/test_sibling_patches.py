#!/usr/bin/env python3
"""Accessible product repos: sibling patches still apply. python3 scripts/test_sibling_patches.py

Constructor has no unit-test workflow on HEAD. This gate clones it, applies
docs/patches/constructor-compiler-tests.patch then constructor-empty-graph.patch,
and runs node --test (6 passed).
OpenVault patches are apply-checked on origin/main (full OpenMW pytest needs uv).
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / "docs" / "patches"


def _run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=120,
    )


class SiblingPatchTests(unittest.TestCase):
    def test_constructor_compiler_tests_on_patched_head(self) -> None:
        first = PATCHES / "constructor-compiler-tests.patch"
        second = PATCHES / "constructor-empty-graph.patch"
        self.assertTrue(first.is_file() and second.is_file())
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
            for patch in (first, second):
                applied = _run(["git", "apply", str(patch)], cwd=dest)
                self.assertEqual(applied.returncode, 0, applied.stderr)
            tests = _run(["node", "--test", "tests/compiler.test.cjs"], cwd=dest)
            self.assertEqual(tests.returncode, 0, tests.stdout + tests.stderr)
            self.assertIn("pass 6", tests.stdout + tests.stderr)

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
            self.assertTrue(
                crew.is_file()
                and ctx.is_file()
                and reset.is_file()
                and aware.is_file()
                and cache.is_file()
                and shapes.is_file()
                and chat.is_file()
                and hop.is_file()
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
            proxy = (
                dest / "OpenMW" / "openmw" / "openvault" / "vault" / "proxy.py"
            ).read_text(encoding="utf-8")
            self.assertIn("chat_shape_refusal", proxy)
            self.assertIn("_run_execution_shape", proxy)
            app_py = (dest / "OpenMW" / "openmw" / "openvault" / "app.py").read_text(
                encoding="utf-8"
            )
            self.assertIn('"/api/crew/gate"', app_py)


if __name__ == "__main__":
    unittest.main()
