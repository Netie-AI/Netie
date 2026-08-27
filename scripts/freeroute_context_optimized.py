"""context-optimized: largest known context window first.

OmniRoute uses a model catalog (`getModelContextLimitForModelString`). FreeRoute
does not vendor that catalog. Callers set `context_window` on the target.
If no target has a window, order is unchanged (same fail-open as OmniRoute).
Unknown windows sort last. This is not cache-affinity and not context-relay.
"""

from __future__ import annotations


def apply_context_optimized(
    keys: list[str], windows: dict[str, float | None]
) -> list[str]:
    if not keys:
        return []
    if not any(windows.get(k) is not None for k in keys):
        return list(keys)
    decorated = list(enumerate(keys))
    decorated.sort(
        key=lambda pair: (
            windows.get(pair[1]) is None,
            -(windows.get(pair[1]) or 0),
            pair[0],
        )
    )
    return [k for _, k in decorated]
