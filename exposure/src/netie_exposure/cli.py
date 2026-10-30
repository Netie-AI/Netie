"""CLI: catalog, queue, growth, crew, approve. Social posting off by default."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

from netie_exposure.catalog import merge_catalog
from netie_exposure.channels import write_outbox
from netie_exposure.crew import summary as crew_summary
from netie_exposure.drafts import render_queue
from netie_exposure.growth import render as render_growth
from netie_exposure.growth import snapshot
from netie_exposure.post import MissingTokens, post_draft
from netie_exposure.refuse import ExposureRefusal, check_request
from netie_exposure.run import run_crew
from netie_exposure.tokens import init_env, load_env_file, social_ready, status as token_status

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTBOX = ROOT / "outbox"


def _followers() -> int | None:
    raw = os.environ.get("LINKEDIN_FOLLOWERS")
    if not raw:
        return None
    return int(raw)


def cmd_catalog(args: argparse.Namespace) -> int:
    catalog = merge_catalog(live=not args.offline)
    if args.json:
        json.dump(catalog, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0
    org = catalog["org"]
    print(f"{org['name']}  {org['github']}")
    print(org["description"])
    print(f"home: {org['home']}  hire: {org['hire']}")
    print(f"live_fetch: {catalog.get('live')}  github_stars_total: {catalog.get('github_stars_total')}")
    print("\nProducts")
    for p in catalog["products"]:
        stars = p.get("stargazers_count")
        star_s = f"  stars={stars}" if stars is not None else ""
        gh = p.get("github") or "-"
        print(f"- {p['name']}: {p['url']}  github={gh}{star_s}")
    print("\nHire")
    for o in catalog["hire_offers"]:
        print(f"- {o['name']}: {o['price']}  {o['url']}")
    return 0


def cmd_queue(args: argparse.Namespace) -> int:
    if args.request:
        check_request(args.request)
    catalog = merge_catalog(live=not args.offline)
    drafts = render_queue(catalog, day=args.day, n=args.n)
    outbox = Path(args.outbox)
    for draft in drafts:
        path = write_outbox(outbox, draft)
        print(f"{draft['id']}  {draft['kind']}/{draft['channel']}  {path}")
    row = snapshot(
        linkedin_followers=_followers(),
        github_stars_total=int(catalog.get("github_stars_total") or 0),
        drafts_written=len(drafts),
        target_linkedin=int(catalog["growth"]["linkedin_followers_target"]),
    )
    print("\n" + render_growth(row), end="")
    return 0


def cmd_growth(args: argparse.Namespace) -> int:
    catalog = merge_catalog(live=not args.offline)
    followers = args.followers if args.followers is not None else _followers()
    row = snapshot(
        linkedin_followers=followers,
        github_stars_total=int(catalog.get("github_stars_total") or 0),
        drafts_written=0,
        target_linkedin=int(catalog["growth"]["linkedin_followers_target"]),
    )
    print(render_growth(row), end="")
    return 0


def cmd_crew(_: argparse.Namespace) -> int:
    json.dump(crew_summary(), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    catalog = merge_catalog(live=False)
    drafts = {d["id"]: d for d in render_queue(catalog, day=args.day)}
    draft = drafts.get(args.id)
    if draft is None:
        md = Path(args.outbox) / f"{args.id}.md"
        if not md.is_file():
            print(f"unknown id {args.id}", file=sys.stderr)
            return 2
        print(f"approved file {md} (no live post: id not in today's queue)")
        return 0
    try:
        result = post_draft(draft, live=bool(args.live), approved_id=args.id)
    except MissingTokens as exc:
        print(str(exc), file=sys.stderr)
        return 4
    json.dump(result, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")
    return 0 if result.get("ok") else 5


def cmd_tokens(args: argparse.Namespace) -> int:
    if args.init:
        path = init_env()
        print(f"wrote {path} (gitignored). Paste official LinkedIn/Reddit tokens. I cannot mint them.")
    json.dump(token_status(), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def cmd_auto(args: argparse.Namespace) -> int:
    if args.request:
        check_request(args.request)
    granted = bool(args.grant_auto) or os.environ.get("EXPOSURE_AUTO_POST") == "1"
    if not granted:
        from netie_exposure.refuse import refuse

        refuse("publish_without_approve")
    result = run_crew(
        outbox=Path(args.outbox),
        live=not args.offline,
        day=args.day,
        followers=_followers(),
        rotate=getattr(args, "rotate", 0) or 0,
    )
    catalog = merge_catalog(live=False)
    drafts = render_queue(catalog, day=args.day)
    live = bool(args.live)
    if live and not social_ready():
        print(
            "missing_tokens: no official LinkedIn/Reddit tokens in env. "
            "See TOKENS.md. Chat grant is not OAuth.",
            file=sys.stderr,
        )
        json.dump({"run": result, "posted": [], "tokens": token_status()}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 4
    posted: list[dict] = []
    seen: set[str] = set()
    for draft in drafts:
        channel = draft.get("channel") or ""
        if channel not in ("linkedin", "reddit") or channel in seen:
            continue
        seen.add(channel)
        try:
            posted.append(post_draft(draft, live=live, approved_id=draft["id"]))
        except MissingTokens as exc:
            posted.append({"ok": False, "id": draft["id"], "error": str(exc)})
    json.dump({"run": result, "posted": posted, "live": live}, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    if args.request:
        check_request(args.request)
    result = run_crew(
        outbox=Path(args.outbox),
        live=not args.offline,
        day=args.day,
        followers=_followers(),
        rotate=getattr(args, "rotate", 0) or 0,
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def cmd_calendar(args: argparse.Namespace) -> int:
    if args.request:
        check_request(args.request)
    start = date.fromisoformat(args.day) if args.day else date.today()
    days: list[dict[str, object]] = []
    root = Path(args.outbox)
    for i in range(args.days):
        day = (start + timedelta(days=i)).isoformat()
        result = run_crew(
            outbox=root / day,
            live=not args.offline,
            day=day,
            followers=_followers(),
            rotate=i,
        )
        days.append({"day": day, "rotate": i, "ids": result["ids"], "drafts": result["drafts"]})
        print(f"{day}  rotate={i}  drafts={result['drafts']}", file=sys.stderr)
    json.dump(
        {
            "engine": "cortex",
            "social_posting": "off",
            "linkedin_target": 100000,
            "days": days,
            "note": "Organic campaign. One approved post per channel per day. Not a follower factory.",
        },
        sys.stdout,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0


def cmd_refuse_demo(args: argparse.Namespace) -> int:
    try:
        check_request(args.scenario)
    except ExposureRefusal as exc:
        print(str(exc))
        return 0
    print("no refusal matched")
    return 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="netie-exposure",
        description="Cortex-crew marketing pack. Drafts public posts. Refuses fake followers.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("catalog", help="print org + products + hire offers")
    c.add_argument("--offline", action="store_true", help="facts.json only, no GitHub/hire fetch")
    c.add_argument("--json", action="store_true")
    c.set_defaults(func=cmd_catalog)

    q = sub.add_parser("queue", help="write today's draft mix to the outbox")
    q.add_argument("--offline", action="store_true")
    q.add_argument("--day", help="YYYY-MM-DD (default: today)")
    q.add_argument("--n", type=int, default=6)
    q.add_argument("--outbox", default=str(DEFAULT_OUTBOX))
    q.add_argument("--request", help="optional user request to run through refusals")
    q.set_defaults(func=cmd_queue)

    g = sub.add_parser("growth", help="100k LinkedIn north star (measure, do not fake)")
    g.add_argument("--offline", action="store_true")
    g.add_argument("--followers", type=int, default=None)
    g.set_defaults(func=cmd_growth)

    r = sub.add_parser("crew", help="print Cortex-crew roles")
    r.set_defaults(func=cmd_crew)

    n = sub.add_parser("run", help="execute Vanguard -> Cortex -> channels -> Closer + marketing")
    n.add_argument("--offline", action="store_true")
    n.add_argument("--day", help="YYYY-MM-DD (default: today)")
    n.add_argument("--rotate", type=int, default=0, help="walk products/hire so days differ")
    n.add_argument("--outbox", default=str(DEFAULT_OUTBOX))
    n.add_argument("--request", help="optional user request to run through refusals")
    n.set_defaults(func=cmd_run)

    k = sub.add_parser("calendar", help="N-day organic campaign toward 100k (drafts only)")
    k.add_argument("--offline", action="store_true")
    k.add_argument("--day", help="start YYYY-MM-DD (default: today)")
    k.add_argument("--days", type=int, default=7)
    k.add_argument("--outbox", default=str(DEFAULT_OUTBOX))
    k.add_argument("--request", help="optional user request to run through refusals")
    k.set_defaults(func=cmd_calendar)

    a = sub.add_parser("approve", help="approve a draft id; --live posts via official APIs")
    a.add_argument("id")
    a.add_argument("--day")
    a.add_argument("--outbox", default=str(DEFAULT_OUTBOX))
    a.add_argument("--live", action="store_true", help="call LinkedIn/Reddit official APIs")
    a.set_defaults(func=cmd_approve)

    t = sub.add_parser("tokens", help="show which official tokens are present (no secret print)")
    t.add_argument("--init", action="store_true", help="write gitignored .env + local EXPOSURE_GATE")
    t.set_defaults(func=cmd_tokens)

    u = sub.add_parser("auto", help="run crew then post (official APIs only; needs tokens)")
    u.add_argument("--offline", action="store_true")
    u.add_argument("--day")
    u.add_argument("--rotate", type=int, default=0)
    u.add_argument("--outbox", default=str(DEFAULT_OUTBOX))
    u.add_argument("--request")
    u.add_argument("--grant-auto", action="store_true", help="human grant for this run")
    u.add_argument("--live", action="store_true", help="POST to LinkedIn/Reddit (needs tokens)")
    u.set_defaults(func=cmd_auto)

    x = sub.add_parser("refuse", help="show the refusal for a disallowed tactic")
    x.add_argument("scenario")
    x.set_defaults(func=cmd_refuse_demo)
    return p


def main(argv: list[str] | None = None) -> int:
    load_env_file()
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except ExposureRefusal as exc:
        print(str(exc), file=sys.stderr)
        return 3
    except MissingTokens as exc:
        print(str(exc), file=sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
