"""Cloud Run / local HTTP wrapper around gemini_planner. Loopback Pointer stays separate."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from pointer.gemini_planner import PlannerError, gemini_configured, plan


def health() -> dict:
    ok = gemini_configured()
    return {
        "ok": ok,
        "schema": "pointer.intent/v1",
        "degraded": [] if ok else ["missing_gemini_key"],
        "gcp": "cloud-run" if os.environ.get("K_SERVICE") else "local",
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:  # noqa: A003
        return

    def _json(self, code: int, payload: dict) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        if self.path.split("?", 1)[0] in {"/health", "/"}:
            body = health()
            self._json(200 if body["ok"] else 503, body)
            return
        self._json(404, {"ok": False, "reason": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path.split("?", 1)[0] != "/plan":
            self._json(404, {"ok": False, "reason": "not found"})
            return
        n = int(self.headers.get("Content-Length") or "0")
        try:
            body = json.loads(self.rfile.read(n).decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._json(400, {"ok": False, "reason": "bad json"})
            return
        goal = str(body.get("goal") or "")
        try:
            intent = plan(goal)
        except PlannerError as exc:
            self._json(503, {"ok": False, "reason": str(exc)})
            return
        self._json(200, intent)


def main() -> None:
    bind = os.environ.get("BIND", "0.0.0.0" if os.environ.get("K_SERVICE") else "127.0.0.1")
    port = int(os.environ.get("PORT", "8080"))
    ThreadingHTTPServer((bind, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
