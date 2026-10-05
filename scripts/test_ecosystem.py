#!/usr/bin/env python3
"""Ecosystem lane gate (DR-0002). python3 scripts/test_ecosystem.py

No network. Each rule is proven twice: it passes the real catalog, and it fails when broken.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ecosystem
from ecosystem import Refuse, load, render, validate

ROOT = Path(__file__).resolve().parents[1]


def _row(**kw) -> dict:
    row = {
        "slug": "demo", "upstream": "acme/demo", "commit": "abcdef1234", "license": "MIT",
        "license_class": "permissive", "license_file": "LICENSE", "license_sha256": "0" * 64,
        "kind": "app", "mode": "fork-rebrand", "product": "Crew", "netie_name": "Crew Demo",
        "brand_from": ["Demo"], "role": "r", "gate": "g", "stage": 0,
    }
    row.update(kw)
    return row


def _errs(**kw) -> list[str]:
    return validate({"projects": [_row(**kw)], "unresolved": []}, ROOT)


def _git(d: Path, *a: str) -> None:
    subprocess.run(["git", "-C", str(d), *a], check=True, capture_output=True)


class CatalogGate(unittest.TestCase):
    def test_real_catalog_is_valid(self) -> None:
        self.assertEqual(validate(load()), [])

    def test_table_is_current(self) -> None:
        on_disk = (ROOT / "ecosystem" / "ECOSYSTEM.md").read_text(encoding="utf-8")
        self.assertEqual(on_disk, render(load()), "run: python3 scripts/ecosystem.py render")

    def test_no_non_permissive_row_is_forked(self) -> None:
        for p in load()["projects"]:
            if p["mode"] in ecosystem.FORK:
                self.assertIn(p["license_class"], ("permissive", "permissive-carveout"), p["slug"])

    def test_known_traps_are_not_forkable(self) -> None:
        modes = {p["slug"]: p["mode"] for p in load()["projects"]}
        self.assertEqual(modes["n8n"], "blocked")
        self.assertEqual(modes["open-webui"], "blocked")
        self.assertEqual(modes["nadirclaw"], "blocked")
        self.assertEqual(modes["dify"], "host")
        self.assertEqual(modes["routerly"], "host")

    def test_gate_can_fail_noncommercial_fork(self) -> None:
        self.assertTrue(any("not allowed" in e for e in _errs(license_class="noncommercial")))

    def test_gate_can_fail_copyleft_fork(self) -> None:
        self.assertTrue(any("not allowed" in e for e in _errs(license_class="copyleft")))

    def test_gate_can_fail_branding_locked_fork(self) -> None:
        self.assertTrue(any("not allowed" in e for e in _errs(license_class="branding-locked")))

    def test_gate_can_fail_library_fork(self) -> None:
        self.assertTrue(any("depended on" in e for e in _errs(kind="library")))

    def test_gate_can_fail_bad_inputs(self) -> None:
        self.assertTrue(_errs(commit="main"))
        self.assertTrue(_errs(license_sha256="abc"))
        self.assertTrue(_errs(product="Gizmo"))
        self.assertTrue(_errs(netie_name="Crew Démo"))
        self.assertTrue(_errs(mode="blocked", license_class="noncommercial"))  # no why, no alt
        self.assertTrue(_errs(mode="fork-strip"))  # nothing to strip
        self.assertTrue(_errs(strip=["LICENSE"], mode="fork-strip", why="x"))  # strips a license file

    def test_stage_one_needs_an_overlay(self) -> None:
        self.assertTrue(any("overlay" in e for e in _errs(stage=1)))

    def test_unresolved_rows_need_a_question(self) -> None:
        errs = validate({"projects": [], "unresolved": [{"name": "x"}]}, ROOT)
        self.assertEqual(len(errs), 3)


class Rebrand(unittest.TestCase):
    def _upstream(self, tmp: Path, *, crlf: bool = False) -> tuple[Path, dict]:
        d = tmp / "up"
        (d / "ee").mkdir(parents=True)
        (d / "docs").mkdir()
        lic = "MIT License\nCopyright (c) 2026 Acme\nPermission is hereby granted\n"
        (d / "LICENSE").write_text(lic, encoding="utf-8")
        (d / "NOTICE").write_text("Demo NOTICE by Acme\n", encoding="utf-8")
        (d / "ee" / "paid.ts").write_text("export const x = 1\n", encoding="utf-8")
        nl = "\r\n" if crlf else "\n"
        readme = nl.join([
            "# Demo", "Demo is a tool. See [Demo](https://github.com/acme/demo).",
            "Run `demo init` then:", "```", "demo run   # Demo stays in code", "```",
            "Demo-cli and demo.io are identifiers, not prose.", "",
        ])
        (d / "README.md").write_bytes(readme.encode())
        (d / "docs" / "a.md").write_text("Demo guide\n", encoding="utf-8")
        _git(d, "init", "-q")
        _git(d, "-c", "user.name=t", "-c", "user.email=t@t", "add", "-A")
        _git(d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base")
        row = _row(license_sha256=hashlib.sha256(lic.encode()).hexdigest(), strip=["ee"],
                   mode="fork-strip", why="ee is paid")
        return d, row

    def test_rebrand_touches_prose_only_and_keeps_license(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d, row = self._upstream(Path(tmp))
            lic_before = (d / "LICENSE").read_bytes()
            changed = ecosystem.rebrand(row, d)
            self.assertEqual((d / "LICENSE").read_bytes(), lic_before)
            self.assertEqual((d / "NOTICE").read_text(encoding="utf-8"), "Demo NOTICE by Acme\n")
            self.assertFalse((d / "ee").exists(), "stripped path must be gone")
            text = (d / "README.md").read_text(encoding="utf-8")
            self.assertIn("# Crew Demo", text)
            self.assertIn("Crew Demo is a tool", text)
            self.assertIn("`demo init`", text)  # code span untouched
            self.assertIn("demo run   # Demo stays in code", text)  # fence untouched
            self.assertIn("github.com/acme/demo", text)  # link target untouched
            self.assertIn("Demo-cli and demo.io", text)  # identifier-shaped untouched
            self.assertEqual(text.count("Crew Crew"), 0)
            self.assertIn("Crew Demo guide", (d / "docs" / "a.md").read_text(encoding="utf-8"))
            self.assertIn("NETIE-ATTRIBUTION.md", changed)
            attr = (d / "NETIE-ATTRIBUTION.md").read_text(encoding="utf-8")
            self.assertIn("Copyright (c) 2026 Acme", attr)
            self.assertIn("stage 2", attr.lower())

    def test_banner_does_not_double_the_netie_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d, row = self._upstream(Path(tmp))
            ecosystem.rebrand({**row, "netie_name": "Netie Control"}, d)
            for rel in ("README.md", "NETIE-ATTRIBUTION.md"):
                text = (d / rel).read_text(encoding="utf-8")
                self.assertNotIn("Netie Netie", text, rel)
            self.assertIn("**Netie Control** is a modified distribution", (d / "README.md").read_text(encoding="utf-8"))

    def test_rebrand_preserves_crlf(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d, row = self._upstream(Path(tmp), crlf=True)
            ecosystem.rebrand(row, d)
            raw = (d / "README.md").read_bytes()
            self.assertNotIn(b"\n", raw.replace(b"\r\n", b""), "every newline must stay CRLF")

    def test_translations_notices_and_changelogs_are_left_alone(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d, row = self._upstream(Path(tmp))
            (d / "docs" / "i18n" / "fr").mkdir(parents=True)
            (d / "docs" / "i18n" / "fr" / "a.md").write_text("Demo en francais\n", encoding="utf-8")
            (d / "THIRD_PARTY_NOTICES.md").write_text("Demo uses libfoo\n", encoding="utf-8")
            (d / "CHANGELOG.md").write_text("Demo 1.0 released\n", encoding="utf-8")
            _git(d, "-c", "user.name=t", "-c", "user.email=t@t", "add", "-A")
            _git(d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "more")
            ecosystem.rebrand(row, d)
            for rel, keep in (("docs/i18n/fr/a.md", "Demo en francais"), ("THIRD_PARTY_NOTICES.md", "Demo uses libfoo"),
                              ("CHANGELOG.md", "Demo 1.0 released")):
                self.assertIn(keep, (d / rel).read_text(encoding="utf-8"), rel)

    def test_too_many_docs_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d, row = self._upstream(Path(tmp))
            old = ecosystem.MAX_DOC_FILES
            ecosystem.MAX_DOC_FILES = 1
            try:
                with self.assertRaises(Refuse):
                    ecosystem.rebrand(row, d)
            finally:
                ecosystem.MAX_DOC_FILES = old

    def test_license_drift_refuses_and_changes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d, row = self._upstream(Path(tmp))
            row["license_sha256"] = "f" * 64
            with self.assertRaises(Refuse) as cm:
                ecosystem.rebrand(row, d)
            self.assertIn("drift", str(cm.exception))
            self.assertTrue((d / "ee").exists())
            self.assertFalse((d / "NETIE-ATTRIBUTION.md").exists())

    def test_host_and_blocked_rows_refuse_rebrand(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d, row = self._upstream(Path(tmp))
            for mode in ("host", "blocked", "depend"):
                with self.assertRaises(Refuse):
                    ecosystem.rebrand({**row, "mode": mode}, d)

    def test_dirty_checkout_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d, row = self._upstream(Path(tmp))
            (d / "README.md").write_text("edited\n", encoding="utf-8")
            with self.assertRaises(Refuse):
                ecosystem.rebrand(row, d)

    def test_overlay_round_trip(self) -> None:
        """rebrand --overlay on one clone, apply on a fresh clone: same bytes."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            d, row = self._upstream(tmp)
            fresh = tmp / "fresh"
            subprocess.run(["git", "clone", "-q", str(d), str(fresh)], check=True, capture_output=True)
            old = ecosystem.OVERLAYS
            ecosystem.OVERLAYS = tmp / "overlays"
            try:
                ecosystem.rebrand(row, d, overlay=True)
                meta = json.loads((ecosystem.OVERLAYS / "demo" / "overlay.json").read_text(encoding="utf-8"))
                self.assertEqual(meta["stripped"], ["ee"])
                self.assertNotIn("ee/paid.ts", (ecosystem.OVERLAYS / "demo" / "0001-rebrand.patch").read_text(encoding="utf-8"))
                ecosystem.apply(row, fresh)
            finally:
                ecosystem.OVERLAYS = old
            for rel in ("README.md", "docs/a.md", "NETIE-ATTRIBUTION.md"):
                self.assertEqual((d / rel).read_bytes(), (fresh / rel).read_bytes(), rel)
            self.assertFalse((fresh / "ee").exists())


class Layout(unittest.TestCase):
    def test_no_secrets_or_trees_in_ecosystem_dir(self) -> None:
        big = [p for p in (ROOT / "ecosystem").rglob("*") if p.is_file() and p.stat().st_size > 2_000_000]
        self.assertEqual(big, [], "overlays are patch series, never vendored trees")

    def test_catalog_copy_is_not_mutated_by_validate(self) -> None:
        cat = load()
        snap = copy.deepcopy(cat)
        validate(cat)
        self.assertEqual(cat, snap)


if __name__ == "__main__":
    unittest.main()
