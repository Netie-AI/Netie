"""FREE-token pool + register help. Not a 16th sort. Not OmniRoute vendored.

Uses the existing catalog. Never live quota fetch. Never invent keys.
Empty free pool is 503 with register_url rows, not a silent paid walk.
"""

from __future__ import annotations

from typing import Any

from freeroute_execution import ExecutionRefused, refuse_unported_analogue

FREE_TIERS = frozenset({"free", "freemium", "local"})
DROP_HELP = frozenset({"api_key", "key", "secret", "token", "authorization"})


class FreePoolRefused(ExecutionRefused):
    """No free hop. `.help` is catalog register rows, never secrets."""

    def __init__(self, message: str, help_rows: list[dict[str, str]] | None = None) -> None:
        super().__init__(503, message)
        self.help = help_rows or []


def _help_row(row: dict[str, Any]) -> dict[str, str]:
    return {
        "id": str(row.get("id") or ""),
        "register_url": str(row.get("register_url") or ""),
        "free_notes": str(row.get("free_notes") or ""),
    }


def assist_free_pool(
    catalog: list[dict[str, Any]] | None,
    *,
    allow_paid: bool = False,
    register: bool = False,
    parallel: Any = False,
    fetch_quota: Any = False,
    auto_combo: Any = False,
) -> dict[str, Any]:
    refuse_unported_analogue(
        parallel=parallel,
        fetch_quota=fetch_quota,
        auto_combo=auto_combo,
    )
    rows = [r for r in (catalog or []) if isinstance(r, dict) and r.get("id")]
    for row in rows:
        for bad in DROP_HELP:
            if bad in row:
                raise ExecutionRefused(400, "catalog leaked a secret field")
    pool = [
        {"id": str(r["id"]), "tier": str(r.get("tier") or "").lower()}
        for r in rows
        if str(r.get("tier") or "").lower() in FREE_TIERS
    ]
    if pool:
        out: dict[str, Any] = {"pool": pool, "used_paid": False}
        if register:
            out["register"] = [_help_row(r) for r in rows]
        return out
    if allow_paid:
        paid = [
            {"id": str(r["id"]), "tier": str(r.get("tier") or "paid").lower()}
            for r in rows
        ]
        if paid:
            return {"pool": paid, "used_paid": True}
    raise FreePoolRefused("no free hop", [_help_row(r) for r in rows])
