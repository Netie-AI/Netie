from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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


class WindowsInputTests(unittest.TestCase):
    def test_unicode_and_hotkey_events(self) -> None:
        from pointer import windows_input as w

        pairs = w.unicode_keydown_up("A")
        self.assertEqual(pairs[0][1] & w.KEYEVENTF_UNICODE, w.KEYEVENTF_UNICODE)
        self.assertEqual(pairs[1][1] & w.KEYEVENTF_KEYUP, w.KEYEVENTF_KEYUP)
        hk = w.hotkey_press_release(["ctrl", "s"])
        self.assertEqual(hk[0][0], 0x11)
        self.assertEqual(hk[1][0], ord("S"))
        self.assertEqual(hk[-1][0], 0x11)
        self.assertEqual(hk[-1][1], w.KEYEVENTF_KEYUP)

    def test_move_skips_sync_when_already_there(self) -> None:
        from pointer.executor import Executor
        import tempfile
        from pathlib import Path

        class Fake(Executor):
            def mouse_location(self):
                return {"x": 10, "y": 20, "screen": 0}

        with tempfile.TemporaryDirectory() as td:
            ex = Fake(display=":1", screenshot_dir=Path(td))
            out = ex.move(10, 20)
        self.assertEqual(out["actual"]["x"], 10)

    def test_screenshot_script_quotes_path(self) -> None:
        from pointer import windows_input as w

        script = w.screenshot_powershell(r"C:\Users\x\shot.png")
        self.assertIn("CopyFromScreen", script)
        self.assertIn(r"C:\Users\x\shot.png", script)
        self.assertNotIn("windows screenshot is not wired", script)

    def test_refuses_unknown_hotkey(self) -> None:
        from pointer import windows_input as w

        with self.assertRaises(ValueError):
            w.vk_code("not-a-key")


