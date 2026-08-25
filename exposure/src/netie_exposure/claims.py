"""Strip overclaims. A draft that cannot cite a catalog URL does not ship."""

from __future__ import annotations

import json
from pathlib import Path

_DATA = Path(__file__).resolve().parent / "data" / "claims_deny.json"


def _phrases() -> list[str]:
    payload = json.loads(_DATA.read_text(encoding="utf-8"))
    return [p.lower() for p in payload["phrases"]]


def laptop_ascii(text: str) -> str:
    """NETIE.md rule 10: no em dash, curly quotes, arrow glyphs."""
    table = {
        "\u2014": "-",
        "\u2013": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2192": "->",
        "\u2026": "...",
        "\xa0": " ",
    }
    out = text
    for src, dst in table.items():
        out = out.replace(src, dst)
    return out


def find_denied(text: str) -> list[str]:
    lowered = text.lower()
    return [p for p in _phrases() if p in lowered]


def assert_clean(text: str) -> str:
    """Return laptop-ASCII text or raise ValueError listing denied phrases."""
    cleaned = laptop_ascii(text)
    hits = find_denied(cleaned)
    if hits:
        raise ValueError("denied claims: " + ", ".join(hits))
    return cleaned
