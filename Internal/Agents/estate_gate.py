"""Estate fleet gate -- readable, comparable, adversarial.

Does NOT sync Plane (vacuous if it minted the view it checks).
Does NOT treat MERGEABLE as merge permission.
Does NOT treat 4 green checks + 1 red floor as green.

Usage:
  python estate_gate.py attack   # offline fixtures, no network
  python estate_gate.py snapshot # live gh + Plane + docs -> snapshots/
  python estate_gate.py check    # snapshot then score live invariants
  python estate_gate.py all      # attack then check
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NETIE = HERE.parent.parent
SNAP = HERE / "snapshots"
FLEET = HERE / "FLEET.md"
AGENT = HERE / "AGENT_SYSTEM.md"
RUNTIME = HERE / "RUNTIME.md"
TR = Path.home() / ".claude" / "agents" / "ticket-runner.md"
PRD = Path.home() / ".claude" / "agents" / "prd-agent.md"
EPIC = Path.home() / ".claude" / "agents" / "epic-agent.md"
GUACA = Path(r"D:\Cortex\guaca")
RAKAZO = Path(r"D:\Cortex\rakazo")
PLANE_KEY = Path(r"D:\plane-selfhost\plane-app\api-key.local")
PLANE_BASE = "http://localhost:8099/api/v1"

REPOS = [
    "Netie-AI/Cortex",
    "Netie-AI/dms",
    "Netie-AI/OpenVault",
    "jian-hong/AirGPT",
    "Netie-AI/Pointer",
    "Netie-AI/Space",
]
NAMED_HOLDS = ("Netie-AI/dms#61",)
FROZEN_HEADS = {
    "Netie-AI/Cortex#4": "chore/unblock-ci-and-estate-audit",
    "Netie-AI/Cortex#41": "worktree-dms-59-sqlgate-violations",
    "Netie-AI/Cortex#43": "cursor/warehouse-path-4abf",
    "Netie-AI/Cortex#44": "cursor/sec01-dms-query-manifest-37b6",
    "Netie-AI/dms#61": "cursor/ff-02-polarity-guard-8821",
}
UNSEAT_NO_WRITE = {
    "Netie-AI/Cortex#2",
    "Netie-AI/Cortex#3",
    "Netie-AI/Cortex#4",
    "Netie-AI/Cortex#41",
    "Netie-AI/Cortex#43",
    "Netie-AI/Cortex#44",
}
IN_FLIGHT_FLOOR = ("Netie-AI/Cortex#45", "lint-type-test")
TICKET_KEY = re.compile(
    r"(FF-\d+|CSV-01|SEC-01|SPACE-01|ANS-\d+|META-01|VQ-\d+|D02|HOST-DEMO-\d+|S4:)",
    re.I,
)


def gh_json(args: list[str]):
    raw = subprocess.check_output(["gh", *args], text=True)
    return json.loads(raw)


def file_sha(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def probe_get(url: str, timeout: float = 2.0) -> str:
    """Display-only. Never starts the target process."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return f"up {resp.status}"
    except Exception:
        return "DOWN"


def ticket_key(title: str, head: str = "") -> str | None:
    blob = f"{title} {head}"
    m = TICKET_KEY.search(blob or "")
    if m:
        return m.group(1).upper()
    h = (head or "").lower()
    if "ff-02" in h or "ff02" in h or "ff-02" in (title or "").lower():
        return "FF-02"
    return None


