#!/usr/bin/env python3
"""Deep Agents sits under the wrap. python3 scripts/test_crew_deepagents.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crew_deepagents import bind_deep_agent, bind_kwargs, crew_harness_profile
from crew_tool_wrap import CortexDenied, Verdict


class FakeGate:
    def __init__(self) -> None:
        self.executed: list[str] = []

    def check(self, tool: str, payload: dict[str, Any]) -> Verdict:
        return Verdict(allowed=True)

    def execute(self, tool: str, payload: dict[str, Any]) -> Any:
        self.executed.append(tool)
        return {"ok": True, "tool": tool}


class CrewDeepAgentsTests(unittest.TestCase):
    def test_bind_kwargs_are_wrapped_only(self) -> None:
        kw = bind_kwargs(FakeGate(), ["export_pptx"], model="openai:gpt-4")
        self.assertEqual(len(kw["tools"]), 1)
        self.assertIs(kw["checkpointer"], False)
        self.assertIsNone(kw["subagents"])
        self.assertIsNone(kw["skills"])
        self.assertIsNone(kw["memory"])

    def test_bare_model_refuses(self) -> None:
        with self.assertRaises(CortexDenied) as ctx:
            bind_kwargs(FakeGate(), ["export_pptx"], model="gpt-4")
        self.assertIn("model spec", str(ctx.exception))

    def test_factory_skills_refuse(self) -> None:
        def factory(**_k: Any) -> str:
            return "nope"

        with self.assertRaises(CortexDenied) as ctx:
            bind_deep_agent(
                FakeGate(),
                ["export_pptx"],
                model="openai:gpt-4",
                factory=factory,
                extra={"skills": ["/tmp/skill.md"]},
            )
        self.assertIn("skills", str(ctx.exception))

    def test_factory_memory_refuses(self) -> None:
        def factory(**_k: Any) -> str:
            return "nope"

        with self.assertRaises(CortexDenied):
            bind_deep_agent(
                FakeGate(),
                ["export_pptx"],
                model="openai:gpt-4",
                factory=factory,
                extra={"memory": ["/memories"]},
            )

    def test_factory_subagents_refuse(self) -> None:
        def factory(**_k: Any) -> str:
            return "nope"

        with self.assertRaises(CortexDenied) as ctx:
            bind_deep_agent(
                FakeGate(),
                ["export_pptx"],
                model="openai:gpt-4",
                factory=factory,
                extra={"subagents": [{"name": "x"}]},
            )
        self.assertIn("subagents", str(ctx.exception))

    def test_injected_factory_gets_wrapped_tools(self) -> None:
        seen: dict[str, Any] = {}

        def factory(**kw: Any) -> str:
            seen.update(kw)
            return "agent"

        out = bind_deep_agent(
            FakeGate(),
            ["export_pptx"],
            model="openai:gpt-4",
            factory=factory,
        )
        self.assertEqual(out, "agent")
        self.assertEqual(len(seen["tools"]), 1)
        self.assertIs(seen["checkpointer"], False)
        self.assertIsNone(seen["subagents"])

    def test_profile_excludes_builtins_when_installed(self) -> None:
        try:
            profile = crew_harness_profile()
        except CortexDenied:
            self.skipTest("deepagents not installed")
        excluded = set(profile.excluded_tools)
        for name in ("task", "ls", "glob", "grep", "delete", "execute", "write_todos"):
            self.assertIn(name, excluded)
        self.assertIs(profile.general_purpose_subagent.enabled, False)


if __name__ == "__main__":
    unittest.main()
