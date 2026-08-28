#!/usr/bin/env python3
"""DMS ontology is granted tables. python3 scripts/test_dms_ontology.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dms_ontology import (
    OntologyDenied,
    evidence_or_abstain,
    link_objects,
    mint_object,
    object_types,
    refuse_vendor,
)


ACL = {
    "space-ops": frozenset({"inventory", "shipments"}),
    "space-finance": frozenset({"invoices"}),
}
BINDS = {
    "space-ops": "dms-demo",
    "space-finance": "dms-demo",
}


class DmsOntologyTests(unittest.TestCase):
    def test_objects_are_granted_tables(self) -> None:
        self.assertEqual(object_types(ACL, "space-ops"), ("inventory", "shipments"))
        self.assertEqual(mint_object(ACL, "space-ops", "inventory"), "inventory")
        with self.assertRaises(OntologyDenied):
            mint_object(ACL, "space-ops", "invoices")
        with self.assertRaises(OntologyDenied):
            mint_object(ACL, "space-ops", "hr_notes")
        with self.assertRaises(OntologyDenied):
            mint_object(ACL, "space-ops", "")

    def test_palantir_vendor_refuses(self) -> None:
        with self.assertRaises(OntologyDenied):
            refuse_vendor("Palantir")
        with self.assertRaises(OntologyDenied):
            mint_object(ACL, "space-ops", "inventory", vendor="foundry")

    def test_link_stays_inside_grant(self) -> None:
        self.assertEqual(
            link_objects(ACL, "space-ops", "inventory", "shipments"),
            ("inventory", "shipments"),
        )
        with self.assertRaises(OntologyDenied):
            link_objects(ACL, "space-ops", "inventory", "invoices")

    def test_evidence_must_cite_granted_table(self) -> None:
        ok = evidence_or_abstain(
            ACL,
            "space-ops",
            {"table": "inventory", "sku": "A"},
            warehouse_id="dms-demo",
            binds=BINDS,
        )
        self.assertEqual(ok["status"], "OK")
        miss = evidence_or_abstain(
            ACL,
            "space-ops",
            {"sku": "A"},
            warehouse_id="dms-demo",
            binds=BINDS,
        )
        self.assertEqual(miss["status"], "ABSTAIN")
        leak = evidence_or_abstain(
            ACL,
            "space-ops",
            {"table": "invoices", "amount": 9},
            warehouse_id="dms-demo",
            binds=BINDS,
        )
        self.assertEqual(leak["status"], "ABSTAIN")
        wrong = evidence_or_abstain(
            ACL,
            "space-ops",
            {"table": "inventory"},
            warehouse_id="cortex-duck",
            binds=BINDS,
        )
        self.assertEqual(wrong["status"], "ABSTAIN")


if __name__ == "__main__":
    unittest.main()
