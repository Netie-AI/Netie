"""Hash-chained append-only ledger. A silent edit is detectable."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class Ledger:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("", encoding="utf-8")

    def last_hash(self) -> str:
        last = "0" * 64
        if not self.path.exists() or self.path.stat().st_size == 0:
            return last
        with self.path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                last = row["hash"]
        return last

    def append(self, event: dict[str, Any]) -> str:
        prev = self.last_hash()
        body = json.dumps({"prev": prev, "event": event}, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
        row = {"prev": prev, "hash": digest, "event": event}
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
        return digest

    def verify_chain(self) -> None:
        prev = "0" * 64
        if not self.path.exists():
            return
        with self.path.open(encoding="utf-8") as fh:
            for i, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                body = json.dumps(
                    {"prev": row["prev"], "event": row["event"]},
                    sort_keys=True,
                    separators=(",", ":"),
                )
                expect = hashlib.sha256(body.encode("utf-8")).hexdigest()
                if row["prev"] != prev:
                    raise ValueError(f"ledger break at line {i}: prev mismatch")
                if row["hash"] != expect:
                    raise ValueError(f"ledger break at line {i}: hash mismatch")
                prev = row["hash"]
