"""Cortex is the brain. Pointer only pings it; it does not plan.

Default CORTEX_URL is TAS-CORTEX :8010. Cloneable OpenVault mesh uses :8000.
Do not remap ports here. See pointer.mesh.report().
"""

from __future__ import annotations

import os
import urllib.error
import urllib.request


def cortex_base() -> str:
    return os.environ.get("CORTEX_URL", "http://127.0.0.1:8010").rstrip("/")


def ping(timeout: float = 1.5) -> bool:
    url = cortex_base() + "/health"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return 200 <= resp.status < 300
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        alt = cortex_base() + "/healthz"
        try:
            with urllib.request.urlopen(alt, timeout=timeout) as resp:
                return 200 <= resp.status < 300
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            return False


# TAS-CORTEX.md section 5: POST /api/engine/auto is race_router.auto_route
# (family cosine + stored winner). It does not ingest pointer.intent/v1.
# Cortex reaches this daemon via Pointer POST /v1/intent. Do not POST intents
# the other way.
CORTEX_AUTO_INGESTS_POINTER_INTENT = False


def submit_intent(payload: dict, timeout: float = 5.0) -> dict | None:
    """Refuse to POST pointer.intent to Cortex /api/engine/auto.

    Returning None is the fail-closed miss (unreachable / wrong contract), not a
    silent plan. timeout is accepted for call-site compatibility and unused.
    """
    del payload, timeout
    return None
