"""Organic growth tracker. Measures. Does not manufacture."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def snapshot(
    *,
    linkedin_followers: int | None,
    github_stars_total: int,
    drafts_written: int,
    target_linkedin: int = 100_000,
) -> dict[str, Any]:
    remaining = None if linkedin_followers is None else max(0, target_linkedin - linkedin_followers)
    return {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "linkedin_followers": linkedin_followers,
        "linkedin_target": target_linkedin,
        "linkedin_remaining": remaining,
        "github_stars_total": github_stars_total,
        "drafts_written": drafts_written,
        "organic_only": True,
        "note": (
            "100k is a north star. This pack drafts public posts. "
            "It does not buy or fake followers."
        ),
    }


def append_snapshot(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")


def render(row: dict[str, Any]) -> str:
    current = row["linkedin_followers"]
    current_s = "unknown (set LINKEDIN_FOLLOWERS or pass --followers)" if current is None else str(current)
    remaining = row["linkedin_remaining"]
    remaining_s = "unknown" if remaining is None else str(remaining)
    return (
        f"linkedin: {current_s} / {row['linkedin_target']}  remaining {remaining_s}\n"
        f"github stars (public catalog): {row['github_stars_total']}\n"
        f"drafts this run: {row['drafts_written']}\n"
        f"organic_only: {row['organic_only']}\n"
        f"{row['note']}\n"
    )
