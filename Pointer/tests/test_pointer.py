from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pointer.gate import Gate
from pointer.ledger import Ledger
from pointer.protocol import SCHEMA, Intent


def _intent(**kwargs) -> Intent:
    base = {
        "schema": SCHEMA,
        "intent_id": "it-1",
        "source": "human",
        "goal": "demo",
        "actions": [{"type": "perceive"}],
    }
    base.update(kwargs)
    return Intent.from_dict(base)


class LedgerTests(unittest.TestCase):
    def test_chain_detects_tamper(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.jsonl"
            led = Ledger(path)
            h1 = led.append({"n": 1})
            h2 = led.append({"n": 2})
            self.assertNotEqual(h1, h2)
            led.verify_chain()
            raw = path.read_text(encoding="utf-8").splitlines()
            row = json.loads(raw[0])
            row["event"]["n"] = 99
            raw[0] = json.dumps(row)
            path.write_text("\n".join(raw) + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                Ledger(path).verify_chain()


class GateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.gate = Gate(
            state_dir=Path(self.td.name),
            pair_token="pair",
            cortex_reachable=False,
            approval_token="approve",
        )

    def test_kill_switch_refuses(self) -> None:
        self.gate.arm_kill()
        d = self.gate.decide(_intent(), bearer=None, bind_is_loopback=True)
        self.assertFalse(d.allowed)
        self.assertEqual(d.verdict, "refused")

    def test_act_without_cortex_refuses_unless_explicit(self) -> None:
        intent = _intent(actions=[{"type": "click", "x": 1, "y": 1}])
        d = self.gate.decide(intent, bearer=None, bind_is_loopback=True)
        self.assertFalse(d.allowed)
        self.assertIn("Cortex is unreachable", d.reason)

        local = _intent(
            source="local-test",
            actions=[{"type": "click", "x": 1, "y": 1}],
        )
        d2 = self.gate.decide(local, bearer=None, bind_is_loopback=True)
        self.assertTrue(d2.allowed)
        self.assertIn("local_act_without_cortex", d2.degraded)

    def test_irreversible_needs_approval(self) -> None:
        intent = _intent(
            source="local-test",
            actions=[{"type": "file_delete", "path": "x.txt"}],
        )
        d = self.gate.decide(intent, bearer=None, bind_is_loopback=True)
        self.assertEqual(d.verdict, "needs_approval")
        approved = _intent(
            source="local-test",
            approval_token="approve",
            actions=[{"type": "file_delete", "path": "x.txt"}],
        )
        d2 = self.gate.decide(approved, bearer=None, bind_is_loopback=True)
        self.assertTrue(d2.allowed)

    def test_remote_act_needs_pair_and_approval(self) -> None:
        intent = _intent(
            source="remote-paired",
            actions=[{"type": "click", "x": 1, "y": 1}],
        )
        d = self.gate.decide(intent, bearer=None, bind_is_loopback=True)
        self.assertFalse(d.allowed)
        d2 = self.gate.decide(intent, bearer="pair", bind_is_loopback=True)
        self.assertEqual(d2.verdict, "needs_approval")
        ok = _intent(
            source="remote-paired",
            approval_token="approve",
            actions=[{"type": "click", "x": 1, "y": 1}],
            allow_local_act=True,
        )
        d3 = self.gate.decide(ok, bearer="pair", bind_is_loopback=True)
        self.assertTrue(d3.allowed)

    def test_remote_perceive_with_pair_ok(self) -> None:
        intent = _intent(source="remote-paired", actions=[{"type": "perceive"}])
        d = self.gate.decide(intent, bearer="pair", bind_is_loopback=True)
        self.assertTrue(d.allowed)

    def test_bad_schema_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Intent.from_dict(
                {
                    "schema": "nope",
                    "intent_id": "x",
                    "source": "human",
                    "goal": "g",
                    "actions": [{"type": "perceive"}],
                }
            )


class SandboxEngineTests(unittest.TestCase):
    def test_file_write_stays_in_sandbox(self) -> None:
        from pointer.engine import Engine
        from pointer.executor import ExecutorError

        class DummyExec:
            def mouse_location(self):
                return {"x": 0, "y": 0}

            def screenshot(self, name: str):
                raise ExecutorError("no screen")

        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            eng = Engine(
                state_dir=state,
                pair_token="p",
                approval_token="a",
                bind_is_loopback=True,
                executor=DummyExec(),  # type: ignore[arg-type]
            )
            escaped = eng._run_action(
                Intent.from_dict(
                    {
                        "schema": SCHEMA,
                        "intent_id": "i",
                        "source": "local-test",
                        "goal": "g",
                        "approval_token": "a",
                        "actions": [{"type": "file_write", "path": "../escape.txt", "content": "nope"}],
                    }
                ).actions[0]
            )[0]
            self.assertTrue(escaped.ok)
            written = list((state / "sandbox").glob("*"))
            self.assertEqual(len(written), 1)
            self.assertEqual(written[0].name, "escape.txt")
            self.assertFalse((state / "escape.txt").exists())


if __name__ == "__main__":
    unittest.main()
