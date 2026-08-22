"""Localhost Pointer HTTP API."""

from __future__ import annotations

import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from . import DEFAULT_BIND, DEFAULT_PORT
from .engine import Engine
from .fallback import report as fallback_report
from .pair import PairStore
from .protocol import SCHEMA, Intent


def _state_dir() -> Path:
    override = os.environ.get("POINTER_STATE_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[1] / ".pointer-state"


def pay_page_path() -> Path:
    return Path(__file__).resolve().parents[1] / "pay" / "index.html"


class PointerHandler(BaseHTTPRequestHandler):
    engine: Engine
    pair_token: str
    approval_token: str

    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def _json(self, code: int, payload: dict[str, Any]) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _html(self, code: int, body: bytes) -> None:
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _bearer(self) -> str | None:
        header = self.headers.get("Authorization") or ""
        if header.startswith("Bearer "):
            return header[len("Bearer ") :].strip()
        return self.headers.get("X-Pointer-Token")

    def _body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or "0")
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        if not raw:
            return {}
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid json: {exc}") from exc
        if not isinstance(data, dict):
            raise ValueError("body must be an object")
        return data

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in {"/health", "/healthz"}:
            self._json(200, {"ok": True, "schema": SCHEMA})
            return
        if path == "/v1/status":
            status = self.engine.status()
            status["fallback"] = fallback_report()
            self._json(200, status)
            return
        if path in {"/pay", "/pay/", "/pay/index.html"}:
            page = pay_page_path()
            if not page.is_file():
                self._json(500, {"ok": False, "reason": "pay page missing"})
                return
            self._html(200, page.read_bytes())
            return
        self._json(404, {"ok": False, "reason": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/v1/kill":
            self.engine.gate.arm_kill()
            digest = self.engine.ledger.append({"event": "kill", "source": "http"})
            self._json(200, {"ok": True, "killed": True, "ledger_hash": digest})
            return
        if path == "/v1/unkill":
            if self._bearer() != self.pair_token:
                self._json(403, {"ok": False, "reason": "pair token required to clear kill switch"})
                return
            self.engine.gate.clear_kill()
            digest = self.engine.ledger.append({"event": "unkill", "source": "http"})
            self._json(200, {"ok": True, "killed": False, "ledger_hash": digest})
            return
        if path == "/v1/intent":
            try:
                body = self._body()
                intent = Intent.from_dict(body)
            except ValueError as exc:
                self._json(400, {"ok": False, "reason": str(exc)})
                return
            resp = self.engine.handle(intent, bearer=self._bearer())
            code = 200 if resp.verdict == "executed" else 409 if resp.verdict == "needs_approval" else 403
            self._json(code, resp.to_dict())
            return
        self._json(404, {"ok": False, "reason": "not found"})


def serve(bind: str = DEFAULT_BIND, port: int = DEFAULT_PORT) -> None:
    state = _state_dir()
    store = PairStore(state / "pair.json")
    tokens = store.load()
    bind_is_loopback = bind in {"127.0.0.1", "localhost", "::1"}
    engine = Engine(
        state_dir=state,
        pair_token=tokens["pair_token"],
        approval_token=tokens["approval_token"],
        bind_is_loopback=bind_is_loopback,
    )
    PointerHandler.engine = engine
    PointerHandler.pair_token = tokens["pair_token"]
    PointerHandler.approval_token = tokens["approval_token"]
    httpd = ThreadingHTTPServer((bind, port), PointerHandler)
    print(f"pointer listening on http://{bind}:{port}", flush=True)
    print(f"pair token file: {state / 'pair.json'}", flush=True)
    print("kill switch: POST /v1/kill", flush=True)
    httpd.serve_forever()


def main() -> int:
    ap = argparse.ArgumentParser(description="Pointer laptop-control daemon")
    ap.add_argument("--bind", default=os.environ.get("POINTER_BIND", DEFAULT_BIND))
    ap.add_argument("--port", type=int, default=int(os.environ.get("POINTER_PORT", DEFAULT_PORT)))
    args = ap.parse_args()
    if args.bind not in {"127.0.0.1", "localhost", "::1"}:
        if os.environ.get("POINTER_ALLOW_REMOTE") != "1":
            raise SystemExit(
                "refusing non-loopback bind; set POINTER_ALLOW_REMOTE=1 if you really mean it"
            )
    serve(args.bind, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
