#!/usr/bin/env python3
"""Switchyard is a leave-machine dep. python3 scripts/test_switchyard_honesty.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from switchyard_honesty import SwitchyardDenied, host_switchyard


class SwitchyardHonestyTests(unittest.TestCase):
    def test_vendor_llm_router_refuses(self) -> None:
        with self.assertRaises(SwitchyardDenied) as ctx:
            host_switchyard(ov_leave=True, vendor="llm-router")
        self.assertIn("vendor", str(ctx.exception))

    def test_rewrite_triton_refuses(self) -> None:
        with self.assertRaises(SwitchyardDenied) as ctx:
            host_switchyard(ov_leave=True, rewrite_triton=True)
        self.assertIn("Triton", str(ctx.exception))

    def test_freeroute_is_not_switchyard(self) -> None:
        with self.assertRaises(SwitchyardDenied) as ctx:
            host_switchyard(ov_leave=True, claim="freeroute")
        self.assertIn("key pick", str(ctx.exception))

    def test_ungated_host_refuses(self) -> None:
        with self.assertRaises(SwitchyardDenied) as ctx:
            host_switchyard(ov_leave=False)
        self.assertIn("OpenVault", str(ctx.exception))

    def test_leave_machine_host_is_still_two_of_ten(self) -> None:
        out = host_switchyard(ov_leave=True)
        self.assertEqual(out["status"], "hosted")
        self.assertEqual(out["via"], "openvault")
        self.assertEqual(out["score"], "2/10")
        self.assertEqual(out["license"], "Apache-2.0")

    def test_host_ov_posts_skill_ids(self) -> None:
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
        with self.assertRaises(SwitchyardDenied) as missing:
            host_switchyard(ov_leave=False, ov=ov)
        self.assertIn("parent and child", str(missing.exception))
        self.assertEqual(seen, [])
        out = host_switchyard(
            ov_leave=False,
            ov=ov,
            parent_run_id="p1",
            child_id="sy",
        )
        self.assertEqual(out["score"], "2/10")
        self.assertEqual(seen[0]["skill_ids"], ["S-0004"])
        self.assertEqual(seen[0]["id"], "switchyard")
        self.assertNotIn("skill_body", str(seen[0]))
        blocked = OpenVaultCrewGate("http://127.0.0.1:5000", post=deny)
        with self.assertRaises(SwitchyardDenied) as ctx:
            host_switchyard(
                ov_leave=False,
                ov=blocked,
                parent_run_id="p1",
                child_id="sy",
            )
        self.assertIn("vault miss", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
