"""Append-only hash-chained Crew run log. Not Cortex's ledger. Cannot rewrite.

Crew records what it asked Cortex. Writes that matter still land in Cortex.
"""

from __future__ import annotations

import hashlib
import json
import threading
from pathlib import Path
from typing import Any

GENESIS = "0" * 64


class LedgerBroken(ValueError):
    """Chain does not verify. Do not trust this file."""


class HashLedger:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = threading.Lock()

    def append(self, record: dict[str, Any]) -> str:
        body = json.dumps(record, sort_keys=True, separators=(",", ":"), default=str)
        with self._lock:
            prev = self._tail_hash()
            digest = hashlib.sha256(f"{prev}:{body}".encode()).hexdigest()
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(
                    json.dumps({"hash": digest, "prev": prev, "record": record}) + "\n"
                )
            return digest

    def verify(self) -> int:
        if not self.path.is_file():
            return 0
        prev = GENESIS
        n = 0
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            body = json.dumps(
                row["record"], sort_keys=True, separators=(",", ":"), default=str
            )
            expect = hashlib.sha256(f"{prev}:{body}".encode()).hexdigest()
            if row.get("prev") != prev or row.get("hash") != expect:
                raise LedgerBroken(f"break at entry {n}")
            prev = row["hash"]
            n += 1
        return n

    def _tail_hash(self) -> str:
        if not self.path.is_file():
            return GENESIS
        last = ""
        with self.path.open(encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    last = line
        if not last:
            return GENESIS
        return json.loads(last)["hash"]
