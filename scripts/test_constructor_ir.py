#!/usr/bin/env python3
"""Constructor IR does not invent Cortex defaults. python3 scripts/test_constructor_ir.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from constructor_action_bind import PieceDenied, bind_action
from constructor_ir import ConstructorIRDenied, compile_ir, ghost_walk, refuse_assumed, topo


def _edge(a: str, b: str) -> dict[str, str]:
    return {"from": a, "to": b}


class ConstructorIRTests(unittest.TestCase):
    def test_empty_graph_invents_nothing(self) -> None:
        with self.assertRaises(ConstructorIRDenied) as ctx:
            compile_ir([])
        self.assertIn("empty", str(ctx.exception))

    def test_unknown_kind_refuses(self) -> None:
        with self.assertRaises(ConstructorIRDenied):
            compile_ir([{"id": "a", "kind": "n8n-node"}])

    def test_cycle_refuses_and_topo_drops_leftovers(self) -> None:
        nodes = [
            {"id": "a", "kind": "connector", "object_type": "crm"},
            {"id": "b", "kind": "app", "object_type": "desk"},
        ]
        edges = [_edge("a", "b"), _edge("b", "a")]
        with self.assertRaises(ConstructorIRDenied):
            compile_ir(nodes, edges)
        self.assertEqual(topo(nodes, edges), [])

    def test_kahn_entry_and_app_sink(self) -> None:
        nodes = [
            {"id": "later", "kind": "app", "object_type": "desk"},
            {"id": "first", "kind": "connector", "object_type": "crm"},
        ]
        ir = compile_ir(nodes, [_edge("first", "later")])
        self.assertEqual(ir["entry_node_id"], "first")
        self.assertEqual(ir["output_node_id"], "later")
        kinds = {n["id"]: n["kind"] for n in ir["nodes"]}
        self.assertEqual(kinds["later"], "EMIT")
        self.assertEqual(kinds["first"], "DOCUMENT_REF")

    def test_unlabeled_tool_and_object_and_tier(self) -> None:
        with self.assertRaises(ConstructorIRDenied):
            compile_ir([{"id": "t", "kind": "tool_call"}])
        with self.assertRaises(ConstructorIRDenied):
            compile_ir([{"id": "c", "kind": "connector"}])
        ir = compile_ir(
            [
                {
                    "id": "t",
                    "kind": "tool_call",
                    "action_type": "export_pptx",
                    "object_type": "deck",
                }
            ]
        )
        self.assertIsNone(ir["nodes"][0]["tier"])
        self.assertTrue(ir["nodes"][0]["requires_confirm"])

    def test_chat_does_not_assume_inventory(self) -> None:
        with self.assertRaises(ConstructorIRDenied):
            refuse_assumed("make a desk", {"object_type": "inventory"})
        refuse_assumed("use inventory rows", {"object_type": "inventory"})
        with self.assertRaises(ConstructorIRDenied):
            compile_ir(
                [{"id": "a", "kind": "app", "object_type": "desk"}],
                assumed={"action_type": "export_pptx"},
                utterance="draw boxes",
            )

    def test_ghost_walk_refuses_fake_order(self) -> None:
        with self.assertRaises(ConstructorIRDenied):
            ghost_walk([{"id": "a", "kind": "mystery"}])
        nodes = [
            {"id": "c", "kind": "connector", "object_type": "crm"},
            {"id": "a", "kind": "app", "object_type": "desk"},
        ]
        self.assertEqual(ghost_walk(nodes, [_edge("c", "a")]), ["c", "a"])

    def test_bind_refuses_unlabeled_and_unknown_piece(self) -> None:
        with self.assertRaises(PieceDenied):
            bind_action("")
        with self.assertRaises(PieceDenied):
            bind_action("activepieces.gmail.send")
        self.assertEqual(bind_action("export_pptx"), "export_pptx")

    def test_unlisted_object_is_dropped_not_invented(self) -> None:
        ir = compile_ir(
            [{"id": "c", "kind": "connector", "object_type": "hr_notes"}]
        )
        self.assertIsNone(ir["nodes"][0]["object_type"])
        kept = compile_ir(
            [{"id": "c", "kind": "connector", "object_type": "inventory"}]
        )
        self.assertEqual(kept["nodes"][0]["object_type"], "inventory")

    def test_unknown_action_and_note_leak_refuse(self) -> None:
        with self.assertRaises(ConstructorIRDenied):
            compile_ir(
                [{"id": "t", "kind": "tool_call", "action_type": "bash"}]
            )
        with self.assertRaises(ConstructorIRDenied) as ctx:
            compile_ir(
                [
                    {
                        "id": "c",
                        "kind": "connector",
                        "object_type": "inventory",
                        "note": "skill_body: SECRET",
                    }
                ]
            )
        self.assertIn("NOTE_LEAK", str(ctx.exception))

    def test_kahn_order_and_disconnected_refuse(self) -> None:
        nodes = [
            {"id": "later", "kind": "app", "object_type": "desk"},
            {"id": "first", "kind": "connector", "object_type": "inventory"},
        ]
        ir = compile_ir(nodes, [_edge("first", "later")])
        self.assertEqual([n["id"] for n in ir["nodes"]], ["first", "later"])
        with self.assertRaises(ConstructorIRDenied):
            compile_ir(
                [
                    {"id": "a", "kind": "connector", "object_type": "inventory"},
                    {"id": "b", "kind": "app", "object_type": "desk"},
                ]
            )
        with self.assertRaises(ConstructorIRDenied):
            compile_ir(
                [
                    {
                        "id": "c",
                        "kind": "connector",
                        "object_type": "inventory",
                        "data_point": "salary",
                    }
                ]
            )
        with self.assertRaises(ConstructorIRDenied):
            compile_ir(
                [
                    {
                        "id": "c",
                        "kind": "connector",
                        "object_type": "inventory",
                        "fetch_from": "warehouse.hr_notes",
                    }
                ]
            )


if __name__ == "__main__":
    unittest.main()
