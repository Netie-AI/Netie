#!/usr/bin/env python3
"""Verify Pointer on this machine: unit tests, live mouse, fallback binaries."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
PKG_PARENT = ROOT
if str(PKG_PARENT) not in sys.path:
    sys.path.insert(0, str(PKG_PARENT))

# tests/ lives under Pointer/; package is Pointer/pointer
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def run_unit() -> unittest.TestResult:
    loader = unittest.TestLoader()
    suite = loader.discover(str(ROOT / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return result


def live_mouse() -> dict:
    from pointer.executor import Executor, ExecutorError

    ex = Executor(display=os.environ.get("DISPLAY"), screenshot_dir=ROOT / ".pointer-state" / "shots")
    before = ex.mouse_location()
    target_x, target_y = 220, 180
    moved = ex.move(target_x, target_y)
    after = ex.mouse_location()
    shot = None
    shot_error = None
    try:
        shot = str(ex.screenshot("verify-live.png"))
        size = Path(shot).stat().st_size
    except ExecutorError as exc:
        shot_error = str(exc)
        size = 0
    ok = after.get("x") == target_x and after.get("y") == target_y
    return {
        "ok": ok,
        "before": before,
        "moved": moved,
        "after": after,
        "screenshot": shot,
        "screenshot_bytes": size,
        "screenshot_error": shot_error,
        "display": os.environ.get("DISPLAY"),
    }


def main() -> int:
    from pointer.fallback import report

    os.chdir(ROOT)
    unit = run_unit()
    live = None
    live_error = None
    if os.environ.get("DISPLAY") and os.environ.get("POINTER_SKIP_LIVE") != "1":
        try:
            live = live_mouse()
        except Exception as exc:  # noqa: BLE001 - verify must never crash silent
            live_error = f"{type(exc).__name__}: {exc}"
    payload = {
        "unit_tests": {
            "run": unit.testsRun,
            "failures": len(unit.failures),
            "errors": len(unit.errors),
            "ok": unit.wasSuccessful(),
        },
        "live_mouse": live,
        "live_error": live_error,
        "fallback": report(),
        "git": subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT.parent, text=True).strip(),
    }
    print(json.dumps(payload, indent=2))
    if not unit.wasSuccessful():
        return 1
    if live is not None and not live.get("ok"):
        return 1
    if live_error:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
