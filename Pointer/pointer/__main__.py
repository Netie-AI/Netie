"""python -m pointer ..."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import fallback, server
from .executor import Executor, ExecutorError
from .pair import PairStore, write_card
from .prove import write_prove
from .server import _state_dir


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="pointer")
    sub = ap.add_subparsers(dest="cmd", required=True)
    serve = sub.add_parser("serve", help="run the localhost daemon")
    serve.add_argument("--bind", default=None)
    serve.add_argument("--port", type=int, default=None)
    sub.add_parser("verify", help="print stack status as JSON")
    live = sub.add_parser("live-click", help="move the mouse to prove control")
    live.add_argument("--x", type=int, default=200)
    live.add_argument("--y", type=int, default=200)
    sub.add_parser("prove", help="write .pointer-state/PROVE.json (no tokens)")
    pair = sub.add_parser("pair", help="print pair file path; --show dumps tokens locally")
    pair.add_argument("--show", action="store_true", help="print tokens to stdout (laptop only)")
    pair.add_argument("--card", action="store_true", help="write .pointer-state/PAIR_CARD.txt (gitignored)")
    pair.add_argument(
        "--rotate-approval",
        action="store_true",
        help="replace approval token after a local paste",
    )
    args = ap.parse_args(argv)

    if args.cmd == "serve":
        argv2: list[str] = []
        if args.bind:
            argv2 += ["--bind", args.bind]
        if args.port:
            argv2 += ["--port", str(args.port)]
        sys.argv = ["pointer.server", *argv2]
        return server.main()
    if args.cmd == "verify":
        print(json.dumps(fallback.report(), indent=2))
        return 0
    if args.cmd == "live-click":
        ex = Executor(display=None, screenshot_dir=_state_dir() / "shots")
        before = ex.mouse_location()
        moved = ex.move(args.x, args.y)
        after = ex.mouse_location()
        try:
            shot = str(ex.screenshot("live.png"))
        except ExecutorError as exc:
            shot = f"screenshot failed: {exc}"
        print(
            json.dumps(
                {"before": before, "moved": moved, "after": after, "screenshot": shot},
                indent=2,
            )
        )
        ok = after.get("x") == args.x and after.get("y") == args.y
        return 0 if ok else 1
    if args.cmd == "prove":
        import platform
        from datetime import datetime, timezone

        state = _state_dir()
        ex = Executor(display=None, screenshot_dir=state / "shots")
        before = ex.mouse_location()
        target_x, target_y = 220, 180
        if before.get("x") == target_x and before.get("y") == target_y:
            target_x, target_y = 400, 300
        moved = ex.move(target_x, target_y)
        after = ex.mouse_location()
        shot = None
        shot_error = None
        shot_bytes = 0
        try:
            shot = str(ex.screenshot("prove.png"))
            shot_bytes = Path(shot).stat().st_size
        except ExecutorError as exc:
            shot_error = str(exc)
        fb = fallback.report()
        payload = {
            "schema": "pointer.prove/v1",
            "when": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "mouse_before": before,
            "moved": moved,
            "mouse_after": after,
            "screenshot": shot,
            "screenshot_bytes": shot_bytes,
            "screenshot_error": shot_error,
            "ok": after.get("x") == target_x and after.get("y") == target_y,
            "openclaw": fb.get("binaries", {}).get("openclaw"),
            "hermes": fb.get("binaries", {}).get("hermes"),
        }
        path = write_prove(state, payload)
        print(json.dumps({"prove_file": str(path), "ok": payload["ok"]}, indent=2))
        return 0 if payload["ok"] else 1
    if args.cmd == "pair":
        path = _state_dir() / "pair.json"
        store = PairStore(path)
        if args.rotate_approval:
            store.rotate_approval()
        tokens = store.load()
        payload = {
            "pair_file": str(path),
            "has_pair_token": bool(tokens.get("pair_token")),
            "has_approval_token": bool(tokens.get("approval_token")),
            "rotated_approval": bool(args.rotate_approval),
        }
        if args.card:
            payload["card_file"] = str(write_card(_state_dir(), show_tokens=args.show))
        if args.show:
            payload["pair_token"] = tokens["pair_token"]
            payload["approval_token"] = tokens["approval_token"]
        print(json.dumps(payload, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
