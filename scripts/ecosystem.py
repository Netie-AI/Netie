#!/usr/bin/env python3
"""Ecosystem lane (DR-0002): catalog gate, generated table, license drift, rebrand overlays.

    python3 scripts/ecosystem.py validate
    python3 scripts/ecosystem.py render [--check]
    python3 scripts/ecosystem.py drift                       # network: re-hash upstream licenses
    python3 scripts/ecosystem.py clone SLUG DIR              # shallow clone at the pinned base
    python3 scripts/ecosystem.py rebrand SLUG DIR [--overlay]  # stage 1 on a pristine checkout
    python3 scripts/ecosystem.py apply SLUG DIR              # replay the overlay patch series

We fork and rebrand only permissive upstreams, LICENSE and NOTICE untouched. Everything
else is hosted unmodified or blocked. Stage 1 is docs, attribution and strips only: it never
renames a package, binary or identifier, because that needs a build to prove. Stdlib only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "ecosystem" / "catalog.json"
TABLE = ROOT / "ecosystem" / "ECOSYSTEM.md"
OVERLAYS = ROOT / "ecosystem" / "overlays"

FORK = ("fork-rebrand", "fork-strip")
MODES = FORK + ("depend", "host", "blocked")
#: Which modes a license class may take. A gate that cannot say no is not a gate.
ALLOWED = {
    "permissive": set(MODES) - {"blocked"},
    "permissive-carveout": {"fork-strip", "depend", "host"},
    "copyleft": {"host", "blocked"},
    "source-available": {"host", "blocked"},
    "branding-locked": {"host", "blocked"},
    "noncommercial": {"blocked"},
}
PRODUCTS = {"Cortex", "OpenVault", "FreeIDE", "AirGPT", "Crew", "Control", "KB", "Pointer",
            "Constructor", "DMS", "Space"}
KINDS = {"app", "library", "service"}
REQUIRED = ("slug", "upstream", "commit", "license", "license_class", "license_file",
            "license_sha256", "kind", "mode", "product", "netie_name", "role", "gate", "stage")
#: Files that carry legal text or history are never rewritten, and neither are translations.
PROTECTED = re.compile(r"licen[cs]e|notice|copying|patents|third[_-]?party|attribution|changelog|history", re.I)
SKIP_DIRS = {"i18n", "locales", "locale", "translations", "node_modules", "LICENSES", ".git"}
MAX_DOC_FILES = 600
STAGES = "0 catalogued | 1 overlay patch exists | 2 gate wired and tested | 3 shippable"


class Refuse(Exception):
    """A rule said no. Printed, exit 1."""


def load(path: Path = CATALOG) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(cat: dict, root: Path = ROOT) -> list[str]:
    errs: list[str] = []
    if not json.dumps(cat, ensure_ascii=False).isascii():
        errs.append("catalog: non-ASCII text (laptop-ASCII rule)")
    seen: set[str] = set()
    slugs = {p.get("slug") for p in cat.get("projects", [])}
    for p in cat.get("projects", []):
        s = p.get("slug", "?")
        missing = [k for k in REQUIRED if k not in p]
        if missing:
            errs.append(f"{s}: missing {', '.join(missing)}")
            continue
        if s in seen:
            errs.append(f"{s}: duplicate slug")
        seen.add(s)
        def bad(msg: str, s: str = s) -> None:
            errs.append(f"{s}: {msg}")

        if not re.fullmatch(r"[\w.-]+/[\w.-]+", p["upstream"]):
            bad("upstream must be owner/repo")
        if not re.fullmatch(r"[0-9a-f]{7,40}", p["commit"]):
            bad("commit must be 7-40 hex")
        if not re.fullmatch(r"[0-9a-f]{64}", p["license_sha256"]):
            bad("license_sha256 must be 64 hex")
        if p["kind"] not in KINDS:
            bad(f"kind {p['kind']!r} not in {sorted(KINDS)}")
        if p["product"] not in PRODUCTS:
            bad(f"product {p['product']!r} is not a Netie product")
        if p["mode"] not in MODES:
            bad(f"mode {p['mode']!r} not in {MODES}")
        if p["license_class"] not in ALLOWED:
            bad(f"license_class {p['license_class']!r} unknown")
        elif p["mode"] in MODES and p["mode"] not in ALLOWED[p["license_class"]]:
            bad(f"mode {p['mode']} is not allowed for license_class {p['license_class']}")
        if not isinstance(p["stage"], int) or not 0 <= p["stage"] <= 3:
            bad("stage must be 0-3")
        if p["mode"] in FORK:
            if p["kind"] == "library":
                bad("a library is depended on, not forked")
            if not p.get("brand_from"):
                bad("fork modes need brand_from (display names to rebrand in prose)")
            if p["mode"] == "fork-strip" and not (p.get("strip") or p.get("disable")):
                bad("fork-strip needs strip or disable")
            if p["mode"] == "fork-strip" and not p.get("why"):
                bad("fork-strip needs why")
            if p["stage"] >= 1:
                ov = root / "ecosystem" / "overlays" / s
                if not (ov / "overlay.json").is_file() or not list(ov.glob("*.patch")):
                    bad("stage >= 1 needs ecosystem/overlays/<slug>/overlay.json and a .patch")
                else:
                    base = json.loads((ov / "overlay.json").read_text(encoding="utf-8"))["base_commit"]
                    if not base.startswith(p["commit"]):
                        bad(f"overlay base {base[:10]} is not the catalog commit {p['commit']}")
        if p["mode"] in ("host", "blocked") and not p.get("why"):
            bad(f"{p['mode']} needs why")
        if p["mode"] in ("host", "blocked") and not p.get("alt"):
            bad(f"{p['mode']} needs alt")
        for rel in p.get("strip", []):
            if rel.startswith(("/", "..")) or PROTECTED.search(Path(rel).name):
                bad(f"strip path {rel!r} is unsafe or names a license file")
        if p.get("superseded_by") and p["superseded_by"] not in slugs:
            bad("superseded_by names an unknown slug")
    for u in cat.get("unresolved", []):
        for k in ("name", "status", "why", "ask"):
            if k not in u:
                errs.append(f"unresolved {u.get('name', '?')}: missing {k}")
    return errs


def render(cat: dict) -> str:
    order = {m: i for i, m in enumerate(MODES)}
    rows = sorted(cat["projects"], key=lambda p: (order[p["mode"]], p["product"], p["slug"]))
    out = [
        "# Netie ecosystem catalog",
        "",
        "GENERATED by `python3 scripts/ecosystem.py render` from `ecosystem/catalog.json`. Do not hand-edit.",
        f"Licenses verified {cat['verified_on']} from each upstream LICENSE file at the pinned commit.",
        "Not verified: vendor terms of service, counsel review, whether each upstream still builds.",
        "",
        f"Stages: {STAGES}. Decision: `docs/decisions/DR-0002-adopt-and-rebrand-permissive-upstreams.md`.",
        "",
    ]
    titles = {
        "fork-rebrand": "Ship under the Netie name (permissive, license and notices kept)",
        "fork-strip": "Ship under the Netie name after stripping what the license or policy forbids",
        "depend": "Depend on (libraries: no fork, no rebrand)",
        "host": "Host unmodified, never rebrand",
        "blocked": "Blocked: license forbids the plan",
    }
    for mode in MODES:
        part = [p for p in rows if p["mode"] == mode]
        if not part:
            continue
        out += [f"## {titles[mode]}", "",
                "| Netie name | Upstream | License | Feeds | Stage |", "|---|---|---|---|---|"]
        for p in part:
            out.append(f"| {p['netie_name']} | {p['upstream']} @ {p['commit']} | {p['license']} "
                       f"| {p['product']} | {p['stage']} |")
        out.append("")
        for p in part:
            out.append(f"- **{p['slug']}**: {p['role']}")
            out.append(f"  - Gate: {p['gate']}")
            if p.get("strip"):
                out.append(f"  - Stripped paths: {', '.join(p['strip'])}")
            for d in p.get("disable", []):
                out.append(f"  - Must be off before release: {d}")
            if p.get("why"):
                out.append(f"  - Why: {p['why']}")
            if p.get("alt"):
                out.append(f"  - Instead: {p['alt']}")
            if p.get("superseded_by"):
                out.append(f"  - Superseded by: {p['superseded_by']}")
        out.append("")
    out += ["## Names that did not resolve to a shippable repo", "",
            "| Name | Status | Why | Need from founder |", "|---|---|---|---|"]
    for u in cat.get("unresolved", []):
        out.append(f"| {u['name']} | {u['status']} | {u['why']} | {u['ask']} |")
    return "\n".join(out) + "\n"


# ---- upstream checkouts ------------------------------------------------------------------

def git(d: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(d), *args], capture_output=True, text=True)
    if r.returncode:
        raise Refuse(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _project(cat: dict, slug: str) -> dict:
    for p in cat["projects"]:
        if p["slug"] == slug:
            return p
    raise Refuse(f"unknown slug {slug!r}")


def _check_license(p: dict, d: Path) -> None:
    lf = d / p["license_file"]
    if not lf.is_file():
        raise Refuse(f"{p['slug']}: {p['license_file']} missing in checkout")
    if _sha(lf) != p["license_sha256"]:
        raise Refuse(f"{p['slug']}: license drift, {p['license_file']} no longer matches the "
                     "catalog. Re-read it, then update the row. Nothing was changed.")


def _need_fork(p: dict) -> None:
    if p["mode"] not in FORK:
        raise Refuse(f"{p['slug']}: mode is {p['mode']}. Only {', '.join(FORK)} may be rebranded.")


def drift(cat: dict) -> int:
    bad = 0
    for p in cat["projects"]:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "r"
            r = subprocess.run(
                ["git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--sparse",
                 f"https://github.com/{p['upstream']}", str(d)],
                capture_output=True, text=True, env={**os.environ, "GIT_LFS_SKIP_SMUDGE": "1"})
            lf = d / p["license_file"]
            if r.returncode or not lf.is_file():
                print(f"FAIL  {p['slug']}: cannot read {p['license_file']} ({r.stderr.strip()[:80]})")
                bad += 1
            elif _sha(lf) != p["license_sha256"]:
                print(f"DRIFT {p['slug']}: license changed upstream, re-read before shipping")
                bad += 1
            else:
                head = git(d, "rev-parse", "--short=10", "HEAD").strip()
                moved = "" if head == p["commit"] else f" (HEAD moved to {head})"
                print(f"ok    {p['slug']}{moved}")
    return 1 if bad else 0


def clone(p: dict, d: Path) -> None:
    url = f"https://github.com/{p['upstream']}"
    meta = OVERLAYS / p["slug"] / "overlay.json"
    base = json.loads(meta.read_text(encoding="utf-8"))["base_commit"] if meta.is_file() else None
    d.mkdir(parents=True, exist_ok=True)
    if base:
        try:
            git(d, "init", "-q")
            git(d, "remote", "add", "origin", url)
            git(d, "fetch", "-q", "--depth", "1", "origin", base)
            git(d, "checkout", "-q", "FETCH_HEAD")
            return
        except Refuse as e:
            print(f"WARN cannot fetch pinned base {base[:10]} ({e}); cloning HEAD instead", file=sys.stderr)
            shutil.rmtree(d)
    r = subprocess.run(["git", "clone", "-q", "--depth", "1", url, str(d)], capture_output=True, text=True)
    if r.returncode:
        raise Refuse(f"clone failed: {r.stderr.strip()}")


# ---- stage 1 rebrand ---------------------------------------------------------------------

_FENCE = re.compile(r"^\s*(```|~~~)")
#: Never rewrite code spans, link targets, html tags or bare URLs. Identifiers are stage 2.
_SKIP = re.compile(r"(`[^`\n]*`|\]\([^)\n]*\)|<[^>\n]+>|https?://\S+)")


def _prose(text: str, names: list[str], to: str) -> str:
    pat = re.compile(r"(?<![\w/.-])(?:" + "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True))
                     + r")(?![\w/-])")
    out, fenced = [], False
    for line in text.splitlines(keepends=True):
        if _FENCE.match(line):
            fenced = not fenced
            out.append(line)
        elif fenced:
            out.append(line)
        else:
            parts = _SKIP.split(line)
            for i in range(0, len(parts), 2):
                parts[i] = pat.sub(to, parts[i])
            out.append("".join(parts))
    return "".join(out)


def _display(p: dict) -> str:
    n = p["netie_name"]
    return n if n.startswith("Netie") else f"Netie {n}"


def _doc_files(d: Path) -> list[Path]:
    files = [f for f in d.iterdir() if f.is_file() and f.suffix == ".md" and not PROTECTED.search(f.name)]
    if (d / "docs").is_dir():
        files += [f for f in (d / "docs").rglob("*.md")
                  if f.is_file() and not PROTECTED.search(f.name)
                  and not SKIP_DIRS & set(f.relative_to(d).parts)]
    if len(files) > MAX_DOC_FILES:
        raise Refuse(f"rebrand would scan {len(files)} docs (cap {MAX_DOC_FILES}); narrow SKIP_DIRS")
    return sorted(files)


def _attribution(p: dict, d: Path) -> str:
    holders = [ln.strip() for ln in (d / p["license_file"]).read_text(encoding="utf-8", errors="replace").splitlines()
               if ln.strip().lower().startswith("copyright")]
    lines = [
        "# Attribution", "",
        f"{_display(p)} is a modified distribution of {p['upstream']}",
        f"(https://github.com/{p['upstream']}), pinned at commit {p['commit']}.", "",
        f"Upstream license: {p['license']}. {p['license_file']} is included unmodified, with every",
        "upstream copyright line, and so is any NOTICE file.", "",
    ]
    lines += [f"- {h}" for h in holders]
    lines += ["", "Not affiliated with or endorsed by the upstream authors. Upstream names and",
              "logos belong to their owners.", "", "## Changed in stage 1", "",
              f"- Display name {', '.join(p['brand_from'])} rewritten to {p['netie_name']} in prose docs only.",
              "- This file and a README banner added."]
    if p.get("strip"):
        lines.append(f"- Removed because the license or policy forbids shipping them: {', '.join(p['strip'])}.")
    lines += ["", "## Not done yet (stage 2)", "",
              "- Package names, binaries, identifiers and UI strings are still upstream's.",
              "- SECURITY, SUPPORT and CONTRIBUTING contacts and URLs still point at upstream.",
              "- Translated docs, changelogs and third-party notices are untouched.",
              "- Netie gate wiring: " + p["gate"]]
    lines += [f"- Must be disabled before any release: {x}" for x in p.get("disable", [])]
    return "\n".join(lines) + "\n"


def rebrand(p: dict, d: Path, *, overlay: bool = False) -> list[str]:
    _need_fork(p)
    _check_license(p, d)
    if git(d, "status", "--porcelain").strip():
        raise Refuse(f"{p['slug']}: checkout is not pristine, run on a fresh clone")
    for rel in p.get("strip", []):
        t = d / rel
        if not t.exists():
            raise Refuse(f"{p['slug']}: strip path {rel} missing, upstream moved?")
        shutil.rmtree(t) if t.is_dir() else t.unlink()
    changed: list[str] = []
    for f in _doc_files(d):
        old = f.read_bytes().decode("utf-8", "surrogateescape")
        new = _prose(old, p["brand_from"], p["netie_name"])
        if f.name == "README.md" and f.parent == d:
            nl = "\r\n" if "\r\n" in old else "\n"
            new = (f"> **{_display(p)}** is a modified distribution of "
                   f"[{p['upstream']}](https://github.com/{p['upstream']}) ({p['license']}). "
                   f"See NETIE-ATTRIBUTION.md. Not endorsed by the upstream authors.{nl}{nl}") + new
        if new != old:
            f.write_bytes(new.encode("utf-8", "surrogateescape"))
            changed.append(str(f.relative_to(d)))
    (d / "NETIE-ATTRIBUTION.md").write_text(_attribution(p, d), encoding="utf-8", newline="\n")
    changed.append("NETIE-ATTRIBUTION.md")
    _check_license(p, d)  # prove the rebrand left the license alone
    if overlay:
        _write_overlay(p, d, changed)
    return changed


def _write_overlay(p: dict, d: Path, changed: list[str]) -> None:
    ex = [f":(exclude){rel}" for rel in p.get("strip", [])]
    git(d, "add", "-A")
    patch = git(d, "diff", "--cached", "--binary", "--", ".", *ex)
    git(d, "reset", "-q")
    out = OVERLAYS / p["slug"]
    out.mkdir(parents=True, exist_ok=True)
    (out / "0001-rebrand.patch").write_text(patch, encoding="utf-8", newline="\n")
    (out / "overlay.json").write_text(json.dumps({
        "slug": p["slug"], "upstream": p["upstream"], "base_commit": git(d, "rev-parse", "HEAD").strip(),
        "license_sha256": p["license_sha256"], "stripped": p.get("strip", []), "files_changed": changed,
        "series": sorted(x.name for x in out.glob("*.patch")),
    }, indent=2) + "\n", encoding="utf-8", newline="\n")


def pin_catalog(slug: str, commit: str, stage: int, path: Path = CATALOG) -> None:
    """Tool-owned fields: after an overlay is cut, the row pins its base commit and reaches stage 1."""
    t = path.read_text(encoding="utf-8")
    i = t.index(f'"slug": "{slug}"')
    j = t.index('"commit": "', i) + len('"commit": "')
    t = t[:j] + commit + t[t.index('"', j):]
    k = t.index('"stage": ', i) + len('"stage": ')
    stage_now = int(t[k])
    t = t[:k] + str(max(stage, stage_now)) + t[k + 1:]
    path.write_text(t, encoding="utf-8", newline="\n")


def apply(p: dict, d: Path) -> None:
    _need_fork(p)
    _check_license(p, d)
    out = OVERLAYS / p["slug"]
    patches = sorted(out.glob("*.patch"))
    if not patches:
        raise Refuse(f"{p['slug']}: no overlay patches in {out}")
    for rel in p.get("strip", []):
        t = d / rel
        if not t.exists():
            raise Refuse(f"{p['slug']}: strip path {rel} missing, upstream moved?")
        shutil.rmtree(t) if t.is_dir() else t.unlink()
    for patch in patches:
        r = subprocess.run(["git", "-C", str(d), "apply", str(patch)], capture_output=True, text=True)
        if r.returncode:
            raise Refuse(f"{patch.name} does not apply: {r.stderr.strip()}")
    _check_license(p, d)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate")
    r = sub.add_parser("render")
    r.add_argument("--check", action="store_true", help="fail if ECOSYSTEM.md is stale")
    sub.add_parser("drift")
    for name in ("clone", "rebrand", "apply"):
        s = sub.add_parser(name)
        s.add_argument("slug")
        s.add_argument("dir", type=Path)
        if name == "rebrand":
            s.add_argument("--overlay", action="store_true", help="write ecosystem/overlays/<slug>/")
    a = ap.parse_args(argv)
    try:
        cat = load()
        errs = validate(cat)
        if errs:
            print("FAIL\n" + "\n".join(errs))
            return 1
        if a.cmd == "validate":
            print(f"ok {len(cat['projects'])} projects, {len(cat.get('unresolved', []))} unresolved")
        elif a.cmd == "render":
            text = render(cat)
            if a.check:
                if not TABLE.is_file() or TABLE.read_text(encoding="utf-8") != text:
                    print("FAIL ecosystem/ECOSYSTEM.md is stale: run python3 scripts/ecosystem.py render")
                    return 1
                print("ok ECOSYSTEM.md is current")
            else:
                TABLE.write_text(text, encoding="utf-8", newline="\n")
                print(f"wrote {TABLE.relative_to(ROOT)}")
        elif a.cmd == "drift":
            return drift(cat)
        elif a.cmd == "clone":
            clone(_project(cat, a.slug), a.dir)
            print(f"cloned {a.slug} -> {a.dir}")
        elif a.cmd == "rebrand":
            p = _project(cat, a.slug)
            for f in rebrand(p, a.dir, overlay=a.overlay):
                print(f"  {f}")
            if a.overlay:
                base = json.loads((OVERLAYS / p["slug"] / "overlay.json").read_text(encoding="utf-8"))["base_commit"]
                pin_catalog(p["slug"], base[:10], 1)
                print(f"pinned {p['slug']} at {base[:10]}, stage 1 (run: python3 scripts/ecosystem.py render)")
        elif a.cmd == "apply":
            apply(_project(cat, a.slug), a.dir)
            print(f"applied {a.slug} overlay to {a.dir}")
    except Refuse as e:
        print(f"REFUSE {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
