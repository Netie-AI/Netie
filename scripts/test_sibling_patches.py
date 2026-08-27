#!/usr/bin/env python3
"""Accessible product repos: sibling patches still apply. python3 scripts/test_sibling_patches.py

Constructor has no unit-test workflow on HEAD. This gate clones it, applies
docs/patches/constructor-compiler-tests.patch, and runs node --test.
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
        patch = PATCHES / "constructor-compiler-tests.patch"
        self.assertTrue(patch.is_file())
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
            applied = _run(["git", "apply", str(patch)], cwd=dest)
            self.assertEqual(applied.returncode, 0, applied.stderr)
            tests = _run(["node", "--test", "tests/compiler.test.cjs"], cwd=dest)
            self.assertEqual(tests.returncode, 0, tests.stdout + tests.stderr)
            self.assertIn("pass 3", tests.stdout + tests.stderr)

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
            self.assertTrue(crew.is_file())
            for patch in (detect, strict, lkgp, crew):
                check = _run(["git", "apply", "--check", str(patch)], cwd=dest)
                self.assertEqual(check.returncode, 0, f"{patch.name}: {check.stderr}")
                applied = _run(["git", "apply", str(patch)], cwd=dest)
                self.assertEqual(applied.returncode, 0, f"{patch.name}: {applied.stderr}")
            strategies = (
                dest / "OpenMW" / "openmw" / "openvault" / "route" / "strategies.py"
            ).read_text(encoding="utf-8")
            self.assertIn('if strategy == "lkgp":', strategies)
            app_py = (dest / "OpenMW" / "openmw" / "openvault" / "app.py").read_text(
                encoding="utf-8"
            )
            self.assertIn('"/api/crew/gate"', app_py)


if __name__ == "__main__":
    unittest.main()
