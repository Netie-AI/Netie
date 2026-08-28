#!/usr/bin/env python3
"""Two Spaces, named warehouse: abstain outside ACL. python3 scripts/test_dms_space_acl.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dms_space_acl import (
    DEMO_ALL_TABLES,
    SpaceDenied,
    answer_or_abstain,
    browse_or_abstain,
    mint_manifest,
    tables_for_space,
    warehouse_for_space,
)


ACL = {
    "space-ops": frozenset({"inventory", "shipments"}),
    "space-finance": frozenset({"invoices"}),
}
BINDS = {
    "space-ops": "dms-demo",
    "space-finance": "dms-demo",
}
SQL = "SELECT sku FROM inventory"


def _ask(
    space: str,
    table: str,
    rows: list[dict],
    *,
    warehouse_id: str = "dms-demo",
    sql: str = SQL,
) -> dict:
    return answer_or_abstain(
        ACL,
        space,
        table,
        rows,
        warehouse_id=warehouse_id,
        binds=BINDS,
        sql=sql,
    )


class SpaceAclTests(unittest.TestCase):
    def test_ops_cannot_read_invoices(self) -> None:
        out = _ask("space-ops", "invoices", [{"id": 1, "amount": 9}])
        self.assertEqual(out["status"], "ABSTAIN")
        self.assertEqual(out["rows"], [])

    def test_finance_cannot_read_inventory(self) -> None:
        out = _ask("space-finance", "inventory", [{"sku": "A"}])
        self.assertEqual(out["status"], "ABSTAIN")

    def test_ops_can_read_own_table(self) -> None:
        rows = [{"sku": "A"}]
        out = _ask("space-ops", "inventory", rows)
        self.assertEqual(out["status"], "OK")
        self.assertEqual(out["rows"], rows)
        self.assertEqual(out["warehouse_id"], "dms-demo")
        self.assertEqual(out["sql"], SQL)
        out["rows"][0]["sku"] = "LEAK"
        self.assertEqual(rows[0]["sku"], "A")

    def test_row_declaring_other_table_abstains(self) -> None:
        out = _ask(
            "space-ops",
            "inventory",
            [{"sku": "A", "table": "invoices"}],
        )
        self.assertEqual(out["status"], "ABSTAIN")
        self.assertEqual(out["rows"], [])

    def test_unknown_space_abstains(self) -> None:
        out = _ask("space-other", "inventory", [{"sku": "A"}])
        self.assertEqual(out["status"], "ABSTAIN")

    def test_cortex_warehouse_does_not_answer_dms_space(self) -> None:
        out = _ask(
            "space-ops",
            "inventory",
            [{"sku": "A"}],
            warehouse_id="cortex-demo",
        )
        self.assertEqual(out["status"], "ABSTAIN")
        self.assertEqual(out["rows"], [])
        self.assertIn("cortex-demo", out["reason"])

    def test_blank_sql_abstains(self) -> None:
        out = _ask("space-ops", "inventory", [{"sku": "A"}], sql="  ")
        self.assertEqual(out["status"], "ABSTAIN")
        self.assertEqual(out["rows"], [])

    def test_sql_join_to_ungranted_table_abstains(self) -> None:
        out = _ask(
            "space-ops",
            "inventory",
            [{"sku": "A"}],
            sql="SELECT sku FROM inventory JOIN hr_notes ON true",
        )
        self.assertEqual(out["status"], "ABSTAIN")
        self.assertEqual(out["rows"], [])
        self.assertIn("hr_notes", out["reason"])

    def test_sql_join_to_granted_table_ok(self) -> None:
        out = _ask(
            "space-ops",
            "inventory",
            [{"sku": "A"}],
            sql="SELECT sku FROM inventory JOIN shipments ON true",
        )
        self.assertEqual(out["status"], "OK")

    def test_sql_that_omits_asked_table_abstains(self) -> None:
        out = _ask(
            "space-ops",
            "inventory",
            [{"sku": "A"}],
            sql="SELECT 1",
        )
        self.assertEqual(out["status"], "ABSTAIN")
        self.assertIn("does not name inventory", out["reason"])

    def test_mint_does_not_leak_demo_acl(self) -> None:
        granted = mint_manifest(ACL, "space-finance")
        self.assertEqual(granted, ("invoices",))
        self.assertNotEqual(set(granted), set(DEMO_ALL_TABLES))

    def test_empty_space_denied(self) -> None:
        with self.assertRaises(SpaceDenied):
            tables_for_space({"space-empty": frozenset()}, "space-empty")

    def test_unbound_space_denied(self) -> None:
        with self.assertRaises(SpaceDenied):
            warehouse_for_space({"space-ops": "dms-demo"}, "space-finance")

    def test_bronze_browse_still_needs_grant(self) -> None:
        leak = browse_or_abstain(ACL, "space-ops", "invoices", tier="bronze")
        self.assertEqual(leak["status"], "ABSTAIN")
        self.assertEqual(leak["rows"], [])
        ok = browse_or_abstain(ACL, "space-ops", "inventory", tier="bronze")
        self.assertEqual(ok["status"], "OK")
        self.assertEqual(ok["tier"], "bronze")
        bad = browse_or_abstain(ACL, "space-ops", "inventory", tier="lake")
        self.assertEqual(bad["status"], "ABSTAIN")

    def test_chat_mode_is_anythingllm_overlay(self) -> None:
        out = answer_or_abstain(
            ACL,
            "space-ops",
            "inventory",
            [{"sku": "A"}],
            warehouse_id="dms-demo",
            binds=BINDS,
            sql=SQL,
            chat_mode=True,
        )
        self.assertEqual(out["status"], "ABSTAIN")
        self.assertIn("AnythingLLM", out["reason"])
        self.assertEqual(out["rows"], [])


if __name__ == "__main__":
    unittest.main()
