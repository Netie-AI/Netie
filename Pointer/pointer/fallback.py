"""Check OpenClaw / Hermes / Ollama. Do not install a third orchestrator."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any


def which_all() -> dict[str, str | None]:
    return {
        "ollama": shutil.which("ollama"),
        "openclaw": shutil.which("openclaw"),
        "hermes": shutil.which("hermes"),
        "xdotool": shutil.which("xdotool"),
        "ffmpeg": shutil.which("ffmpeg"),
    }


def product_pointer_paths() -> list[Path]:
    return [
        Path("D:/Pointer"),
        Path("/mnt/d/Pointer"),
        Path.home() / "Pointer",
    ]


def product_pointer_present() -> dict[str, Any]:
    hits = []
    for p in product_pointer_paths():
        hits.append({"path": str(p), "exists": p.is_dir()})
    return {
        "any": any(h["exists"] for h in hits),
        "paths": hits,
        "github": "Netie-AI/Pointer (private; this cloud token cannot clone it)",
    }


def report() -> dict[str, Any]:
    bins = which_all()
    product = product_pointer_present()
    return {
        "product_pointer": product,
        "binaries": bins,
        "fallback_policy": (
            "OpenClaw and Hermes are Ollama-launched personal assistants, not Pointer. "
            "NETIE.md forbids a third orchestrator. This daemon is the laptop-control path. "
            "Install OpenClaw/Hermes on the Windows laptop only if this daemon cannot run "
            "and only as a messaging assistant, never as a second Cortex."
        ),
        "install_if_missing": {
            "openclaw": "ollama launch openclaw",
            "hermes": "ollama launch hermes",
            "or_hermes_manual": "curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash",
        },
        "should_install_here": False,
        "reason": "This cloud VM is not the founder laptop; installing OpenClaw here would not control D:\\Pointer and would split the governance spine.",
    }
