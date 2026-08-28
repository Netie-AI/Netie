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

    def test_hotkey_on_secret_field_refuses(self) -> None:
        with self.assertRaises(PointerDenied) as ctx:
            invoke_hand(
                "hotkey",
                cortex_allowed=True,
                cortex_intent="paste",
                element={"role": "textbox", "name": "Password", "type": "password"},
            )
        self.assertIn("secret", str(ctx.exception))
        out = invoke_hand(
            "hotkey",
            cortex_allowed=True,
            cortex_intent="save",
        )
        self.assertEqual(out["hand"], "hotkey")
        self.assertEqual(out["status"], "allowed")

    def test_action_history_is_brain(self) -> None:
        with self.assertRaises(PointerDenied) as ctx:
            invoke_hand(
                "get_action_history",
                cortex_allowed=True,
                cortex_intent="replay last clicks",
            )
        self.assertIn("brain", str(ctx.exception))

    def test_uncropped_screenshot_refuses(self) -> None:
        with self.assertRaises(PointerDenied) as ctx:
            invoke_hand(
                "screenshot",
                cortex_allowed=True,
                cortex_intent="capture the desktop",
            )
        self.assertIn("screenshot_uncropped", str(ctx.exception))
        with self.assertRaises(PointerDenied):
            invoke_hand(
                "take_snapshot",
                cortex_allowed=True,
                cortex_intent="dump pixels",
                element={"role": "textbox", "name": "Password", "type": "password"},
            )
        out = invoke_hand(
            "get_screen_diff",
            cortex_allowed=True,
            cortex_intent="diff the save button",
            element={"role": "button", "name": "Save"},
        )
        self.assertEqual(out["hand"], "get_screen_diff")
        self.assertTrue(out["crop"])

    def test_process_list_refuses(self) -> None:
        with self.assertRaises(PointerDenied) as ctx:
            invoke_hand(
                "list_processes",
                cortex_allowed=True,
                cortex_intent="see what is running",
            )
        self.assertIn("process_list", str(ctx.exception))

    def test_page_info_is_secret_dump(self) -> None:
        with self.assertRaises(PointerDenied) as ctx:
            invoke_hand(
                "browser_get_page_info",
                cortex_allowed=True,
                cortex_intent="read the form",
                ov_leave=True,
            )
        self.assertIn("page dump", str(ctx.exception))

    def test_hover_on_secret_field_refuses(self) -> None:
        with self.assertRaises(PointerDenied) as ctx:
            invoke_hand(
                "hover",
                cortex_allowed=True,
                cortex_intent="inspect",
                element={"role": "textbox", "name": "Password", "type": "password"},
            )
        self.assertIn("secret", str(ctx.exception))
        out = invoke_hand(
            "hover",
            cortex_allowed=True,
            cortex_intent="inspect save",
            element={"role": "button", "name": "Save"},
        )
        self.assertEqual(out["clicked"], "Save")
        with self.assertRaises(PointerDenied):
            invoke_hand(
                "scroll",
                cortex_allowed=True,
                cortex_intent="scroll the pin",
                element={"role": "textbox", "name": "otp"},
            )
        out = invoke_hand(
            "scroll",
            cortex_allowed=True,
            cortex_intent="scroll the page",
        )
        self.assertEqual(out["hand"], "scroll")

    def test_visual_detect_needs_crop(self) -> None:
        with self.assertRaises(PointerDenied) as ctx:
            invoke_hand(
                "detect_elements_visual",
                cortex_allowed=True,
                cortex_intent="find icons",
            )
        self.assertIn("screenshot_uncropped", str(ctx.exception))

    def test_does_not_import_uacc(self) -> None:
        src = Path(__file__).with_name("pointer_hands.py").read_text(encoding="utf-8")
        self.assertNotIn("import uacc", src)
        self.assertNotIn("from uacc", src)
        self.assertNotIn("os.environ", src)


if __name__ == "__main__":
    unittest.main()
