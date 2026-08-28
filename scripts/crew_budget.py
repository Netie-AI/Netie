"""Token budget for Crew runners. Over budget is FAILED, not a silent spend.

This is the cheap half of token-efficient Crew. OpenVault still meters keys.
Cortex still decides the tool. Crew just stops when the ticket's budget is gone.
"""

from __future__ import annotations

import json
import threading
from typing import Any


class BudgetDenied(PermissionError):
    """Job does not run. Ticket stays open."""


class TokenBudget:
    def __init__(self, max_tokens: int) -> None:
        if max_tokens < 1:
            raise ValueError("max_tokens must be >= 1")
        self.max_tokens = max_tokens
        self.spent = 0
        self._lock = threading.Lock()

    def remaining(self) -> int:
        with self._lock:
            return self.max_tokens - self.spent

    def charge(self, n: int) -> None:
        if n < 0:
            raise ValueError("charge must be >= 0")
        with self._lock:
            if self.spent + n > self.max_tokens:
                raise BudgetDenied(
                    f"budget {self.max_tokens} spent {self.spent} need {n}"
                )
            self.spent += n


def estimate_tokens(payload: dict[str, Any]) -> int:
    raw = json.dumps(payload, separators=(",", ":"), default=str)
    return max(1, (len(raw) + 3) // 4)
