"""FreeBuild honesty. Never report a live URL you did not observe.

From OpenVault docs/SHIPPING_MODEL.md: wrangler output is parsed, never
constructed. simulated is a loud fail, not a Deploy-button success.
HT1 is a live openable URL under the leave-machine gate. This repo cannot
run HT1; it can refuse to fake it.
"""

from __future__ import annotations

import re

URL_RE = re.compile(r"https://[^\s]+")


class ShipDenied(PermissionError):
    """Not live. Do not show a green Deploy."""


def parse_observed_url(tool_output: str, *, exit_code: int) -> str:
    if exit_code != 0:
        raise ShipDenied("provider exited non-zero")
    found = URL_RE.findall(tool_output or "")
    if not found:
        raise ShipDenied("zero exit with no URL")
    return found[0]


def report_deploy(
    *,
    simulated: bool,
    observed_url: str | None,
    constructed_url: str | None,
) -> dict[str, str]:
    if constructed_url:
        raise ShipDenied("URL must be parsed, never constructed")
    if simulated:
        raise ShipDenied("simulated is not HT1")
    if not observed_url:
        raise ShipDenied("no observed URL")
    return {"status": "LIVE", "url": observed_url, "ht1": "observed"}