def plane_items(key: str) -> list[dict]:
    out: list[dict] = []
    r = urllib.request.Request(
        f"{PLANE_BASE}/workspaces/netie/projects/",
        headers={"X-API-Key": key},
    )
    with urllib.request.urlopen(r, timeout=20) as resp:
        projs = json.loads(resp.read()).get("results") or []
    for p in projs:
        path = f"/workspaces/netie/projects/{p['id']}/work-items/"
        while path:
            req = urllib.request.Request(
                f"{PLANE_BASE}{path}",
                headers={"X-API-Key": key},
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                blob = json.loads(resp.read())
            rows = blob if isinstance(blob, list) else blob.get("results") or []
            for it in rows:
                name = str(it.get("name") or "")
                if name.startswith("[DONE]"):
                    continue
                if it.get("external_source") == "github" and it.get("external_id"):
                    out.append(
                        {
                            "external_id": it["external_id"],
                            "name": name,
                            "project": p.get("identifier"),
                        }
                    )
            nxt = blob.get("next_cursor") if isinstance(blob, dict) else None
            if not nxt or not blob.get("next_page_results"):
                break
            path = f"/workspaces/netie/projects/{p['id']}/work-items/?cursor={nxt}"
    return out


def live_snapshot() -> dict:
    prs = []
    for repo in REPOS:
        rows = gh_json(
            [
                "pr",
                "list",
                "--repo",
                repo,
                "--state",
                "open",
                "--limit",
                "30",
                "--json",
                "number,title,headRefName,baseRefName,mergeable,url",
            ]
        )
        for pr in rows:
            prs.append(
                {
                    "id": f"{repo}#{pr['number']}",
                    "repo": repo,
                    "number": pr["number"],
                    "title": pr["title"],
                    "head": pr["headRefName"],
                    "base": pr["baseRefName"],
                    "mergeable": pr.get("mergeable"),
                    "key": ticket_key(pr["title"], pr["headRefName"]),
                }
            )
    # A demo/* branch merged to main is a hard violation (AGENT_SYSTEM.md section 7),
    # and it can only be seen in the MERGED list - the open list cannot contain it by
    # construction, which is why the previous check could never fire. Left as None on
    # error so the checker reports NOT_EVALUATED rather than a silent pass.
    demo_merged_to_main: list[dict] | None = None
    try:
        demo_merged_to_main = []
        for repo in REPOS:
            merged = gh_json(
                [
                    "pr",
                    "list",
                    "--repo",
                    repo,
                    "--state",
                    "merged",
                    "--base",
                    "main",
                    "--limit",
                    "100",
                    "--json",
                    "number,headRefName",
                ]
            )
            for m in merged or []:
                if str(m.get("headRefName", "")).startswith("demo/"):
                    demo_merged_to_main.append(
                        {"id": f"{repo}#{m.get('number')}", "head": m.get("headRefName")}
                    )
    except subprocess.CalledProcessError:
        demo_merged_to_main = None

    floors = {}
    try:
        c45 = gh_json(
            [
                "pr",
                "view",
                "45",
                "--repo",
                "Netie-AI/Cortex",
                "--json",
                "state,statusCheckRollup,headRefName",
            ]
        )
        floors["Netie-AI/Cortex#45"] = {
            "state": c45.get("state"),
            "head": c45.get("headRefName"),
            "checks": [
                {"name": x.get("name"), "conclusion": x.get("conclusion")}
                for x in (c45.get("statusCheckRollup") or [])
            ],
        }
    except subprocess.CalledProcessError as e:
        floors["Netie-AI/Cortex#45"] = {"error": str(e)}
    try:
        a42 = gh_json(["issue", "view", "42", "--repo", "jian-hong/AirGPT", "--json", "state,title"])
        air42 = {"state": a42.get("state"), "title": a42.get("title")}
    except subprocess.CalledProcessError as e:
        air42 = {"error": str(e)}
    plane = []
    plane_err = None
    if PLANE_KEY.exists():
        try:
            plane = plane_items(PLANE_KEY.read_text(encoding="utf-8").strip())
        except urllib.error.HTTPError as e:
            plane_err = f"HTTP {e.code}"
        except OSError as e:
            plane_err = str(e)
    else:
        plane_err = "missing api-key.local"
    nc = probe_get("http://localhost:3100/api/health")
    snap = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "docs": {
            "FLEET.md": file_sha(FLEET),
            "AGENT_SYSTEM.md": file_sha(AGENT),
            "ticket-runner.md": file_sha(TR),
            "prd-agent.md": file_sha(PRD),
            "epic-agent.md": file_sha(EPIC),
            "RUNTIME.md": file_sha(RUNTIME),
        },
        "prs": prs,
        "demo_merged_to_main": demo_merged_to_main,
        "floors": floors,
        "airgpt_42": air42,
        "plane": plane,
        "plane_err": plane_err,
        "shells": {
            "plane": "up" if not plane_err else f"DOWN {plane_err}",
            "netie_control": nc,
            "netie_control_note": "GET-only. GATED. Do not boot Paperclip to dodge a Grok cap.",
            "prd_agent": "deployed" if PRD.exists() else "MISSING",
            "epic_agent": "deployed" if EPIC.exists() else "MISSING",
            "ticket_runner": "deployed" if TR.exists() else "MISSING",
            "gating": "estate_gate.py (this snapshot)",
            "pr_bot": "FLEET.md + BRANCH_HOLD.md",
            "decision": "FLEET.md Decision Agent (founder cards)",
            "marketing": "MARKETING.md (report, not a poster bot)",
            "money": "MONEY_LANE.md (Gmail + Stripe)",
            "guaca": "cloned, not the loop" if GUACA.exists() else "missing",
            "rakazo": "cloned, not the loop" if RAKAZO.exists() else "missing",
        },
    }
    SNAP.mkdir(parents=True, exist_ok=True)
    latest = SNAP / "latest.json"
    prev = SNAP / "previous.json"
    if latest.exists():
        prev.write_bytes(latest.read_bytes())
    latest.write_text(json.dumps(snap, indent=2), encoding="utf-8")
    return snap


