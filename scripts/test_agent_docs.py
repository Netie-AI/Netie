#!/usr/bin/env python3
"""Agent docs stay a pointer plus the constitution. python3 scripts/test_agent_docs.py"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AgentDocTests(unittest.TestCase):
    def test_agents_is_a_pointer(self) -> None:
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        lines = [ln for ln in text.splitlines() if ln.strip()]
        self.assertLessEqual(len(lines), 12)
        self.assertIn("CLAUDE.md", text)
        self.assertIn("NETIE.md", text)
        self.assertIn("NETIE.md` wins", text)
        self.assertIn("Do not vendor", text)
        self.assertIn("make ci", text)

    def test_claude_binds_reuse_to_the_constitution(self) -> None:
        text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        for needle in (
            "does not amend `NETIE.md`",
            "Classify every external project",
            "Do not copy the tree",
            "no SPDX license",
            "Constructor",
            "not n8n",
            "Control",
            "board view",
            "Deep Agents",
            "does not mean removing copyright",
            "make ci",
            "two epics",
        ):
            self.assertIn(needle, text, needle)

    def test_readme_matches_this_repo(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for needle in (
            "accountable enough to run a business on",
            "portable contracts",
            "does not vendor",
            "NETIE.md` wins",
            "TAS/ESTATE-GAP.md",
            "uv add git+https://github.com/Netie-AI/Netie.git",
            "Do not `uv add` this package into Cortex",
            "MIT",
            "make ci",
        ):
            self.assertIn(needle, text, needle)
        self.assertNotIn("sub-millisecond", text.lower())
        self.assertNotIn("clone and rebrand", text.lower())

    def test_docs_do_not_authorize_a_clone_program(self) -> None:
        blob = "\n".join(
            (ROOT / name).read_text(encoding="utf-8")
            for name in ("AGENTS.md", "CLAUDE.md", "README.md")
        ).lower()
        for banned in (
            "sub-millisecond",
            "clone and rebrand",
            "ready to sell",
            "slap a netie logo",
            "fork n8n",
            "vendor omnroute",
        ):
            self.assertNotIn(banned, blob, banned)


if __name__ == "__main__":
    unittest.main()
