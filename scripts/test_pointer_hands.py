#!/usr/bin/env python3
"""UACC names sit behind Cortex. python3 scripts/test_pointer_hands.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pointer_click import PointerDenied
from pointer_hands import UACC_HANDS, invoke_hand


class PointerHandsTests(unittest.TestCase):
    def test_lists_sixty_eight_uacc_names(self) -> None:
        self.assertEqual(len(UACC_HANDS), 68)
        self.assertEqual(len(set(UACC_HANDS)), 68)

    def test_unknown_hand_refuses(self) -> None:
        with self.assertRaises(PointerDenied) as ctx:
            invoke_hand(
                "shell.exec",
                cortex_allowed=True,
                cortex_intent="run a command",
            )
        self.assertIn("unknown hand", str(ctx.exception))

    def test_no_cortex_allow_refuses_click(self) -> None:
        with self.assertRaises(PointerDenied):
            invoke_hand(
                "click",
                cortex_allowed=False,
                cortex_intent="save",
                element={"role": "button", "name": "Save"},
            )

    def test_planner_is_a_second_brain(self) -> None:
        with self.assertRaises(PointerDenied) as ctx:
            invoke_hand(
                "uacc_planner",
                cortex_allowed=True,
                cortex_intent="plan the desktop",
            )
        self.assertIn("brain", str(ctx.exception))

    def test_clipboard_is_secret_capture(self) -> None:
        with self.assertRaises(PointerDenied):
            invoke_hand(
                "clipboard_read",
                cortex_allowed=True,
                cortex_intent="read pasteboard",
            )

    def test_execute_js_is_ungoverned(self) -> None:
        with self.assertRaises(PointerDenied) as ctx:
            invoke_hand(
                "browser_execute_js",
                cortex_allowed=True,
                cortex_intent="run js",
                ov_leave=True,
            )
        self.assertIn("script", str(ctx.exception))

    def test_open_url_needs_openvault_leave(self) -> None:
        with self.assertRaises(PointerDenied) as ctx:
            invoke_hand(
                "open_url",
                cortex_allowed=True,
                cortex_intent="open docs",
            )
        self.assertIn("OpenVault", str(ctx.exception))
        out = invoke_hand(
            "open_url",
            cortex_allowed=True,
            cortex_intent="open docs",
            ov_leave=True,
        )
        self.assertEqual(out["hand"], "open_url")
        self.assertEqual(out["status"], "allowed")

    def test_click_hand_uses_fail_closed_click(self) -> None:
        out = invoke_hand(
            "click",
            cortex_allowed=True,
            cortex_intent="save the file",
            element={"role": "button", "name": "Save"},
        )
        self.assertEqual(out["clicked"], "Save")
        with self.assertRaises(PointerDenied):
            invoke_hand(
                "smart_type",
                cortex_allowed=True,
                cortex_intent="log in",
                element={"role": "textbox", "name": "Password", "type": "password"},
            )

    def test_does_not_import_uacc(self) -> None:
        src = Path(__file__).with_name("pointer_hands.py").read_text(encoding="utf-8")
        self.assertNotIn("import uacc", src)
        self.assertNotIn("from uacc", src)
        self.assertNotIn("os.environ", src)


if __name__ == "__main__":
    unittest.main()