def score(snap: dict) -> list[str]:
    fails: list[str] = []
    prs = snap.get("prs") or []
    by_id = {p["id"]: p for p in prs}

    for hold in NAMED_HOLDS:
        if hold not in by_id:
            fails.append(f"HOLD_MISSING {hold} (merged or dropped -- founder must lift holds in FLEET.md)")
        elif by_id[hold].get("mergeable") == "MERGEABLE":
            # MERGEABLE is not permission -- record as warn-as-fail if someone treats it as green
            pass

    fleet = FLEET.read_text(encoding="utf-8") if FLEET.exists() else ""
    agent = AGENT.read_text(encoding="utf-8") if AGENT.exists() else ""
    if "Seat **every READY ticket at once**" not in agent and "seats every READY" not in agent:
        fails.append("DOC_SERIAL_REGRESSION AGENT_SYSTEM Ticket Runner lost parallel seats")
    if "MERGEABLE is not permission" not in fleet:
        fails.append("DOC_HOLD_WEAK FLEET.md dropped MERGEABLE-is-not-permission")
    tr = TR.read_text(encoding="utf-8") if TR.exists() else ""
    if "manager" not in tr.lower():
        fails.append("DOC_RUNNER_EXECUTOR ticket-runner.md is not manager")
    rt = RUNTIME.read_text(encoding="utf-8") if RUNTIME.exists() else ""
    for needle in ("Coordinator", "FLEET.md", "One writer per branch"):
        if needle not in rt:
            fails.append(f"RUNTIME_MISSING {needle}")

    groups: dict[tuple[str, str], list[str]] = {}
    for p in prs:
        if not p.get("key"):
            continue
        groups.setdefault((p["repo"], p["key"]), []).append(p["id"])
    for (repo, key), ids in groups.items():
        if len(ids) > 1:
            fails.append(f"DUAL_WRITE {repo} {key} writers={ids}")

    for pid, head in FROZEN_HEADS.items():
        p = by_id.get(pid)
        if not p:
            fails.append(f"FROZEN_GONE {pid} expected head {head}")
        elif p["head"] != head:
            fails.append(f"FROZEN_ATTACH {pid} head={p['head']} expected={head}")

    # AGENT_SYSTEM.md section 7: a demo/* branch is NEVER merged to main. It is
    # recorded from and deleted.
    #
    # This check used to read `prs`, which is the OPEN list, for state == "MERGED".
    # The comment underneath said so out loud - "open list has no MERGED" - which
    # means the check was structurally incapable of firing, and the result was
    # assigned to a variable nothing ever read. A checker that reports success while
    # analysing nothing is worse than no checker (R-0007), so it now reads a list
    # that can actually contain the thing it looks for, and appends to fails.
    demo_merged = snap.get("demo_merged_to_main")
    if demo_merged is None:
        # The snapshot could not answer. That is not a pass - say so, rather than
        # inheriting the old silent green.
        fails.append("DEMO_MERGE_NOT_EVALUATED could not list merged demo/* PRs")
    else:
        for p in demo_merged:
            fails.append(f"DEMO_MERGED {p.get('id')} head={p.get('head')} was merged to main")

    a42 = snap.get("airgpt_42") or {}
    if a42.get("state") and a42["state"].lower() != "open":
        fails.append(f"AIRGPT_42_CLOSED state={a42.get('state')}")

    c45 = (snap.get("floors") or {}).get("Netie-AI/Cortex#45") or {}
    if (c45.get("state") or "").upper() == "MERGED":
        # The floor is pinned to one PR id. That PR is now merged, so every run since
        # has taken this branch and the VACUOUS_GREEN detector below has not executed
        # once - the detector that exists to catch a gate reporting green while its
        # own floor is red became the thing it detects.
        #
        # A stale floor is a finding, not a pass. Re-pin IN_FLIGHT_FLOOR to a PR that
        # is actually in flight; until someone does, this fails loudly.
        fails.append(
            f"FLOOR_STALE {IN_FLIGHT_FLOOR[0]} is MERGED - the vacuous-green detector "
            f"has not run since. Re-pin IN_FLIGHT_FLOOR to an in-flight PR."
        )
    else:
        checks = c45.get("checks") or []
        named = {c["name"]: c.get("conclusion") for c in checks}
        floor_name = IN_FLIGHT_FLOOR[1]
        if checks:
            conc = named.get(floor_name)
            ok = sum(1 for c in checks if c.get("conclusion") == "SUCCESS")
            if ok == len(checks) - 1 and conc == "FAILURE":
                fails.append(
                    f"VACUOUS_GREEN Cortex#45 {ok}/{len(checks)} SUCCESS but {floor_name}=FAILURE"
                )
            elif conc == "FAILURE":
                fails.append(f"CI_FLOOR Cortex#45 {floor_name}=FAILURE")
            elif conc != "SUCCESS":
                fails.append(f"CI_FLOOR Cortex#45 {floor_name}={conc or 'PENDING'}")

    if snap.get("plane_err"):
        fails.append(f"PLANE_DOWN {snap['plane_err']}")
    else:
        gh_ids = {p["id"] for p in prs}
        pl_ids = {x["external_id"] for x in snap.get("plane") or []}
        missing = sorted(gh_ids - pl_ids)
        extra = sorted(pl_ids - gh_ids)
        if missing:
            fails.append(f"PLANE_LAG missing={missing[:8]}")
        if extra:
            fails.append(f"PLANE_DRIFT extra={extra[:8]} (view invented SoT)")

    if "Cortex#42" in fleet and "skipped" not in fleet.lower():
        fails.append("DOC_C42 FLEET.md lost skip on Cortex#42")
    return fails


