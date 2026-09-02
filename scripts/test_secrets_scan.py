#!/usr/bin/env python3
"""Live provider keys stay out of git. python3 scripts/test_secrets_scan.py"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from secrets_scan import ANTHROPIC_LIVE, OPENROUTER_LIVE, findings, FORBIDDEN_TRACKED

ROOT = Path(__file__).resolve().parents[1]


class SecretsScanTests(unittest.TestCase):
    def test_repo_head_has_no_live_openrouter_key(self) -> None:
        self.assertEqual(findings(ROOT), [])

    def test_openrouter_64_hex_is_live(self) -> None:
        blob = "sk-or-v1-" + ("ab" * 32)
        self.assertIsNotNone(OPENROUTER_LIVE.search(blob))
        self.assertIsNone(OPENROUTER_LIVE.search("sk-or-v1-abc123def456ghi789"))
        self.assertIsNone(OPENROUTER_LIVE.search("$OPENROUTER_API_KEY"))

    def test_anthropic_test_fixture_is_allowed(self) -> None:
        self.assertIsNone(ANTHROPIC_LIVE.search("sk-ant-test-anth-hop-aaaaaaaa"))
        live = "sk-ant-" + "api03-not-a-test-key"
        self.assertIsNotNone(ANTHROPIC_LIVE.search(live))

    def test_keys_txt_basename_is_forbidden(self) -> None:
        self.assertIn("keys.txt", FORBIDDEN_TRACKED)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Keys.txt").write_text("OpenRouter: $OPENROUTER_API_KEY\n", encoding="utf-8")
            rows = findings(root)
        self.assertTrue(any("forbidden tracked secrets file" in r for r in rows))

    def test_detects_live_key_in_curl_sample(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sample.txt").write_text(
                'Authorization: Bearer sk-or-v1-' + ("cd" * 32) + "\n",
                encoding="utf-8",
            )
            rows = findings(root)
        self.assertTrue(any("OpenRouter live key" in r for r in rows))


if __name__ == "__main__":
    unittest.main()
