#!/usr/bin/env python3
"""Founder apply-all stays a local apply. python3 scripts/test_apply_product_patches.py

Does not clone product remotes (sibling already does). Asserts patch files
exist, order matches STACKS, constructor extras stay mixed-out, and --push
refuses.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from apply_product_patches import (
    CONSTRUCTOR_26,
    CONSTRUCTOR_EXTRAS,
    OPENVAULT_STACK,
    PATCHES,
    ROOT,
    STACKS,
    main,
)


class ApplyProductPatchesTests(unittest.TestCase):
    def test_every_stack_patch_exists(self) -> None:
        for name, stack in STACKS.items():
            self.assertTrue(stack.patches, name)
            for patch_name in stack.patches:
                path = PATCHES / patch_name
                self.assertTrue(path.is_file(), f"{name}: missing {patch_name}")

    def test_constructor_does_not_mix_extras(self) -> None:
        self.assertEqual(len(CONSTRUCTOR_26), 26)
        self.assertEqual(STACKS["constructor"].patches, CONSTRUCTOR_26)
        for extra in CONSTRUCTOR_EXTRAS:
            self.assertNotIn(extra, STACKS["constructor"].patches)
            self.assertTrue((PATCHES / extra).is_file(), extra)

    def test_openvault_crew_gate_before_crew_netie(self) -> None:
        names = list(OPENVAULT_STACK)
        self.assertLess(
            names.index("openvault-crew-gate.patch"),
            names.index("openvault-crew-netie.patch"),
        )
        self.assertLess(
            names.index("openvault-crew-netie.patch"),
            names.index("openvault-crew-skill-ids.patch"),
        )
        self.assertLess(
            names.index("openvault-crew-skill-ids.patch"),
            names.index("openvault-free-pool.patch"),
        )
        self.assertLess(
            names.index("openvault-free-pool-route.patch"),
            names.index("openvault-ship-claim-ov.patch"),
        )
        self.assertEqual(STACKS["openvault"].patches, OPENVAULT_STACK)
        self.assertTrue(STACKS["openvault"].uv_add_netie)

    def test_cortex_never_uv_adds_netie(self) -> None:
        self.assertFalse(STACKS["cortex"].uv_add_netie)
        self.assertEqual(
            STACKS["cortex"].patches,
            (
                "cortex-netie-path.patch",
                "cortex-web-via-runner.patch",
                "cortex-role-execute.patch",
                "cortex-observe-guard.patch",
            ),
        )

    def test_pointer_observe_after_hands(self) -> None:
        names = list(STACKS["pointer"].patches)
        self.assertEqual(names[0], "pointer-netie-hands.patch")
        self.assertEqual(names[1], "pointer-observe-guard.patch")

    def test_kb_index_is_a_stack(self) -> None:
        self.assertEqual(STACKS["kb"].patches, ("kb-netie-index.patch",))
        self.assertTrue(STACKS["kb"].uv_add_netie)

    def test_readme_names_each_stack_patch(self) -> None:
        readme = (ROOT / "docs" / "patches" / "README.md").read_text(encoding="utf-8")
        for name, stack in STACKS.items():
            for patch_name in stack.patches:
                self.assertIn(patch_name, readme, f"{name}: {patch_name}")
        self.assertIn("python3 scripts/apply_product_patches.py", readme)
        self.assertIn("do not mix", readme.lower())

    def test_script_source_never_pushes(self) -> None:
        src = (ROOT / "scripts" / "apply_product_patches.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn('["git", "push"', src)
        self.assertNotIn("git push origin", src)
        self.assertIn("do not push", src)
        self.assertIn("refuse mix", src)

    def test_push_flag_refuses(self) -> None:
        code = main(["--push", "--dry-run"])
        self.assertEqual(code, 2)

    def test_dry_run_prints_order_without_clone(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "apply_product_patches.py"),
                "--product",
                "pointer",
                "--dry-run",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("pointer-netie-hands.patch", proc.stdout)
        self.assertIn("pointer-observe-guard.patch", proc.stdout)
        self.assertIn("do not push", proc.stdout)
        self.assertNotIn("Cloning", proc.stdout)

    def test_apply_stack_refuses_constructor_extras(self) -> None:
        src = (ROOT / "scripts" / "apply_product_patches.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("CONSTRUCTOR_EXTRAS", src)
        self.assertIn("refuse mix", src)
        for extra in CONSTRUCTOR_EXTRAS:
            self.assertNotIn(extra, STACKS["constructor"].patches)


if __name__ == "__main__":
    unittest.main()
