#!/usr/bin/env python3
"""Two Spaces, one warehouse: abstain outside ACL. python3 scripts/test_dms_space_acl.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dms_space_acl import (
    DEMO_ALL_TABLES,
    SpaceDenied,
    answer_or_abstain,
    mint_manifest,
    tables_for_space,
)


WAREHOUSE = {
    "space-ops": frozenset({"inventory", "shipments"}),
    "space-finance": frozenset({"invoices"}),
}


class SpaceAclTests(unittest.TestCase):
    def test_ops_cannot_read_invoices(self) -> None:
        out = answer_or_abstain(
            WAREHOUSE, "space-ops", "invoices", [{"id": 1, "amount": 9}]
        )
        self.assertEqual(out["status"], "ABSTAIN")
        self.assertEqual(out["rows"], [])

    def test_finance_cannot_read_inventory(self) -> None:
        out = answer_or_abstain(
            WAREHOUSE, "space-finance", "inventory", [{"sku": "A"}]
        )
        self.assertEqual(out["status"], "ABSTAIN")

    def test_ops_can_read_own_table(self) -> None:
        rows = [{"sku": "A"}]
        out = answer_or_abstain(WAREHOUSE, "space-ops", "inventory", rows)
        self.assertEqual(out["status"], "OK")
        self.assertEqual(out["rows"], rows)
        out["rows"][0]["sku"] = "LEAK"
        self.assertEqual(rows[0]["sku"], "A")

    def test_row_declaring_other_table_abstains(self) -> None:
        out = answer_or_abstain(
            WAREHOUSE,
            "space-ops",
            "inventory",
            [{"sku": "A", "table": "invoices"}],
        )
        self.assertEqual(out["status"], "ABSTAIN")
        self.assertEqual(out["rows"], [])

    def test_unknown_space_abstains(self) -> None:
        out = answer_or_abstain(WAREHOUSE, "space-other", "inventory", [{"sku": "A"}])
        self.assertEqual(out["status"], "ABSTAIN")

    def test_mint_does_not_leak_demo_acl(self) -> None:
        granted = mint_manifest(WAREHOUSE, "space-finance")
        self.assertEqual(granted, ("invoices",))
        self.assertNotEqual(set(granted), set(DEMO_ALL_TABLES))

    def test_empty_space_denied(self) -> None:
        with self.assertRaises(SpaceDenied):
            tables_for_space({"space-empty": frozenset()}, "space-empty")


if __name__ == "__main__":
    unittest.main()
