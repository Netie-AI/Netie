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


def run_unit() -> unittest.TestResult:
    loader = unittest.TestLoader()
    suite = loader.discover(str(ROOT / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return result


def live_mouse() -> dict:
    from pointer.executor import Executor, ExecutorError

    ex = Executor(display=os.environ.get("DISPLAY"), screenshot_dir=ROOT / ".pointer-state" / "shots")
    before = ex.mouse_location()
    target_x = 220 if before.get("x") != 220 else 400
    target_y = 180 if before.get("y") != 180 else 300
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


def daemon_health() -> dict:
    import json
    import urllib.error
    import urllib.request

    url = os.environ.get("POINTER_URL", "http://127.0.0.1:7420") + "/health"
    pay_url = os.environ.get("POINTER_URL", "http://127.0.0.1:7420") + "/pay"
    qr_url = os.environ.get("POINTER_URL", "http://127.0.0.1:7420") + "/pay/pointer-rm300.png"
    root_url = os.environ.get("POINTER_URL", "http://127.0.0.1:7420") + "/"
    out: dict = {"url": url, "pay_url": pay_url, "qr_url": qr_url, "root_url": root_url}
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            out["ok"] = resp.status == 200
            out["body"] = body
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        out["ok"] = False
        out["error"] = str(exc)
        return out
    try:
        with urllib.request.urlopen(pay_url, timeout=2) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            out["pay_ok"] = resp.status == 200 and "buy.stripe.com" in html and "pointer-rm300.png" in html
            out["pay_bytes"] = len(html)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        out["pay_ok"] = False
        out["pay_error"] = str(exc)
    try:
        with urllib.request.urlopen(qr_url, timeout=2) as resp:
            raw = resp.read()
            out["qr_ok"] = resp.status == 200 and raw.startswith(b"\x89PNG")
            out["qr_bytes"] = len(raw)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        out["qr_ok"] = False
        out["qr_error"] = str(exc)
    try:
        with urllib.request.urlopen(root_url, timeout=2) as resp:
            root = resp.read().decode("utf-8", errors="replace")
            out["root_ok"] = (
                resp.status == 200
                and "pointer prove" in root
                and "POINTER_ALLOW_REMOTE" in root
                and "pair_token:" not in root
            )
            out["root_bytes"] = len(root)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        out["root_ok"] = False
        out["root_error"] = str(exc)
    return out


def live_intent() -> dict:
    import json
    import urllib.error
    import urllib.request
    from pointer.protocol import SCHEMA

    base = os.environ.get("POINTER_URL", "http://127.0.0.1:7420")
    pair = ROOT / ".pointer-state" / "pair.json"
    if not pair.is_file():
        return {"ok": False, "error": "pair.json missing; start the daemon once"}
    tokens = json.loads(pair.read_text(encoding="utf-8"))
    marker = "pointer-verify-act"
    payload = {
        "schema": SCHEMA,
        "intent_id": "verify-act-1",
        "source": "local-test",
        "goal": "sandbox write to prove gated act",
        "approval_token": tokens.get("approval_token"),
        "actions": [{"type": "file_write", "path": "verify-tick.txt", "content": marker}],
    }
    req = urllib.request.Request(
        base + "/v1/intent",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            code = resp.status
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {"raw": raw}
        code = exc.code
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        return {"ok": False, "error": str(exc)}
    dest = ROOT / ".pointer-state" / "sandbox" / "verify-tick.txt"
    written = dest.is_file() and dest.read_text(encoding="utf-8") == marker
    return {
        "ok": code == 200 and body.get("verdict") == "executed" and written,
        "http": code,
        "verdict": body.get("verdict"),
        "reason": body.get("reason"),
        "degraded": body.get("degraded"),
        "sandbox_written": written,
    }


def hackathon_live() -> dict:
    import threading
    import urllib.error
    import urllib.request
    from http.server import ThreadingHTTPServer

    from hackathon.app import Handler
    from pointer.gemini_planner import gemini_configured

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{port}/health"
    out: dict = {"url": url}
    try:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                raw = resp.read()
                code = resp.status
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            code = exc.code
        body = json.loads(raw.decode("utf-8"))
        out["http"] = code
        out["body"] = body
        if gemini_configured():
            out["ok"] = code == 200 and body.get("ok") is True
        else:
            out["ok"] = (
                code == 503
                and body.get("ok") is False
                and "missing_gemini_key" in (body.get("degraded") or [])
            )
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        out["ok"] = False
        out["error"] = str(exc)
    finally:
        httpd.shutdown()
        httpd.server_close()
    return out


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
    daemon = daemon_health()
    intent = live_intent() if daemon.get("ok") else {"ok": False, "skipped": True, "reason": "daemon down"}
    hack = hackathon_live()
    payload = {
        "unit_tests": {
            "run": unit.testsRun,
            "failures": len(unit.failures),
            "errors": len(unit.errors),
            "ok": unit.wasSuccessful(),
        },
        "live_mouse": live,
        "live_error": live_error,
        "daemon": daemon,
        "live_intent": intent,
        "hackathon_live": hack,
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
    if daemon.get("ok") and not intent.get("ok"):
        return 1
    if daemon.get("ok") and not daemon.get("pay_ok"):
        return 1
    if daemon.get("ok") and not daemon.get("qr_ok"):
        return 1
    if daemon.get("ok") and not daemon.get("root_ok"):
        return 1
    if not hack.get("ok"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
