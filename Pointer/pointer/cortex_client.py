"""Cortex is the brain. Pointer only pings it; it does not plan."""

from __future__ import annotations

import json
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


def submit_intent(payload: dict, timeout: float = 5.0) -> dict | None:
    """POST the intent to Cortex if a plan endpoint exists. None = not reachable."""
    url = cortex_base() + "/api/engine/auto"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError):
        return None
