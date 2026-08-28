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


if __name__ == "__main__":
    unittest.main()
