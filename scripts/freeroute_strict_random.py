"""strict-random: 9th FreeRoute strategy. Algorithm port, not OmniRoute source.

First pick: shuffle-deck without replacement (same idea as OpenVault
`rr_state.get_next_from_deck`). Remainder: shuffle so a failing first pick
does not always fall to the same peer (OmniRoute issue #3959, reimplemented
in Python; do not vendor OmniRoute).
"""

from __future__ import annotations

import random
import threading
from dataclasses import dataclass

MAX_IN_FLIGHT_NOTE = "Crew cap is separate. This is key/target ordering only."


@dataclass
class _Deck:
    order: list[str]
    index: int
    ids_key: str


_decks: dict[str, _Deck] = {}
_lock = threading.Lock()


def fisher_yates(items: list[str]) -> list[str]:
    result = list(items)
    for i in range(len(result) - 1, 0, -1):
        j = random.randrange(i + 1)
        result[i], result[j] = result[j], result[i]
    return result


def _ids_key(item_ids: list[str]) -> str:
    return ",".join(sorted(item_ids))


def next_from_deck(namespace: str, item_ids: list[str]) -> str:
    if not item_ids:
        return ""
    if len(item_ids) == 1:
        return item_ids[0]
    with _lock:
        key = _ids_key(item_ids)
        existing = _decks.get(namespace)
        if existing and existing.ids_key == key and existing.index < len(existing.order):
            chosen = existing.order[existing.index]
            _decks[namespace] = _Deck(existing.order, existing.index + 1, key)
            return chosen
        last_used = None
        if existing and existing.ids_key == key and existing.order:
            last_used = existing.order[-1]
        new_order = fisher_yates(item_ids)
        if last_used is not None and new_order[0] == last_used and len(new_order) > 1:
            swap_idx = 1 + random.randrange(len(new_order) - 1)
            new_order[0], new_order[swap_idx] = new_order[swap_idx], new_order[0]
        _decks[namespace] = _Deck(new_order, 1, key)
        return new_order[0]


def reset_decks() -> None:
    with _lock:
        _decks.clear()


def apply_strict_random(keys: list[str], *, combo_name: str) -> list[str]:
    if not keys:
        return []
    chosen = next_from_deck(f"strict:{combo_name}", keys)
    rest = fisher_yates([k for k in keys if k != chosen])
    return [chosen, *rest]