def attack() -> int:
    """Fixtures. A green here does not prove live gh. Live is `check`."""
    fails: list[str] = []

    # Vacuous: 4 SUCCESS + 1 FAILURE is not green
    snap = {
        "prs": [],
        "floors": {
            "Netie-AI/Cortex#45": {
                "checks": [
                    {"name": "rls-proof", "conclusion": "SUCCESS"},
                    {"name": "secrets-scan", "conclusion": "SUCCESS"},
                    {"name": "base-install", "conclusion": "SUCCESS"},
                    {"name": "protected-paths", "conclusion": "SUCCESS"},
                    {"name": "lint-type-test", "conclusion": "FAILURE"},
                ]
            }
        },
        "airgpt_42": {"state": "OPEN"},
        "plane": [],
        "plane_err": "forced-empty",
    }
    got = [f for f in score(snap) if f.startswith("VACUOUS_GREEN") or f.startswith("CI_FLOOR") or f.startswith("PLANE_DOWN")]
    if not any(x.startswith("VACUOUS_GREEN") or x.startswith("CI_FLOOR") for x in got):
        fails.append("ATTACK_MISS vacuous-green of Cortex#45 was not caught")

    snap_pending = {
        "prs": [],
        "floors": {
            "Netie-AI/Cortex#45": {
                "checks": [
                    {"name": "lint-type-test", "conclusion": ""},
                    {"name": "rls-proof", "conclusion": "SUCCESS"},
                ]
            }
        },
        "airgpt_42": {"state": "OPEN"},
        "plane": [],
        "plane_err": "x",
    }
    got_p = score(snap_pending)
    if not any("PENDING" in x for x in got_p):
        fails.append("ATTACK_MISS empty lint-type-test conclusion was treated as green")

    # Dual write FF-02
    snap2 = {
        "prs": [
            {"id": "Netie-AI/dms#61", "repo": "Netie-AI/dms", "number": 61, "title": "FF-02 polarity", "head": "a", "base": "main", "mergeable": "MERGEABLE", "key": "FF-02"},
            {"id": "Netie-AI/dms#62", "repo": "Netie-AI/dms", "number": 62, "title": "FF-02 acl", "head": "b", "base": "main", "mergeable": "MERGEABLE", "key": "FF-02"},
        ],
        "floors": {},
        "airgpt_42": {"state": "OPEN"},
        "plane": [],
        "plane_err": "x",
    }
    got2 = score(snap2)
    if not any("DUAL_WRITE" in x for x in got2):
        fails.append("ATTACK_MISS dual-write FF-02 was not caught")
    claims2 = build_claims(snap2)
    extra_roles = [v["role"] for v in claims2["by_pr"].values()]
    if extra_roles.count("EXTRA_STOP") != 1 or claims2["by_pr"]["Netie-AI/dms#61"]["role"] != "HELD":
        fails.append("ATTACK_MISS claims board did not mark dms#62 EXTRA_STOP with #61 HELD")

    # MERGEABLE held is still present (not a fail by itself) -- merging would be gone from open list
    snap3 = {
        "prs": [],
        "floors": {},
        "airgpt_42": {"state": "OPEN"},
        "plane": [],
        "plane_err": "x",
    }
    got3 = score(snap3)
    if not any("HOLD_MISSING Netie-AI/dms#61" in x for x in got3):
        fails.append("ATTACK_MISS dropped hold dms#61 was not caught")

    # Plane extra = second SoT
    snap4 = {
        "prs": [{"id": "Netie-AI/dms#61", "repo": "Netie-AI/dms", "number": 61, "title": "x", "head": FROZEN_HEADS["Netie-AI/dms#61"], "base": "main", "mergeable": "UNKNOWN", "key": None}],
        "floors": {},
        "airgpt_42": {"state": "OPEN"},
        "plane": [{"external_id": "Netie-AI/dms#61", "name": "ok"}, {"external_id": "ghost#1", "name": "invented"}],
        "plane_err": None,
    }
    got4 = score(snap4)
    if not any("PLANE_DRIFT" in x for x in got4):
        fails.append("ATTACK_MISS Plane extra work item was not caught")

    # Frozen attach
    snap5 = {
        "prs": [
            {"id": "Netie-AI/Cortex#44", "repo": "Netie-AI/Cortex", "number": 44, "title": "SEC-01", "head": "cursor/other-writer", "base": "main", "mergeable": "UNKNOWN", "key": "SEC-01"},
            {"id": "Netie-AI/dms#61", "repo": "Netie-AI/dms", "number": 61, "title": "h", "head": FROZEN_HEADS["Netie-AI/dms#61"], "base": "main", "mergeable": "UNKNOWN", "key": None},
        ],
        "floors": {},
        "airgpt_42": {"state": "OPEN"},
        "plane": [{"external_id": "Netie-AI/Cortex#44"}, {"external_id": "Netie-AI/dms#61"}],
        "plane_err": None,
    }
    got5 = score(snap5)
    if not any("FROZEN_ATTACH Netie-AI/Cortex#44" in x for x in got5):
        fails.append("ATTACK_MISS second writer on Cortex#44 was not caught")

    if fails:
        print("ATTACK FAIL")
        for f in fails:
            print(f"- {f}")
        return 1
    print("ATTACK PASS 7 fixtures (vacuous-green, pending-floor, dual-write, claims-extra-stop, dropped-hold, plane-drift, frozen-attach)")
    return 0


