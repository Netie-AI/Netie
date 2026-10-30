#!/usr/bin/env python3
"""Estate docs gate. Same checks as .github/workflows/docs-ci.yml.

Run from the Netie repo root:

    python3 scripts/check_docs.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "NETIE.md",
    "STATUS.md",
    "Internal/Agents/AGENT_SYSTEM.md",
    "Internal/Rules/DOCUMENT_SYSTEM.md",
    "Internal/Workflow/OPERATING_MODEL.md",
    "TAS/TAS-CORTEX.md",
    "TAS/TAS-DMS.md",
    "TAS/TAS-SPACE.md",
    "TAS/TAS-CREW.md",
    "TAS/TAS-OPENVAULT.md",
    "TAS/TAS-AIRGPT.md",
    "TAS/TAS-POINTER.md",
    "TAS/TAS-CONTROL.md",
    "TAS/TAS-CONSTRUCTOR.md",
    "TAS/ESTATE-GAP.md",
    "White Paper - Why/WP-001-accountable-ai-operating-system.md",
    "docs/decisions/DR-0001-one-decision-layer.md",
    "docs/ACCESS.md",
    "Software Blueprint/Crew/PRD-002-operator-factory.md",
    "pyproject.toml",
]

ASCII_ROOTS = [
    "NETIE.md",
    "STATUS.md",
    "Internal",
    "TAS",
    "White Paper - Why",
    "docs",
    "Software Blueprint",
]

FORBIDDEN = {
    "\u2014": "em dash",
    "\u2013": "en dash",
    "\u2018": "curly quote",
    "\u2019": "curly quote",
    "\u201c": "curly quote",
    "\u201d": "curly quote",
}


def main() -> int:
    fails: list[str] = []
    for rel in REQUIRED:
        path = ROOT / rel
        if not path.is_file():
            fails.append(f"missing {rel}")

    for root in ASCII_ROOTS:
        base = ROOT / root
        files = [base] if base.is_file() else sorted(base.rglob("*.md"))
        for path in files:
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            for i, line in enumerate(text.splitlines(), 1):
                for ch, name in FORBIDDEN.items():
                    if ch in line:
                        rel = path.relative_to(ROOT)
                        fails.append(f"laptop-ASCII {rel}:{i} {name}")

    if fails:
        print("FAIL")
        for row in fails:
            print(row)
        return 1
    tests = sorted((ROOT / "scripts").glob("test_*.py"))
    if not tests:
        fails.append("no scripts/test_*.py")
    for wrap in tests:
        proc = subprocess.run(
            [sys.executable, str(wrap)],
            cwd=str(ROOT / "scripts"),
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            fails.append(f"{wrap.name} failed")
            fails.append(proc.stderr or proc.stdout)

    if fails:
        print("FAIL")
        for row in fails:
            print(row)
        return 1
    print(
        f"ok {len(REQUIRED)} files, laptop-ASCII clean, {len(tests)} script tests passed"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
