"""reset-aware: remaining quota first; exhausted-and-resetting next.

OmniRoute: session/weekly remaining mixed with reset-pressure
(urgency * (1-remaining)). We do not parse provider resetAt. Missing reset
remaining_ms => urgency 0 (remaining-only). OmniRoute uses 0.5 there; we do
not invent pressure. limit_reached sorts last. Tie-band rotation not ported.
"""

from __future__ import annotations

SESSION_MS = 5 * 60 * 60 * 1000
WEEKLY_MS = 7 * 24 * 60 * 60 * 1000
SESSION_REMAINING_W = 0.45
SESSION_PRESSURE_W = 0.55
WEEKLY_REMAINING_W = 0.25
WEEKLY_PRESSURE_W = 0.75
SESSION_WEIGHT = 0.35
WEEKLY_WEIGHT = 0.65
EXHAUSTION_GUARD = 0.10


def clamp01(value: float) -> float:
    if value <= 0:
        return 0.0
    if value >= 1:
        return 1.0
    return value


def reset_urgency(remaining_ms: float | None, window_ms: float) -> float:
    if remaining_ms is None:
        return 0.0
    if remaining_ms <= 0:
        return 1.0
    return clamp01(1.0 - remaining_ms / window_ms)


def score_reset_aware(
    *,
    session_remaining: float | None,
    weekly_remaining: float | None,
    limit_reached: bool = False,
    session_reset_ms: float | None = None,
    weekly_reset_ms: float | None = None,
) -> float:
    if limit_reached:
        return float("-inf")
    sess = 0.5 if session_remaining is None else clamp01(session_remaining)
    week = 0.5 if weekly_remaining is None else clamp01(weekly_remaining)
    s_press = reset_urgency(session_reset_ms, SESSION_MS) * (1 - sess)
    w_press = reset_urgency(weekly_reset_ms, WEEKLY_MS) * (1 - week)
    session_score = SESSION_REMAINING_W * sess + SESSION_PRESSURE_W * s_press
    weekly_score = WEEKLY_REMAINING_W * week + WEEKLY_PRESSURE_W * w_press
    score = SESSION_WEIGHT * session_score + WEEKLY_WEIGHT * weekly_score
    if sess < EXHAUSTION_GUARD:
        score *= max(0.05, sess / EXHAUSTION_GUARD)
    return score


def apply_reset_aware(
    keys: list[str],
    sat: dict[str, tuple[float | None, float | None, bool]],
) -> list[str]:
    if not keys:
        return []
    decorated = list(enumerate(keys))
    decorated.sort(
        key=lambda pair: (
            -score_reset_aware(
                session_remaining=sat.get(pair[1], (None, None, False))[0],
                weekly_remaining=sat.get(pair[1], (None, None, False))[1],
                limit_reached=sat.get(pair[1], (None, None, False))[2],
            ),
            pair[0],
        )
    )
    return [k for _, k in decorated]