def build_claims(snap: dict) -> dict:
    """One ticket key -> one owner. Extras STOP. Agents read this instead of chatting."""
    prs = list(snap.get("prs") or [])
    groups: dict[str, list[dict]] = {}
    for p in prs:
        key = p.get("key") or p["id"]
        groups.setdefault(f"{p['repo']}::{key}", []).append(p)
    tickets = []
    by_pr = {}
    for gkey, rows in sorted(groups.items()):
        rows = sorted(rows, key=lambda x: x["number"])
        hold = next((p for p in rows if p["id"] in NAMED_HOLDS), None)
        frozen = next((p for p in rows if p["id"] in FROZEN_HEADS), None)
        if hold:
            owner, role = hold, "HELD"
        elif frozen:
            owner, role = frozen, "SEATED"
        else:
            owner, role = rows[0], "SEATED"
        if owner["id"] in UNSEAT_NO_WRITE:
            role = "UNSEATED"
        extras = [p for p in rows if p["id"] != owner["id"]]
        tickets.append(
            {
                "ticket": gkey.split("::", 1)[1],
                "repo": owner["repo"],
                "owner_pr": owner["id"],
                "head": owner["head"],
                "role": role,
                "may_write": role == "SEATED",
                "extras": [p["id"] for p in extras],
            }
        )
        by_pr[owner["id"]] = {
            "ticket": gkey.split("::", 1)[1],
            "role": role,
            "may_write": role == "SEATED",
            "reason": "named hold" if role == "HELD" else "first/frozen writer",
        }
        for p in extras:
            by_pr[p["id"]] = {
                "ticket": gkey.split("::", 1)[1],
                "role": "EXTRA_STOP",
                "may_write": False,
                "reason": f"dual-write; owner is {owner['id']}. Pick a different ticket.",
            }
    return {
        "ts": snap.get("ts"),
        "rule": "Read this file before writing. EXTRA_STOP and HELD must not write. Inform others by leaving this file as the inbox -- do not chat-storm CI.",
        "tickets": tickets,
        "by_pr": by_pr,
    }