class PayPageTests(unittest.TestCase):
    def test_live_stripe_links_present(self) -> None:
        html = (Path(__file__).resolve().parents[1] / "pay" / "index.html").read_text(encoding="utf-8")
        for url in (
            "https://buy.stripe.com/dRmaEXchg7Wr7nS8D29ws08",
            "https://buy.stripe.com/dRm8wP3KKfoT9w0g5u9ws03",
            "https://buy.stripe.com/fZu3cvdlkb8D4bG5qQ9ws04",
            "https://buy.stripe.com/3cIcN54OO6SnaA4g5u9ws07",
            "https://buy.stripe.com/5kQ14nepo3Gb37C9H69ws06",
            "https://donate.stripe.com/aFa14n8104KfcIc9H69ws05",
        ):
            self.assertIn(url, html)
        self.assertIn("Payouts to Bank Islam are blocked", html)
        self.assertIn("https://docs.google.com/document/d/1h7H6thuUqyD71MlDyQd0Vbey5ucO30JGM1sSZ_mN4nI/edit", html)
        self.assertIn("https://hackerone.com/opportunities/all", html)
        self.assertIn("https://app.outlier.ai/", html)
        self.assertIn("pointer-rm300.png", html)
        self.assertIn("https://drive.google.com/file/d/12HUn5z1C62HwMp144kB_-wvnBom4XIke/view", html)
        self.assertIn("FIVERR_GIG.md", html)
        self.assertIn("https://docs.google.com/document/d/1CIfusgZvh8yXwucboi1iYpdMhgFHEyFlWEqjY4U_fIs/edit", html)
        self.assertIn("https://docs.google.com/document/d/1n5htCeuadHZsU7udormJGiAh-EmigBj3izXWR4NUMD4/edit", html)
        self.assertIn("HACKERONE.md", html)
        self.assertIn("https://litter.catbox.moe/67z3ik.html", html)
        self.assertIn("https://telegra.ph/Netie-pay-08-22", html)
        self.assertIn("web.archive.org/web/20260822131625", html)
        self.assertNotIn("edit.telegra.ph/auth", html)
        self.assertIn("https://docs.google.com/document/d/16kmarL_ZW48KYA0uvQW51-JvwnB7yyKB9ZabmTNoSoA/edit", html)
        self.assertIn("CRADLE_SPARK.md", html)
        self.assertIn("https://docs.google.com/document/d/1by_5VEBbQpD86So-q6K8F2T2MpcHWNkd4BKb4UlARI0/edit", html)
        self.assertIn("175ocCJoFFaXbbKkHKNyvw0w6AkwEiaix1D527Qf-8Oo", html)
        self.assertIn("STRIPE_PAYOUTS.md", html)
        self.assertIn("dashboard.stripe.com/settings/update", html)
        self.assertIn("1hP52Fun6L1LQEsxdgU-1E-f60yhXJ45He69tt7WrT4o", html)
        self.assertIn("FORHIRE.md", html)
        self.assertIn("1k0aHSZTRYeilXjc4CK4AbiyA7sXor2qTusYhg-oRLc4", html)
        self.assertIn("BUGCROWD.md", html)
        self.assertIn("1P3E2rf1NSnNUrf454YB6dL5P34ObNv3PmICVu1yb59Y", html)
        self.assertIn("AGENTIC_HACK.md", html)
        self.assertIn("hackathon/README.md", html)
        self.assertIn("gemini_planner.py", html)
        self.assertIn("forms.gle/riGhgDSHkHeMx8Ca6", html)
        self.assertIn("cannot auto-join", html)
        self.assertIn("AGENTIC_DEMO.md", html)
        self.assertIn("1BE_tt-bZB47vTRJsDgHHJsLMlXEz-dcpvP1cDz3L8uo", html)
        self.assertIn("YC_FALL_2026.md", html)
        self.assertIn("1QM46jy2SNF23oosjQSa8CakDfdGCZu5r-r_oANhp0QM", html)
        self.assertIn("ycombinator.com/apply", html)
        self.assertIn("AGENTIC_CINEMA.md", html)
        self.assertIn("11CCnQ5coVVPbTZa-gsJJxbBvyttSCZKyy9i3RiwdkPY", html)
        self.assertIn("agentic-cinema.devpost.com", html)
        self.assertNotIn("100K+", html)
        self.assertNotIn("030627070887", html)

    def test_forhire_pack_has_rate_and_seven_day_cap(self) -> None:
        text = (Path(__file__).resolve().parents[1] / "docs" / "FORHIRE.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("[For Hire]", text)
        self.assertIn("USD 70", text)
        self.assertIn("one post per 7 days", text)
        self.assertIn("1hP52Fun6L1LQEsxdgU-1E-f60yhXJ45He69tt7WrT4o", text)
        self.assertIn("100K downloads", text)
        self.assertIn("will not post to Reddit", text)

    def test_agentic_hack_pack_requires_gemini_and_forbids_false_traction(self) -> None:
        pack = (Path(__file__).resolve().parents[1] / "docs" / "AGENTIC_HACK.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("31 Aug 2026", pack)
        self.assertIn("Gemini 3.5", pack)
        self.assertIn("cannot submit", pack)
        self.assertIn("cannot auto-join or auto-win", pack)
        self.assertIn("A win is not confirmed", pack)
        self.assertIn("not part of this contest", pack)
        self.assertIn("does **not** satisfy", pack)
        self.assertIn("gemini_planner.py", pack)
        self.assertIn("hackathon/Dockerfile", pack)
        self.assertIn("1P3E2rf1NSnNUrf454YB6dL5P34ObNv3PmICVu1yb59Y", pack)
        self.assertIn("100K downloads", pack)
        self.assertIn("ycombinator.com/apply", pack)
        self.assertIn("Devpost login exists", pack)
        self.assertIn("forms.gle/riGhgDSHkHeMx8Ca6", pack)
        self.assertIn("AGENTIC_DEMO.md", pack)
        self.assertNotIn("we will win $1m", pack.lower())

    def test_agentic_demo_shot_list_is_honest(self) -> None:
        demo = (Path(__file__).resolve().parents[1] / "docs" / "AGENTIC_DEMO.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("4 minute", demo)
        self.assertIn("unedited", demo)
        self.assertIn("missing_gemini_key", demo)
        self.assertIn("1BE_tt-bZB47vTRJsDgHHJsLMlXEz-dcpvP1cDz3L8uo", demo)
        self.assertIn("Do not fake", demo)
        self.assertIn("100K downloads", demo)
        self.assertIn("A win is not confirmed", demo)
        self.assertNotIn("we will win $1m", demo.lower())

    def test_bugcrowd_pack_forbids_exploits(self) -> None:
        pack = (Path(__file__).resolve().parents[1] / "docs" / "BUGCROWD.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("will not write exploits", pack)
        self.assertIn("login.bugcrowd.com/signin/register", pack)
        self.assertIn("1k0aHSZTRYeilXjc4CK4AbiyA7sXor2qTusYhg-oRLc4", pack)
        self.assertIn("Do not test netie.ai", pack)
        self.assertIn("engagements/tesla", pack)

    def test_stripe_payouts_pack_has_dashboard_and_no_nric(self) -> None:
        text = (Path(__file__).resolve().parents[1] / "docs" / "STRIPE_PAYOUTS.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Do not send NRIC", text)
        self.assertIn("payouts_enabled", text)
        self.assertIn("dashboard.stripe.com/settings/update", text)
        self.assertNotIn("030627070887", text)

    def test_cradle_pack_forbids_false_traction(self) -> None:
        pack = (Path(__file__).resolve().parents[1] / "docs" / "CRADLE_SPARK.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("gms.cradle.com.my", pack)
        self.assertIn("16kmarL_ZW48KYA0uvQW51-JvwnB7yyKB9ZabmTNoSoA", pack)
        self.assertIn("100K+ Downloads", pack)
        self.assertIn("MYR 0, 0 charges", pack)
        self.assertIn("Second teammate is not named", pack)

    def test_hackerone_pack_forbids_exploits(self) -> None:
        pack = (Path(__file__).resolve().parents[1] / "docs" / "HACKERONE.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("will not write exploits", pack)
        self.assertIn("https://hackerone.com/users/sign_up", pack)
        self.assertIn("1n5htCeuadHZsU7udormJGiAh-EmigBj3izXWR4NUMD4", pack)
        self.assertIn("Do not test netie.ai", pack)

    def test_fiverr_pack_forbids_false_traction(self) -> None:
        pack = (Path(__file__).resolve().parents[1] / "docs" / "FIVERR_GIG.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("USD 70", pack)
        self.assertIn("Do not also collect Stripe", pack)
        self.assertIn("100K downloads", pack)
        self.assertIn("false vs Stripe", pack)
        self.assertIn("1CIfusgZvh8yXwucboi1iYpdMhgFHEyFlWEqjY4U_fIs", pack)


class PayRouteTests(unittest.TestCase):
    def test_pay_page_path_is_the_html_file(self) -> None:
        from pointer.server import pay_page_path, pay_qr_path

        p = pay_page_path()
        self.assertTrue(p.is_file())
        self.assertEqual(p.name, "index.html")
        self.assertIn("buy.stripe.com", p.read_text(encoding="utf-8"))
        qr = pay_qr_path()
        self.assertTrue(qr.is_file())
        self.assertTrue(qr.read_bytes().startswith(b"\x89PNG"))

    def test_handler_serves_html_and_png(self) -> None:
        from pointer.server import PointerHandler

        self.assertTrue(callable(getattr(PointerHandler, "_html")))
        self.assertTrue(callable(getattr(PointerHandler, "_png")))


class PairCardTests(unittest.TestCase):
    def test_card_omits_tokens_until_show(self) -> None:
        from pointer.pair import laptop_next_steps, write_card

        steps = laptop_next_steps()
        self.assertEqual(len(steps), 5)
        self.assertTrue(any("pointer prove" in s for s in steps))
        self.assertTrue(any("POINTER_ALLOW_REMOTE" in s for s in steps))
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            text = write_card(state, show_tokens=False).read_text(encoding="utf-8")
            tokens = json.loads((state / "pair.json").read_text(encoding="utf-8"))
            self.assertIn("Do not email tokens", text)
            self.assertNotIn("\npair_token:", text)
            self.assertNotIn(tokens["pair_token"], text)
            shown = write_card(state, show_tokens=True).read_text(encoding="utf-8")
            self.assertIn(tokens["pair_token"], shown)
            hidden = write_card(state, show_tokens=False).read_text(encoding="utf-8")
            self.assertNotIn(tokens["pair_token"], hidden)
            nxt = (state / "POINTER_NEXT.txt").read_text(encoding="utf-8")
            self.assertIn("POINTER_PROVE.json", nxt)
            self.assertIn("open_revenue.ps1", nxt)
            self.assertNotIn(tokens["pair_token"], nxt)
            self.assertNotIn("approval_token:", nxt)

    def test_install_script_accepts_py_launcher(self) -> None:
        src = (Path(__file__).resolve().parents[1] / "scripts" / "install_windows.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn("Get-Command py", src)
        self.assertIn("POINTER_NEXT.txt", src)
        self.assertIn("POINTER_PROVE.json", src)
        self.assertIn("Start-Process", src)
        self.assertIn("http://127.0.0.1:7420/pay", src)
        self.assertIn("/select,", src)
        self.assertIn("CORTEX_URL", src)
        self.assertIn("mesh", src)
        self.assertIn("drive.google.com/drive/my-drive", src)
        self.assertIn("open_revenue.ps1", src)

    def test_open_revenue_script_has_five_cash_paths(self) -> None:
        src = (Path(__file__).resolve().parents[1] / "scripts" / "open_revenue.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn("aistudio.google.com/apikey", src)
        self.assertIn("allthingsagentichackathon.devpost.com", src)
        self.assertIn("forms.gle/riGhgDSHkHeMx8Ca6", src)
        self.assertIn("agentic-cinema.devpost.com", src)
        self.assertIn("ycombinator.com/apply", src)
        self.assertIn("hacker101.com", src)
        self.assertNotIn("POINTER_ALLOW_REMOTE=1", src)
        self.assertIn("Do not blast Easyway/Hengxing", src)
        self.assertIn("not a $1m claim", src.lower())
        self.assertIn("does not auto-join or auto-win", src)
        cmd = (Path(__file__).resolve().parents[1] / "scripts" / "install_windows.cmd").read_text(
            encoding="utf-8"
        )
        self.assertIn("install_windows.ps1", cmd)
        self.assertIn("ExecutionPolicy Bypass", cmd)
        self.assertIn("install_windows.cmd", (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8"))
        inst = (Path(__file__).resolve().parents[1] / "INSTALL.txt").read_text(encoding="utf-8")
        self.assertIn("install_windows.cmd", inst)
        self.assertIn("POINTER_ALLOW_REMOTE", inst)
        self.assertNotIn("pair_token", inst)

    def test_agentic_cinema_pack_is_new_project_and_honest(self) -> None:
        pack = (Path(__file__).resolve().parents[1] / "docs" / "AGENTIC_CINEMA.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("9 Sep 2026", pack)
        self.assertIn("agentic-cinema.devpost.com", pack)
        self.assertIn("cannot submit", pack)
        self.assertIn("modification of existing Pointer", pack)
        self.assertIn("100K downloads", pack)
        self.assertIn("7,500", pack)
        self.assertIn("11CCnQ5coVVPbTZa-gsJJxbBvyttSCZKyy9i3RiwdkPY", pack)
        self.assertNotIn("030627070887", pack)

    def test_live_click_uses_state_shots(self) -> None:
        src = (Path(__file__).resolve().parents[1] / "pointer" / "__main__.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("/tmp/pointer-live", src)
        self.assertIn('_state_dir() / "shots"', src)

    def test_laptop_root_html_has_steps_not_tokens(self) -> None:
        from pointer.server import laptop_root_html

        html = laptop_root_html().decode("utf-8")
        self.assertIn("pointer prove", html)
        self.assertIn("POINTER_ALLOW_REMOTE", html)
        self.assertIn("Drive My Drive", html)
        self.assertNotIn("pair_token:", html)


class ProveTests(unittest.TestCase):
    def test_prove_file_rejects_tokens(self) -> None:
        from pointer.prove import write_prove

        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            with self.assertRaises(ValueError):
                write_prove(state, {"ok": True, "pair_token": "secret"})
            path = write_prove(state, {"schema": "pointer.prove/v1", "ok": True, "platform": "test"})
            text = path.read_text(encoding="utf-8")
            self.assertIn("pointer.prove/v1", text)
            self.assertNotIn("pair_token", text)
            self.assertNotIn("approval_token", text)

    def test_prove_ok_needs_screenshot_bytes(self) -> None:
        from pointer.prove import prove_ok

        after = {"x": 220, "y": 180}
        self.assertTrue(prove_ok(after=after, target_x=220, target_y=180, shot_bytes=200))
        self.assertFalse(prove_ok(after=after, target_x=220, target_y=180, shot_bytes=0))
        self.assertFalse(prove_ok(after={"x": 1, "y": 1}, target_x=220, target_y=180, shot_bytes=200))

    def test_dpi_aware_skipped_off_windows(self) -> None:
        from pointer.windows_input import ensure_dpi_aware

        self.assertEqual(ensure_dpi_aware(), "skipped")


class GeminiPlannerTests(unittest.TestCase):
    def test_missing_key_is_fail_closed(self) -> None:
        from pointer.gemini_planner import PlannerError, plan

        with mock.patch.dict(
            os.environ, {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}, clear=False
        ):
            with self.assertRaises(PlannerError):
                plan("move to 220,180")

    def test_google_api_key_from_openvault_env(self) -> None:
        from pointer.gemini_planner import gemini_key_source, plan
        from pointer.protocol import SCHEMA

        good = {
            "schema": SCHEMA,
            "intent_id": "h-1",
            "source": "local-test",
            "goal": "move",
            "actions": [{"type": "move", "x": 220, "y": 180}],
        }
        with mock.patch.dict(
            os.environ, {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": "ov-google-key"}
        ):
            self.assertEqual(gemini_key_source()[1], "GOOGLE_API_KEY")
            with mock.patch("pointer.gemini_planner._generate", return_value=json.dumps(good)):
                out = plan("move")
        self.assertEqual(out["actions"][0]["type"], "move")

    def test_plan_validates_schema_and_refuses_shell(self) -> None:
        from pointer.gemini_planner import PlannerError, plan
        from pointer.protocol import SCHEMA

        good = {
            "schema": SCHEMA,
            "intent_id": "h-1",
            "source": "local-test",
            "goal": "move",
            "actions": [{"type": "move", "x": 220, "y": 180}, {"type": "perceive"}],
        }
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            with mock.patch("pointer.gemini_planner._generate", return_value=json.dumps(good)):
                out = plan("move")
        self.assertEqual(out["schema"], SCHEMA)
        self.assertEqual(out["actions"][0]["type"], "move")
        bad = dict(good)
        bad["actions"] = [{"type": "shell", "command": "rm -rf /"}]
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            with mock.patch("pointer.gemini_planner._generate", return_value=json.dumps(bad)):
                with self.assertRaises(PlannerError):
                    plan("hack")

    def test_hackathon_health_degraded_without_key(self) -> None:
        from hackathon.app import health

        with mock.patch.dict(
            os.environ, {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}, clear=False
        ):
            body = health()
        self.assertFalse(body["ok"])
        self.assertIn("missing_gemini_key", body["degraded"])
        self.assertIsNone(body["key_env"])

    def test_hackathon_dockerfile_copies_pointer(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "hackathon" / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("COPY pointer", text)
        self.assertIn("google-genai", (root / "hackathon" / "requirements.txt").read_text(encoding="utf-8"))
        readme = (root / "hackathon" / "README.md").read_text(encoding="utf-8")
        self.assertIn("POINTER_ALLOW_REMOTE stays unset", readme)
        self.assertIn("Cloud Run", readme)
        self.assertIn("GOOGLE_API_KEY", readme)
        self.assertIn("OpenVault", readme)


class MeshTests(unittest.TestCase):
    def test_defaults_disagree_on_cortex_port(self) -> None:
        from pointer import mesh

        self.assertIn(":8010", mesh.TAS_CORTEX_DEFAULT)
        self.assertIn(":8000", mesh.OPENVAULT_MESH_CORTEX_DEFAULT)
        self.assertIn(":5000", mesh.OPENVAULT_DEFAULT)
        self.assertEqual(mesh.OPENVAULT_GOOGLE_ENV, "GOOGLE_API_KEY")
        self.assertEqual(mesh.OPENVAULT_GOOGLE_PROVIDER, "google")
        self.assertFalse(mesh.report()["silent_port_remap"])
        self.assertFalse(mesh.report()["cortex_auto_ingests_pointer_intent"])
        self.assertNotIn("030627070887", Path(mesh.__file__).read_text(encoding="utf-8"))

    def test_gate_does_not_follow_openvault_mesh_port(self) -> None:
        import urllib.error

        from pointer import cortex_client, mesh

        class Resp:
            def __init__(self, status: int) -> None:
                self.status = status

            def __enter__(self) -> "Resp":
                return self

            def __exit__(self, *args: object) -> None:
                return None

            def read(self) -> bytes:
                return b"{}"

        def fake_open(url: str, timeout: float = 1.0):  # noqa: ARG001
            if ":8000" in url and url.rstrip("/").endswith("/health"):
                return Resp(200)
            raise urllib.error.URLError("down")

        env = {
            "CORTEX_URL": mesh.TAS_CORTEX_DEFAULT,
            "OPENVAULT_CORTEX_URL": mesh.OPENVAULT_MESH_CORTEX_DEFAULT,
            "OPENVAULT_URL": mesh.OPENVAULT_DEFAULT,
        }
        with mock.patch.dict(os.environ, env, clear=False):
            with mock.patch("urllib.request.urlopen", side_effect=fake_open):
                self.assertFalse(cortex_client.ping())
                rep = mesh.report()
        self.assertFalse(rep["cortex_tas"]["reachable"])
        self.assertTrue(rep["cortex_openvault_mesh"]["reachable"])
        self.assertIn("cortex_on_openvault_port_set_CORTEX_URL", rep["degraded"])
        self.assertFalse(rep["silent_port_remap"])

    def test_submit_intent_does_not_post_to_auto_route(self) -> None:
        from pointer import cortex_client

        self.assertFalse(cortex_client.CORTEX_AUTO_INGESTS_POINTER_INTENT)
        with mock.patch("urllib.request.urlopen") as opener:
            out = cortex_client.submit_intent({"schema": SCHEMA, "goal": "nope"})
        self.assertIsNone(out)
        opener.assert_not_called()


class YcPackTests(unittest.TestCase):
    def test_yc_pack_is_late_apply_and_honest(self) -> None:
        text = (Path(__file__).resolve().parents[1] / "docs" / "YC_FALL_2026.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("1QM46jy2SNF23oosjQSa8CakDfdGCZu5r-r_oANhp0QM", text)
        self.assertIn("ycombinator.com/apply", text)
        self.assertIn("late", text.lower())
        self.assertIn("cannot fill", text)
        self.assertIn("100K downloads", text)
        self.assertIn("Charges: 0", text)
        self.assertNotIn("030627070887", text)
        self.assertIn("Do not write", text)
        self.assertIn("$1M ARR", text)
        self.assertIn("YC_FALL_2026.md", (Path(__file__).resolve().parents[1] / "docs" / "ACTIVE.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
