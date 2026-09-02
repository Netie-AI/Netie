#!/usr/bin/env python3
"""Memory is OV+Cortex ids. python3 scripts/test_ov_memory.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ov_memory import MemoryDenied, recall, remember, refuse_vendor


class OvMemoryTests(unittest.TestCase):
    def test_graphiti_vendor_refuses(self) -> None:
        with self.assertRaises(MemoryDenied):
            refuse_vendor("graphiti")
        with self.assertRaises(MemoryDenied):
            remember("north", "n1", vendor="zep")
        with self.assertRaises(MemoryDenied):
            remember("north", "n1", vendor="graphify")

    def test_remember_is_ids_only(self) -> None:
        row = remember("north", "chunk-1")
        self.assertEqual(row["kind"], "memory")
        self.assertEqual(row["id"], "chunk-1")
        with self.assertRaises(MemoryDenied):
            remember("north", "chunk-1", body="SECRET")
        with self.assertRaises(MemoryDenied):
            remember("", "chunk-1")

    def test_recall_stays_in_space(self) -> None:
        rows = [
            {"space_id": "north", "id": "a"},
            {"space_id": "south", "id": "b"},
        ]
        out = recall(rows, "north")
        self.assertEqual(out, [{"kind": "memory", "space_id": "north", "id": "a"}])
        with self.assertRaises(MemoryDenied):
            recall([{"space_id": "north", "id": "a", "transcript": "hi"}], "north")


if __name__ == "__main__":
    unittest.main()