def write_panel(snap: dict, claims: dict, fails: list[str]) -> Path:
    SNAP.mkdir(parents=True, exist_ok=True)
    status = "FAIL" if fails else "PASS"
    fail_html = "".join(f"<li>{html.escape(f)}</li>" for f in fails) or "<li>none</li>"
    claim_rows = []
    for t in claims.get("tickets") or []:
        extras = ", ".join(t["extras"]) or "-"
        write = "YES" if t["may_write"] else "NO"
        claim_rows.append(
            "<tr>"
            f"<td>{html.escape(t['ticket'])}</td>"
            f"<td>{html.escape(t['owner_pr'])}</td>"
            f"<td>{html.escape(t['role'])}</td>"
            f"<td>{write}</td>"
            f"<td>{html.escape(t['head'])}</td>"
            f"<td>{html.escape(extras)}</td>"
            "</tr>"
        )
    pr_rows = []
    by_pr = claims.get("by_pr") or {}
    for p in snap.get("prs") or []:
        c = by_pr.get(p["id"], {})
        pr_rows.append(
            "<tr>"
            f"<td>{html.escape(p['id'])}</td>"
            f"<td>{html.escape(c.get('role', '?'))}</td>"
            f"<td>{'YES' if c.get('may_write') else 'NO'}</td>"
            f"<td>{html.escape(p.get('head') or '')}</td>"
            f"<td>{html.escape((p.get('title') or '')[:90])}</td>"
            "</tr>"
        )
    c45 = ((snap.get("floors") or {}).get("Netie-AI/Cortex#45") or {}).get("checks") or []
    floor_html = "".join(
        f"<li>{html.escape(c.get('name') or '')} = {html.escape(c.get('conclusion') or 'PENDING')}</li>"
        for c in c45
    ) or "<li>no checks</li>"
    page = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta http-equiv="refresh" content="30"/>
