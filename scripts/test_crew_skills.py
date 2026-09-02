#!/usr/bin/env python3
"""Skill kind needs a registry row. python3 scripts/test_crew_skills.py"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crew_ov_gate import OpenVaultCrewGate, refuse_crew_gate
from crew_runs import CrewGraph
from crew_skills import SkillDenied, SkillRegistry, register_skill
from crew_tool_wrap import CortexDenied


def _allow(url: str, body: dict[str, Any]) -> dict[str, Any]:
    return {"allowed": True, "found": True, "parent_run_id": body["parent_run_id"]}


class CrewSkillTests(unittest.TestCase):
    def test_register_is_ids_only(self) -> None:
        reg = SkillRegistry()
        register_skill(reg, "netie-kb.export-pptx")
        self.assertTrue(reg.has("netie-kb.export-pptx"))
        dumped = json.dumps(reg.index())
        self.assertIn("netie-kb.export-pptx", dumped)
        self.assertNotIn("skill_body", dumped)
        with self.assertRaises(SkillDenied):
            register_skill(reg, "x", skill_body="SECRET")
        with self.assertRaises(SkillDenied):
            register_skill(reg, "")

    def test_skill_kind_needs_a_row(self) -> None:
        with self.assertRaises(CortexDenied) as ctx:
            refuse_crew_gate(kind="skill", id="netie-kb.export-pptx")
        self.assertIn("no skill registered", str(ctx.exception))
        reg = SkillRegistry()
        register_skill(reg, "netie-kb.export-pptx")
        ok = refuse_crew_gate(
            kind="skill", id="netie-kb.export-pptx", registry=reg
        )
        self.assertEqual(ok["status"], "ok")
        with self.assertRaises(CortexDenied):
            refuse_crew_gate(
                kind="skill",
                id="netie-kb.export-pptx",
                registry=reg,
                skill_body="SECRET",
            )

    def test_spawn_skill_after_register(self) -> None:
        reg = SkillRegistry()
        register_skill(reg, "netie-kb.export-pptx")
        g = CrewGraph(
            ov=OpenVaultCrewGate(
                "http://127.0.0.1:5000", post=_allow, registry=reg
            )
        )
        g.open_parent("p1", "T1")
        child = g.spawn_child(
            parent_id="p1",
            child_id="c1",
            deficit="need export",
            kind="skill",
            resource_id="netie-kb.export-pptx",
        )
        self.assertEqual(child.id, "c1")
        missing = CrewGraph(
            ov=OpenVaultCrewGate("http://127.0.0.1:5000", post=_allow)
        )
        missing.open_parent("p1", "T1")
        with self.assertRaises(CortexDenied):
            missing.spawn_child(
                parent_id="p1",
                child_id="c1",
                deficit="need export",
                kind="skill",
                resource_id="netie-kb.export-pptx",
            )


if __name__ == "__main__":
    unittest.main()
