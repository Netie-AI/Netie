"""headroom: most free capacity first. Algorithm port, not OmniRoute quota fetch.

OmniRoute: headroom = 1 - max(util_5h, util_7d), missing util = 0 (full
headroom, fail-open). We take the two utilization numbers on the target.
We do not fetch 5h/7d plan windows from a provider API.
"""

from __future__ import annotations

import math


def clamp_util(value: float | None) -> float:
    if value is None or not math.isfinite(value):
        return 0.0
    if value <= 0:
        return 0.0
    if value >= 1:
        return 1.0
    return value


def compute_headroom(util_5h: float | None, util_7d: float | None) -> float:
    return 1.0 - max(clamp_util(util_5h), clamp_util(util_7d))


def apply_headroom(
    keys: list[str], sat: dict[str, tuple[float | None, float | None]]
) -> list[str]:
    if not keys:
        return []
    decorated = list(enumerate(keys))
    decorated.sort(
        key=lambda pair: (
            -compute_headroom(*(sat.get(pair[1], (None, None)))),
            pair[0],
        )
    )
    return [k for _, k in decorated]
