#!/usr/bin/env python3
"""Never fake a FreeBuild URL. python3 scripts/test_freebuild_honesty.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from freebuild_honesty import ShipDenied, parse_observed_url, report_deploy


class FreebuildHonestyTests(unittest.TestCase):
    def test_constructed_pages_dev_is_denied(self) -> None:
        with self.assertRaises(ShipDenied):
            report_deploy(
                simulated=False,
                observed_url=None,
                constructed_url="https://demo.pages.dev",
            )

    def test_simulated_is_not_ht1(self) -> None:
        with self.assertRaises(ShipDenied):
            report_deploy(
                simulated=True,
                observed_url="https://demo.pages.dev",
                constructed_url=None,
            )

    def test_zero_exit_without_url_fails(self) -> None:
        with self.assertRaises(ShipDenied):
            parse_observed_url("done", exit_code=0)

    def test_wrangler_url_is_live(self) -> None:
        url = parse_observed_url(
            "Uploaded!\nhttps://demo.pages.dev\n", exit_code=0
        )
        out = report_deploy(
            simulated=False, observed_url=url, constructed_url=None
        )
        self.assertEqual(out["status"], "LIVE")
        self.assertEqual(out["ht1"], "observed")

    def test_live_ov_posts_skill_ids(self) -> None:
        from typing import Any

        from crew_ov_gate import OpenVaultCrewGate
        from crew_skills import SkillRegistry, register_skill

        seen: list[dict[str, Any]] = []

        def post(url: str, body: dict[str, Any]) -> dict[str, Any]:
            seen.append(body)
            return {"allowed": True}

        def deny(url: str, body: dict[str, Any]) -> dict[str, Any]:
            return {"allowed": False, "reason": "vault miss"}

        reg = SkillRegistry()
        register_skill(reg, "S-0004")
        ov = OpenVaultCrewGate("http://127.0.0.1:5000", post=post, registry=reg)
        with self.assertRaises(ShipDenied) as missing:
            report_deploy(
                simulated=False,
                observed_url="https://demo.pages.dev",
                constructed_url=None,
                ov=ov,
            )
        self.assertIn("parent and child", str(missing.exception))
        self.assertEqual(seen, [])
        out = report_deploy(
            simulated=False,
            observed_url="https://demo.pages.dev",
            constructed_url=None,
            ov=ov,
            parent_run_id="p1",
            child_id="ship",
        )
        self.assertEqual(out["status"], "LIVE")
        self.assertEqual(out["ht1"], "observed")
        self.assertEqual(seen[0]["skill_ids"], ["S-0004"])
        self.assertEqual(seen[0]["id"], "freebuild")
        self.assertNotIn("skill_body", str(seen[0]))
        blocked = OpenVaultCrewGate("http://127.0.0.1:5000", post=deny)
        with self.assertRaises(ShipDenied) as ctx:
            report_deploy(
                simulated=False,
                observed_url="https://demo.pages.dev",
                constructed_url=None,
                ov=blocked,
                parent_run_id="p1",
                child_id="ship",
            )
        self.assertIn("vault miss", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
