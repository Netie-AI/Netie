"""Load official channel tokens from env. Never mint LinkedIn/Reddit OAuth. Never print secrets."""

from __future__ import annotations

import os
import secrets
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ENV_EXAMPLE = ROOT / "env.example"
ENV_FILE = ROOT / ".env"

LINKEDIN_VARS = ("LINKEDIN_ACCESS_TOKEN",)
REDDIT_VARS = ("REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USERNAME", "REDDIT_PASSWORD")
GITHUB_VARS = ("GITHUB_TOKEN", "GH_TOKEN")


def load_env_file(path: Path | None = None) -> None:
    """Load gitignored .env without printing. Does not override real env."""
    dest = path or ENV_FILE
    if not dest.is_file():
        return
    for line in dest.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _present(names: tuple[str, ...]) -> bool:
    return all(bool(os.environ.get(n)) for n in names)


def github_token() -> str | None:
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or None


def status() -> dict[str, Any]:
    """Booleans only. Values never leave this function."""
    return {
        "linkedin": _present(LINKEDIN_VARS),
        "reddit": _present(REDDIT_VARS),
        "github": bool(github_token()),
        "auto_post": os.environ.get("EXPOSURE_AUTO_POST") == "1",
        "gate_set": bool(os.environ.get("EXPOSURE_GATE")),
        "note": (
            "Chat cannot grant LinkedIn or Reddit OAuth. Create apps at "
            "linkedin.com/developers/apps and reddit.com/prefs/apps, then put "
            "tokens in the environment or gitignored exposure/.env."
        ),
    }


def ready_to_post() -> list[str]:
    """Channel names that have official tokens (includes GitHub)."""
    s = status()
    return [name for name in ("linkedin", "reddit", "github") if s[name]]


def social_ready() -> list[str]:
    """LinkedIn/Reddit only. CI GITHUB_TOKEN does not count as social OAuth."""
    s = status()
    return [name for name in ("linkedin", "reddit") if s[name]]


def init_env(path: Path | None = None) -> Path:
    """Write gitignored .env skeleton plus a local gate secret. Not a LinkedIn token."""
    dest = path or ENV_FILE
    if dest.exists():
        return dest
    gate = secrets.token_urlsafe(32)
    dest.write_text(
        "# Gitignored. Official tokens only. This file is not a LinkedIn token mint.\n"
        f"EXPOSURE_GATE={gate}\n"
        "EXPOSURE_AUTO_POST=0\n"
        "LINKEDIN_ACCESS_TOKEN=\n"
        "REDDIT_CLIENT_ID=\n"
        "REDDIT_CLIENT_SECRET=\n"
        "REDDIT_USERNAME=\n"
        "REDDIT_PASSWORD=\n"
        "GITHUB_TOKEN=\n",
        encoding="utf-8",
        newline="\n",
    )
    os.environ.setdefault("EXPOSURE_GATE", gate)
    return dest
