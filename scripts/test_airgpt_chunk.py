#!/usr/bin/env python3
"""Table corpus for AirGPT ingest. python3 scripts/test_airgpt_chunk.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from airgpt_chunk import (
    CORPUS_LABELED,
    CORPUS_RAGGED,
    CORPUS_REPEATED_HEADER,
    Chunk,
    chunk_table,
    retrieve_space,
)


class AirgptChunkTests(unittest.TestCase):
    def test_repeated_header_is_not_a_row(self) -> None:
        chunks = chunk_table(CORPUS_REPEATED_HEADER)
        self.assertEqual(len(chunks), 2)
        self.assertTrue(all(c.header == "item,qty" for c in chunks))
        self.assertTrue(all(not c.incomplete for c in chunks))
        self.assertIn("a,1", chunks[0].text)
        self.assertIn("b,2", chunks[1].text)

    def test_ragged_row_does_not_invent_cells(self) -> None:
        chunks = chunk_table(CORPUS_RAGGED)
        short = next(c for c in chunks if c.text.endswith("B2|3"))
        self.assertTrue(short.incomplete)
        self.assertNotIn("KL", short.text.split("\n", 1)[1])
        extra = next(c for c in chunks if "C3" in c.text)
        self.assertTrue(extra.incomplete)
        self.assertNotIn("extra", extra.text.split("\n", 1)[1])
        self.assertEqual(extra.text.split("\n", 1)[1].count("|"), extra.header.count("|"))

    def test_labels_stick_to_following_rows(self) -> None:
        chunks = chunk_table(CORPUS_LABELED)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0].labels, ("warehouse: north",))
        self.assertEqual(chunks[1].labels, ("warehouse: south",))
        north_body = chunks[0].text.split("\n", 1)[1]
        self.assertNotIn("B,2", north_body)

    def test_north_retrieve_does_not_cite_south(self) -> None:
        chunks = chunk_table(CORPUS_LABELED)
        north = retrieve_space(chunks, space="north", query="A,1")
        self.assertEqual(north["status"], "OK")
        self.assertEqual(len(north["chunks"]), 1)
        self.assertIn("A,1", north["chunks"][0].text)
        south_leak = retrieve_space(chunks, space="north", query="B,2")
        self.assertEqual(south_leak["status"], "ABSTAIN")
        self.assertEqual(south_leak["chunks"], [])

    def test_incomplete_row_is_not_evidence(self) -> None:
        labeled_ragged = """# warehouse: ops
sku|qty|dest
B2|3
"""
        chunks = chunk_table(labeled_ragged)
        self.assertEqual(len(chunks), 1)
        self.assertTrue(chunks[0].incomplete)
        out = retrieve_space(chunks, space="ops", query="B2")
        self.assertEqual(out["status"], "ABSTAIN")
        self.assertEqual(out["chunks"], [])

    def test_unlabeled_chunk_does_not_join_a_named_space(self) -> None:
        chunks = chunk_table(CORPUS_REPEATED_HEADER)
        out = retrieve_space(chunks, space="north", query="a,1")
        self.assertEqual(out["status"], "ABSTAIN")
        self.assertEqual(out["chunks"], [])

    def test_chat_md_is_not_evidence(self) -> None:
        chunks = [
            Chunk(
                text="sku,qty\nA,1",
                header="sku,qty",
                incomplete=False,
                labels=("warehouse: north",),
                source="spaces/5/chat_abc.md",
            ),
            Chunk(
                text="sku,qty\nA,1",
                header="sku,qty",
                incomplete=False,
                labels=("warehouse: north",),
                source="spaces/5/inventory.csv",
            ),
        ]
        out = retrieve_space(chunks, space="north", query="A,1")
        self.assertEqual(out["status"], "OK")
        self.assertEqual(len(out["chunks"]), 1)
        self.assertTrue(out["chunks"][0].source.endswith("inventory.csv"))
        chat_only = retrieve_space(
            chunks[:1], space="north", query="A,1", source="chat_abc.md"
        )
        self.assertEqual(chat_only["status"], "ABSTAIN")
        self.assertIn("chats_as_evidence", chat_only["reason"])
        opted = retrieve_space(
            chunks[:1], space="north", query="A,1", chats_as_evidence=True
        )
        self.assertEqual(opted["status"], "OK")

    def test_file_mention_stays_in_space(self) -> None:
        chunks = [
            Chunk(
                text="sku,qty\nA,1",
                header="sku,qty",
                incomplete=False,
                labels=("warehouse: north",),
                source="inventory.csv",
            ),
            Chunk(
                text="sku,qty\nA,1",
                header="sku,qty",
                incomplete=False,
                labels=("warehouse: south",),
                source="hr.csv",
            ),
        ]
        leak = retrieve_space(chunks, space="north", query="A,1", source="hr.csv")
        self.assertEqual(leak["status"], "ABSTAIN")
        self.assertEqual(leak["chunks"], [])
        ok = retrieve_space(
            chunks, space="north", query="A,1", source="inventory.csv"
        )
        self.assertEqual(ok["status"], "OK")
        self.assertEqual(ok["chunks"][0].source, "inventory.csv")


if __name__ == "__main__":
    unittest.main()
