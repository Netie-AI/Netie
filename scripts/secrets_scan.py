#!/usr/bin/env python3
"""Fail if tracked files look like live provider keys.

python3 scripts/secrets_scan.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_TRACKED = frozenset({"env.local", "key.md", "keys.txt"})

# Production OpenRouter keys are sk-or-v1- plus 64 hex. Short fixtures stay.
OPENROUTER_LIVE = re.compile(r"sk-or-v1-[a-fA-F0-9]{64}")
CEREBRAS_LIVE = re.compile(r"csk-[a-z0-9]{32,}")
GITHUB_PAT = re.compile(r"github_pat_[A-Za-z0-9_]{20,}")
GITHUB_CLASSIC = re.compile(r"ghp_[A-Za-z0-9]{20,}")
ANTHROPIC_LIVE = re.compile(r"sk-ant-(?!test-)[A-Za-z0-9\-_]{16,}")

SKIP_DIRS = frozenset({".git", ".venv", "__pycache__", "node_modules", ".pytest_cache"})
TEXT_SUFFIX = frozenset(
    {
        ".md",
        ".txt",
        ".py",
        ".json",
        ".yml",
        ".yaml",
        ".toml",
        ".sh",
        ".ps1",
        ".env",
        ".csv",
        ".patch",
        ".xml",
        ".html",
        ".js",
        ".ts",
        ".tsx",
        ".cs",
        ".go",
        ".rs",
        ".cfg",
        ".ini",
        ".example",
    }
)


def _is_text(path: Path) -> bool:
    if path.suffix.lower() in TEXT_SUFFIX:
        return True
    return path.name.lower() in {"makefile", "dockerfile", "gitignore"}


def iter_tracked(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        files.append(path)
    return files


def findings(root: Path) -> list[str]:
    out: list[str] = []
    for path in iter_tracked(root):
        rel = path.relative_to(root).as_posix()
        if path.name.lower() in FORBIDDEN_TRACKED:
            out.append(f"forbidden tracked secrets file {rel}")
            continue
        if not _is_text(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        checks = (
            ("OpenRouter live key", OPENROUTER_LIVE),
            ("Cerebras live key", CEREBRAS_LIVE),
            ("GitHub PAT", GITHUB_PAT),
            ("GitHub classic token", GITHUB_CLASSIC),
            ("Anthropic live key", ANTHROPIC_LIVE),
        )
        for label, pat in checks:
            if pat.search(text):
                out.append(f"{label} in {rel}")
    return out


def main() -> int:
    rows = findings(ROOT)
    if rows:
        print("FAIL")
        for row in rows:
            print(row)
        return 1
    print("ok secrets scan clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
