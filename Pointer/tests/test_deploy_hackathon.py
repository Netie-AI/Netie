"""Fail-closed Cloud Run deploy helper (P-017). Does not call real gcloud."""

from __future__ import annotations

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SH = ROOT / "scripts" / "deploy_hackathon.sh"
PS1 = ROOT / "scripts" / "deploy_hackathon.ps1"


def _run_sh(env: dict[str, str], extra_path: str | None = None) -> subprocess.CompletedProcess[str]:
    path = extra_path or os.environ.get("PATH", "")
    merged = {**os.environ, "PATH": path}
    merged.pop("GEMINI_API_KEY", None)
    merged.pop("GOOGLE_API_KEY", None)
    merged.pop("POINTER_ALLOW_REMOTE", None)
    merged.pop("DEPLOY", None)
    for k in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "POINTER_ALLOW_REMOTE", "DEPLOY"):
        if k in env:
            merged[k] = env[k]
    return subprocess.run(
        ["bash", str(SH)],
        cwd=str(ROOT),
        env=merged,
        capture_output=True,
        text=True,
        timeout=20,
    )


class TestDeployHackathonSh(unittest.TestCase):
    def test_scripts_exist(self) -> None:
        self.assertTrue(SH.is_file())
        self.assertTrue(PS1.is_file())
        text = SH.read_text(encoding="utf-8")
        self.assertIn("POINTER_ALLOW_REMOTE", text)
        self.assertIn("--no-allow-unauthenticated", text)
        self.assertNotIn("--allow-unauthenticated", text.replace("--no-allow-unauthenticated", ""))
        ps = PS1.read_text(encoding="utf-8")
        self.assertIn("POINTER_ALLOW_REMOTE", ps)
        self.assertIn("--no-allow-unauthenticated", ps)
        self.assertNotIn("--allow-unauthenticated", ps.replace("--no-allow-unauthenticated", ""))

    def test_refuse_pointer_allow_remote(self) -> None:
        r = _run_sh({"POINTER_ALLOW_REMOTE": "1", "GEMINI_API_KEY": "secret-must-not-print"})
        self.assertNotEqual(r.returncode, 0)
        blob = r.stdout + r.stderr
        self.assertIn("POINTER_ALLOW_REMOTE", blob)
        self.assertNotIn("secret-must-not-print", blob)

    def test_refuse_missing_key(self) -> None:
        r = _run_sh({})
        self.assertNotEqual(r.returncode, 0)
        blob = r.stdout + r.stderr
        self.assertIn("GEMINI_API_KEY", blob)

    def test_dry_run_with_mock_gcloud(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / "gcloud"
            fake.write_text("#!/bin/sh\necho mock-gcloud \"$@\"\nexit 0\n", encoding="utf-8")
            fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
            r = _run_sh(
                {"GEMINI_API_KEY": "secret-must-not-print"},
                extra_path=f"{td}:{os.environ.get('PATH', '')}",
            )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        blob = r.stdout + r.stderr
        self.assertIn("Dry run", blob)
        self.assertIn("pointer-hackathon", blob)
        self.assertIn("asia-southeast1", blob)
        self.assertIn("--no-allow-unauthenticated", blob)
        self.assertNotIn("secret-must-not-print", blob)
        self.assertNotIn("mock-gcloud secrets", blob)

    def test_deploy_without_gcloud_fails(self) -> None:
        r = _run_sh(
            {"GEMINI_API_KEY": "secret-must-not-print", "DEPLOY": "1"},
            extra_path="/usr/bin:/bin",
        )
        self.assertNotEqual(r.returncode, 0)
        blob = r.stdout + r.stderr
        self.assertIn("gcloud", blob)
        self.assertNotIn("secret-must-not-print", blob)


if __name__ == "__main__":
    unittest.main()
