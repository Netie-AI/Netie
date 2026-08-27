"""cache-optimized: rendezvous-hash the same prompt key onto one target.

OmniRoute uses explicit prompt_cache_key or a prefix analyzer, then SHA-256
rendezvous of (key, connection-or-execution identity). We do not vendor the
prefix analyzer. Caller supplies cache_key. Empty key leaves order. OAuth
session occupancy is not ported (availability=1).
"""

from __future__ import annotations

import hashlib

MAX_HIGH = (1 << 64) - 1


def target_identity(execution_key: str, connection_id: str | None = None) -> str:
    conn = (connection_id or "").strip()
    if conn:
        return f"connection:{conn}"
    return f"execution:{execution_key}"


def rendezvous_score(cache_key: str, identity: str) -> float:
    digest = hashlib.sha256()
    digest.update(cache_key.encode("utf-8"))
    digest.update(b"\0")
    digest.update(identity.encode("utf-8"))
    high = int.from_bytes(digest.digest()[:16], "big") >> 64
    return high / MAX_HIGH


def apply_cache_optimized(
    keys: list[str],
    cache_key: str | None,
    *,
    connections: dict[str, str] | None = None,
) -> list[str]:
    if not keys:
        return []
    key = (cache_key or "").strip()
    if not key:
        return list(keys)
    conns = connections or {}
    decorated = list(enumerate(keys))
    decorated.sort(
        key=lambda pair: (
            -rendezvous_score(key, target_identity(pair[1], conns.get(pair[1]))),
            pair[0],
        )
    )
    return [k for _, k in decorated]
