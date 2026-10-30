#!/usr/bin/env python3
"""Governed observe is opt-in. python3 scripts/test_pointer_observe.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pointer_click import PointerDenied
from pointer_observe import guard_observe


class PointerObserveTests(unittest.TestCase):
    def test_no_cortex_allow_refuses(self) -> None:
        with self.assertRaises(PointerDenied) as ctx:
            guard_observe(cortex_allowed=False, cortex_intent="see")
        self.assertIn("no Cortex allow", str(ctx.exception))

    def test_no_intent_refuses(self) -> None:
        with self.assertRaises(PointerDenied) as ctx:
            guard_observe(cortex_allowed=True, cortex_intent="  ")
        self.assertIn("no Cortex intent", str(ctx.exception))

    def test_visibility_only_is_ok(self) -> None:
        out = guard_observe(cortex_allowed=True, cortex_intent="hud check")
        self.assertTrue(out["ok"])
        self.assertTrue(out["governed"])
        self.assertIsNone(out["screenshot"])
        self.assertIsNone(out["clipboard"])
        self.assertEqual(out["windows"], [])
        self.assertIsNone(out["foreground"])

    def test_uncropped_png_refuses(self) -> None:
        with self.assertRaises(PointerDenied) as ctx:
            guard_observe(
                cortex_allowed=True,
                cortex_intent="see the desktop",
                screenshot="data:image/png;base64,AAA",
            )
        self.assertIn("screenshot_uncropped", str(ctx.exception))

    def test_clipboard_refuses(self) -> None:
        with self.assertRaises(PointerDenied) as ctx:
            guard_observe(
                cortex_allowed=True,
                cortex_intent="read pasteboard",
                clipboard="secret token",
            )
        self.assertIn("clipboard", str(ctx.exception))

    def test_window_list_refuses(self) -> None:
        with self.assertRaises(PointerDenied) as ctx:
            guard_observe(
                cortex_allowed=True,
                cortex_intent="see titles",
                windows=[{"title": "1Password"}],
            )
        self.assertIn("window_dump", str(ctx.exception))
        with self.assertRaises(PointerDenied):
            guard_observe(
                cortex_allowed=True,
                cortex_intent="see focused",
                foreground={"title": "Bank"},
            )

    def test_labeled_crop_confirms_without_pixels(self) -> None:
        out = guard_observe(
            cortex_allowed=True,
            cortex_intent="crop the save button",
            screenshot="data:image/png;base64,AAA",
            crop={"role": "button", "name": "Save"},
        )
        self.assertTrue(out["crop"])
        self.assertEqual(out["clicked"], "Save")
        self.assertTrue(out["screenshot"]["cropped"])
        self.assertNotIn("dataUrl", out["screenshot"])
        with self.assertRaises(PointerDenied):
            guard_observe(
                cortex_allowed=True,
                cortex_intent="crop password",
                screenshot="data:image/png;base64,AAA",
                crop={"role": "textbox", "name": "Password", "type": "password"},
            )


if __name__ == "__main__":
    unittest.main()
