"""lkgp: last-known-good target first. Algorithm port, not OmniRoute localDb.

OmniRoute looks up provider+connection in SQLite (`getLKGP`). FreeRoute has
execution_key metrics only. We sticky the last *successful* key.

A later failure of that same key clears the pin (OmniRoute `clearLKGP` after
a live incident where a timed-out target stayed first). Missing last-success
leaves order unchanged. This is not highest-success-rate routing.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LkgpState:
    last_success_key: str | None = None

    def record(self, key: str, *, success: bool) -> None:
        if not key:
            return
        if success:
            self.last_success_key = key
        elif self.last_success_key == key:
            self.last_success_key = None


def apply_lkgp(keys: list[str], last_success: str | None) -> list[str]:
    if not keys:
        return []
    if last_success and last_success in keys:
        rest = [k for k in keys if k != last_success]
        return [last_success, *rest]
    return list(keys)
