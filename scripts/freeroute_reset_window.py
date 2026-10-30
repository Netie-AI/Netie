"""reset-window: soonest quota reset first.

OmniRoute sorts on milliseconds until the configured window resets, collapsing
already-elapsed resets to 0 and sending unknown resets to the back (Infinity).
FreeRoute does not fetch provider quota snapshots. Callers set remaining_ms.
Ties keep input order. Tie-band rotation is not ported.
"""

from __future__ import annotations


def remaining_or_inf(value: float | None) -> float:
    if value is None:
        return float("inf")
    if value != value:  # NaN
        return float("inf")
    return max(0.0, value)


def apply_reset_window(
    keys: list[str], remaining_ms: dict[str, float | None]
) -> list[str]:
    if not keys:
        return []
    decorated = list(enumerate(keys))
    decorated.sort(
        key=lambda pair: (remaining_or_inf(remaining_ms.get(pair[1])), pair[0])
    )
    return [k for _, k in decorated]
