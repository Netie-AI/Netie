#!/usr/bin/env python3
"""Deep Agents sits under the wrap. python3 scripts/test_crew_deepagents.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crew_budget import TokenBudget
from crew_deepagents import (
    FORBIDDEN_FACTORY_KEYS,
    bind_deep_agent,
    bind_kwargs,
    crew_harness_profile,
)
from crew_tool_wrap import CortexDenied, Verdict


ROOM = TokenBudget(max_tokens=10_000)


class FakeGate:
    def __init__(self) -> None:
        self.executed: list[str] = []

    def check(self, tool: str, payload: dict[str, Any]) -> Verdict:
        return Verdict(allowed=True)

    def execute(self, tool: str, payload: dict[str, Any]) -> Any:
        self.executed.append(tool)
        return {"ok": True, "tool": tool}


class CrewDeepAgentsTests(unittest.TestCase):
    def test_forbidden_covers_prompt_and_filesystem_knobs(self) -> None:
        for name in ("system_prompt", "middleware", "backend", "permissions", "skills"):
            self.assertIn(name, FORBIDDEN_FACTORY_KEYS)
        kw = bind_kwargs(
            FakeGate(), ["export_pptx"], model="openai:gpt-4", budget=ROOM
        )
        self.assertEqual(len(kw["tools"]), 1)
        self.assertIs(kw["checkpointer"], False)
        self.assertIsNone(kw["subagents"])
        self.assertIsNone(kw["skills"])
        self.assertIsNone(kw["memory"])
        self.assertIsNone(kw["system_prompt"])
        self.assertEqual(kw["middleware"], ())
        self.assertIsNone(kw["backend"])
        self.assertIsNone(kw["permissions"])

    def test_bare_model_refuses(self) -> None:
        with self.assertRaises(CortexDenied) as ctx:
            bind_kwargs(FakeGate(), ["export_pptx"], model="gpt-4", budget=ROOM)
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

    def test_factory_system_prompt_refuses(self) -> None:
        def factory(**_k: Any) -> str:
            return "nope"

        with self.assertRaises(CortexDenied) as ctx:
            bind_deep_agent(
                FakeGate(),
                ["export_pptx"],
                model="openai:gpt-4",
                factory=factory,
                extra={"system_prompt": "SECRET skill body"},
            )
        self.assertIn("system_prompt", str(ctx.exception))

    def test_factory_middleware_refuses(self) -> None:
        def factory(**_k: Any) -> str:
            return "nope"

        with self.assertRaises(CortexDenied) as ctx:
            bind_deep_agent(
                FakeGate(),
                ["export_pptx"],
                model="openai:gpt-4",
                factory=factory,
                extra={"middleware": ["filesystem"]},
            )
        self.assertIn("middleware", str(ctx.exception))

    def test_factory_backend_refuses(self) -> None:
        def factory(**_k: Any) -> str:
            return "nope"

        with self.assertRaises(CortexDenied) as ctx:
            bind_deep_agent(
                FakeGate(),
                ["export_pptx"],
                model="openai:gpt-4",
                factory=factory,
                extra={"backend": "local"},
            )
        self.assertIn("backend", str(ctx.exception))

    def test_factory_response_format_and_debug_refuse(self) -> None:
        def factory(**_k: Any) -> str:
            return "nope"

        with self.assertRaises(CortexDenied) as ctx:
            bind_deep_agent(
                FakeGate(),
                ["export_pptx"],
                model="openai:gpt-4",
                factory=factory,
                extra={"response_format": {"type": "json"}},
            )
        self.assertIn("response_format", str(ctx.exception))
        self.assertIn("response_format", FORBIDDEN_FACTORY_KEYS)
        self.assertIn("debug", FORBIDDEN_FACTORY_KEYS)
        with self.assertRaises(CortexDenied) as ctx:
            bind_deep_agent(
                FakeGate(),
                ["export_pptx"],
                model="openai:gpt-4",
                factory=factory,
                extra={"debug": True},
            )
        self.assertIn("debug", str(ctx.exception))

    def test_bind_without_budget_refuses(self) -> None:
        def factory(**_k: Any) -> str:
            return "nope"

        with self.assertRaises(CortexDenied) as ctx:
            bind_deep_agent(
                FakeGate(),
                ["export_pptx"],
                model="openai:gpt-4",
                factory=factory,
                register=lambda *_a: None,
            )
        self.assertIn("token budget", str(ctx.exception))

    def test_injected_factory_without_register_refuses(self) -> None:
        def factory(**_k: Any) -> str:
            return "nope"

        with self.assertRaises(CortexDenied) as ctx:
            bind_deep_agent(
                FakeGate(),
                ["export_pptx"],
                model="openai:gpt-4",
                factory=factory,
                budget=ROOM,
            )
        self.assertIn("harness register", str(ctx.exception))

    def test_injected_factory_gets_wrapped_tools(self) -> None:
        try:
            crew_harness_profile()
        except CortexDenied:
            self.skipTest("deepagents not installed")
        seen: dict[str, Any] = {}

        def factory(**kw: Any) -> str:
            seen.update(kw)
            return "agent"

        def register(spec: str, profile: Any) -> None:
            seen.setdefault("profiles", {})[spec] = profile

        out = bind_deep_agent(
            FakeGate(),
            ["export_pptx"],
            model="openai:gpt-4",
            factory=factory,
            register=register,
            budget=ROOM,
        )
        self.assertEqual(out, "agent")
        self.assertEqual(len(seen["tools"]), 1)
        self.assertIs(seen["checkpointer"], False)
        self.assertIsNone(seen["subagents"])
        self.assertIsNone(seen["system_prompt"])
        self.assertEqual(seen["middleware"], ())
        profile = seen["profiles"]["openai:gpt-4"]
        excluded = set(profile.excluded_tools)
        for name in ("task", "ls", "execute", "read_file"):
            self.assertIn(name, excluded)
        self.assertIn("SummarizationMiddleware", set(profile.excluded_middleware))
        self.assertIs(profile.general_purpose_subagent.enabled, False)

    def test_profile_excludes_builtins_when_installed(self) -> None:
        try:
            profile = crew_harness_profile()
        except CortexDenied:
            self.skipTest("deepagents not installed")
        excluded = set(profile.excluded_tools)
        for name in ("task", "ls", "glob", "grep", "delete", "execute", "write_todos"):
            self.assertIn(name, excluded)
        self.assertIn("SummarizationMiddleware", set(profile.excluded_middleware))
        self.assertIs(profile.general_purpose_subagent.enabled, False)


if __name__ == "__main__":
    unittest.main()
