"""Pairing and approval tokens. Generated locally, never committed."""

from __future__ import annotations

import json
import secrets
from pathlib import Path


def laptop_next_steps() -> list[str]:
    return [
        "On the Windows laptop, not the cloud VM: copy Pointer/ then run powershell -File scripts/install_windows.ps1",
        "Keep python -m pointer serve on 127.0.0.1:7420. Do not set POINTER_ALLOW_REMOTE=1.",
        "Prove hardware: python -m pointer prove  (writes .pointer-state/PROVE.json, no tokens)",
        "Hold tokens on that machine: python -m pointer pair --card. Use pair --show only locally. Do not email tokens.",
        "This cloud VM cannot click D:\\Pointer. Paste tokens only into a Cursor chat on the laptop, then python -m pointer pair --rotate-approval.",
    ]


def write_card(state_dir: Path, *, show_tokens: bool = False) -> Path:
    store = PairStore(state_dir / "pair.json")
    tokens = store.load()
    lines = [
        "POINTER LAPTOP CARD",
        "Do not commit. Do not email tokens.",
        "health: http://127.0.0.1:7420/health",
        "pay: http://127.0.0.1:7420/pay",
        f"pair_file: {state_dir / 'pair.json'}",
        f"has_pair_token: {bool(tokens.get('pair_token'))}",
        f"has_approval_token: {bool(tokens.get('approval_token'))}",
        "",
        "Next:",
        *[f"{i}. {step}" for i, step in enumerate(laptop_next_steps(), start=1)],
    ]
    if show_tokens:
        lines += [
            "",
            f"pair_token: {tokens['pair_token']}",
            f"approval_token: {tokens['approval_token']}",
        ]
    path = state_dir / "PAIR_CARD.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return path


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
