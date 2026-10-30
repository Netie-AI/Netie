#!/usr/bin/env python3
"""Unlabeled click is refused. python3 scripts/test_pointer_click.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pointer_click import PointerDenied, click, may_click


class PointerClickTests(unittest.TestCase):
    def test_unlabeled_is_refused(self) -> None:
        el = {"role": "button", "bounds": [0, 0, 10, 10]}
        self.assertFalse(may_click(el))
        with self.assertRaises(PointerDenied):
            click(el, cortex_intent="submit form")

    def test_no_cortex_intent_is_refused(self) -> None:
        el = {"role": "button", "name": "Save"}
        with self.assertRaises(PointerDenied):
            click(el, cortex_intent=None)

    def test_named_button_clicks(self) -> None:
        el = {"role": "button", "name": "Save"}
        out = click(el, cortex_intent="save the file")
        self.assertEqual(out["clicked"], "Save")

    def test_password_field_is_refused(self) -> None:
        el = {"role": "textbox", "name": "Password", "type": "password"}
        self.assertFalse(may_click(el))
        with self.assertRaises(PointerDenied) as ctx:
            click(el, cortex_intent="log in")
        self.assertIn("secret", str(ctx.exception))

    def test_otp_field_is_refused(self) -> None:
        el = {
            "role": "textbox",
            "name": "OTP",
            "autocomplete": "one-time-code",
        }
        with self.assertRaises(PointerDenied):
            click(el, cortex_intent="enter 2fa")

    def test_does_not_read_env_or_keys(self) -> None:
        import pointer_click as mod

        src = Path(mod.__file__).read_text(encoding="utf-8")
        self.assertNotIn("os.environ", src)
        self.assertNotIn("getenv", src)
        self.assertNotIn("OPENAI_API_KEY", src)


if __name__ == "__main__":
    unittest.main()
