#!/usr/bin/env python3
"""Space AI/OCR cannot skip OpenVault. python3 scripts/test_space_leave.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crew_ov_gate import OpenVaultCrewGate
from space_leave import SpaceLeaveDenied, leave, persist_key, resolve_login, may_preview, ocr_cloud


def _allow(url: str, body: dict[str, Any]) -> dict[str, Any]:
    return {"allowed": True, "found": True}


def _deny(url: str, body: dict[str, Any]) -> dict[str, Any]:
    return {"allowed": False, "reason": "leave refused"}


class SpaceLeaveTests(unittest.TestCase):
    def test_direct_provider_without_allow_is_denied(self) -> None:
        ov = OpenVaultCrewGate("http://127.0.0.1:5000", post=_deny)
        with self.assertRaises(SpaceLeaveDenied):
            leave(
                ov,
                intent="leave",
                parent_run_id="p1",
                child_id="chat",
                deficit="summarize preview",
            )

    def test_gate_allow_returns(self) -> None:
        ov = OpenVaultCrewGate("http://127.0.0.1:5000", post=_allow)
        out = leave(
            ov,
            intent="leave",
            parent_run_id="p1",
            child_id="chat",
            deficit="summarize preview",
        )
        self.assertTrue(out["allowed"])

    def test_plaintext_key_write_denied(self) -> None:
        with self.assertRaises(SpaceLeaveDenied):
            persist_key("user.env", plaintext=True)

    def test_user_env_denied_even_when_not_marked_plaintext(self) -> None:
        with self.assertRaises(SpaceLeaveDenied) as ctx:
            persist_key(r"%LOCALAPPDATA%\NetieSpace\user.env", plaintext=False)
        self.assertIn("secret write", str(ctx.exception))

    def test_key_file_write_denied_even_when_not_marked_plaintext(self) -> None:
        with self.assertRaises(SpaceLeaveDenied):
            persist_key("id_rsa", plaintext=False)
        with self.assertRaises(SpaceLeaveDenied):
            persist_key("certs/prod.pem", plaintext=False)

    def test_local_vault_scan_denied(self) -> None:
        with self.assertRaises(SpaceLeaveDenied):
            resolve_login(openvault_ok=False, scan_local_vault=True)

    def test_env_file_is_not_a_preview(self) -> None:
        with self.assertRaises(SpaceLeaveDenied) as ctx:
            may_preview("user.env")
        self.assertIn("secret preview", str(ctx.exception))
        with self.assertRaises(SpaceLeaveDenied):
            may_preview("certs/prod.pem")
        with self.assertRaises(SpaceLeaveDenied):
            may_preview(".netrc")
        with self.assertRaises(SpaceLeaveDenied):
            may_preview("Keys.txt")
        with self.assertRaises(SpaceLeaveDenied):
            persist_key("Keys.txt", plaintext=False)
        self.assertEqual(may_preview("report.pdf"), "preview")

    def test_poor_ocr_does_not_grant_baidu(self) -> None:
        with self.assertRaises(SpaceLeaveDenied) as ctx:
            ocr_cloud("scan.png", ov_allowed=False, local_chars=3)
        self.assertIn("poor local OCR", str(ctx.exception))
        self.assertEqual(
            ocr_cloud("scan.png", ov_allowed=True, local_chars=3),
            "cloud",
        )


if __name__ == "__main__":
    unittest.main()
