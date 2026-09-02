#!/usr/bin/env python3
"""KB index never dumps a skill body. python3 scripts/test_kb_lookup.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kb_lookup import KbDenied, lookup, show_brief


class KbLookupTests(unittest.TestCase):
    def test_skill_row_is_ids_only(self) -> None:
        out = show_brief(
            {
                "id": "S-0001",
                "kind": "skill",
                "title": "Coordinate as one fleet",
                "status": "active",
                "tags": ["coordination"],
            }
        )
        self.assertEqual(out["id"], "S-0001")
        self.assertEqual(out["source"], "netie-kb")
        self.assertNotIn("body", out)
        self.assertNotIn("skill_body", out)

    def test_skill_with_body_refuses(self) -> None:
        with self.assertRaises(KbDenied) as ctx:
            show_brief(
                {"id": "S-0001", "kind": "skill", "title": "fleet"},
                body="## Steps\n1. Presence first",
            )
        self.assertIn("skill_body", str(ctx.exception))

    def test_rule_corpus_text_is_allowed(self) -> None:
        out = show_brief(
            {"id": "R-0016", "kind": "rule", "title": "skills live in KB"},
            body="Distilled skills live in Netie-KB.",
        )
        self.assertEqual(out["id"], "R-0016")
        self.assertEqual(out["kind"], "rule")

    def test_lookup_finds_id(self) -> None:
        rows = [
            {"id": "S-0004", "kind": "skill", "title": "Find a skill"},
            {"id": "S-0001", "kind": "skill", "title": "fleet"},
        ]
        out = lookup(rows, "S-0004")
        self.assertEqual(out["title"], "Find a skill")
        with self.assertRaises(KbDenied):
            lookup(rows, "S-9999")

    def test_id_with_drop_key_refuses(self) -> None:
        with self.assertRaises(KbDenied):
            show_brief({"id": "skill_body-1", "kind": "skill", "title": "x"})


if __name__ == "__main__":
    unittest.main()