<title>Netie 24x7 panel</title>
<style>
body {{ font-family: Consolas, monospace; background:#111; color:#ddd; margin:16px; }}
h1,h2 {{ color:#fff; }}
.fail {{ color:#f66; }} .pass {{ color:#6d6; }}
table {{ border-collapse: collapse; width:100%; margin:12px 0; }}
td,th {{ border:1px solid #444; padding:4px 8px; text-align:left; font-size:13px; }}
th {{ background:#222; }}
.note {{ color:#aaa; max-width:72rem; }}
</style></head><body>
<h1>Netie 24x7 panel</h1>
<p>GitHub Issues are SoT. This panel is a view. Refresh every 30s. Watchdog every 15 min.</p>
<h2>Shells (GET / display only)</h2>
<ul>
<li>Plane <a href="http://localhost:8099/netie/">http://localhost:8099/netie/</a> = {html.escape((snap.get("shells") or {}).get("plane") or "?")}</li>
<li>Netie Control GET <code>/api/health</code> :3100 = {html.escape((snap.get("shells") or {}).get("netie_control") or "?")} -- GATED, do not boot</li>
<li>Loop = Ticket Runner + FLEET identities. Grok Bot is a worker. No LangChain / Activepieces clone.</li>
<li>PRD / Epic / Ticket Runner pads = {html.escape((snap.get("shells") or {}).get("prd_agent") or "?")} / {html.escape((snap.get("shells") or {}).get("epic_agent") or "?")} / {html.escape((snap.get("shells") or {}).get("ticket_runner") or "?")}</li>
<li>Gating / PR Bot / Decision / Marketing / Money = identities in FLEET, not extra processes. {html.escape((snap.get("shells") or {}).get("gating") or "")}</li>
<li>Guaca = {html.escape((snap.get("shells") or {}).get("guaca") or "?")}. Rakazo = {html.escape((snap.get("shells") or {}).get("rakazo") or "?")}. Do not start them as the loop.</li>
</ul>
<h2 class="{'fail' if fails else 'pass'}">GATE {html.escape(status)}</h2>
<p class="note">{html.escape(snap.get('ts') or '')} -- agents inform each other via CLAIMS.json, not chat. Dual/triple write = EXTRA_STOP must pick a different ticket.</p>
<ul>{fail_html}</ul>
<h2>Claims (one writer per ticket)</h2>
<table>
<tr><th>ticket</th><th>owner PR</th><th>role</th><th>may_write</th><th>branch</th><th>extras STOP</th></tr>
{''.join(claim_rows)}
</table>
<h2>Cortex#45 floors</h2>
<ul>{floor_html}</ul>
<h2>All open PRs</h2>
<table>
<tr><th>PR</th><th>role</th><th>may_write</th><th>branch</th><th>title</th></tr>
{''.join(pr_rows)}
</table>
<p class="note">Held: dms#61. Skip Cortex#42. Frozen Cortex #4 #41 #43 #44 #45 same branch only. AirGPT#42 stays OPEN. Task NetieEstate24x7 is PT15M; it stops on battery.</p>
</body></html>
"""
    path = SNAP / "panel.html"
    path.write_text(page, encoding="utf-8")
    (HERE / "CLAIMS.json").write_text(json.dumps(claims, indent=2), encoding="utf-8")
    (SNAP / "CLAIMS.json").write_text(json.dumps(claims, indent=2), encoding="utf-8")
    return path


def check() -> int:
    snap = live_snapshot()
    fails = score(snap)
    claims = build_claims(snap)
    panel = write_panel(snap, claims, fails)
    (SNAP / "last_check.txt").write_text(
        "\n".join([snap["ts"], *fails]) if fails else f"{snap['ts']}\nPASS\n",
        encoding="utf-8",
    )
    extras = sum(1 for v in claims["by_pr"].values() if v["role"] == "EXTRA_STOP")
    print(f"SNAPSHOT {SNAP / 'latest.json'}")
    print(f"CLAIMS {HERE / 'CLAIMS.json'} extras_stop={extras}")
    print(f"PANEL {panel}")
    print(f"COMPARE previous={SNAP / 'previous.json'} prs={len(snap['prs'])} plane={len(snap.get('plane') or [])}")
    if fails:
        print("GATE FAIL")
        for f in fails:
            print(f"- {f}")
        return 1
    print("GATE PASS")
    return 0


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "attack":
        return attack()
    if cmd == "snapshot":
        snap = live_snapshot()
        print(f"wrote {SNAP / 'latest.json'} prs={len(snap['prs'])} plane={len(snap.get('plane') or [])}")
        return 0
    if cmd == "check":
        return check()
    if cmd == "all":
        a = attack()
        c = check()
        return a or c
    print("usage: estate_gate.py attack|snapshot|check|all", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
