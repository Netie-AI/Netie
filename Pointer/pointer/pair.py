"""Pairing and approval tokens. Generated locally, never committed."""

from __future__ import annotations

import json
import secrets
from pathlib import Path


class PairStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write(
                {
                    "pair_token": secrets.token_urlsafe(32),
                    "approval_token": secrets.token_urlsafe(32),
                }
            )

    def _write(self, data: dict[str, str]) -> None:
        self.path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        try:
            self.path.chmod(0o600)
        except OSError:
            pass

    def load(self) -> dict[str, str]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def rotate_approval(self) -> str:
        data = self.load()
        data["approval_token"] = secrets.token_urlsafe(32)
        self._write(data)
        return data["approval_token"]
