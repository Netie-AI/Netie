"""python -m pointer ..."""

from __future__ import annotations

import argparse
import json
import sys

from . import fallback, server
from .executor import Executor, ExecutorError


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
        ex = Executor(display=None, screenshot_dir=__import__("pathlib").Path("/tmp/pointer-live"))
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
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
