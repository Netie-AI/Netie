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
    chunk_table,
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
        self.assertIn("extra", extra.text)

    def test_labels_stick_to_following_rows(self) -> None:
        chunks = chunk_table(CORPUS_LABELED)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0].labels, ("warehouse: north",))
        self.assertEqual(chunks[1].labels, ("warehouse: south",))
        north_body = chunks[0].text.split("\n", 1)[1]
        self.assertNotIn("B,2", north_body)


if __name__ == "__main__":
    unittest.main()
