#!/usr/bin/env python3
"""Execution shapes, not sorts. python3 scripts/test_freeroute_execution.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from freeroute_execution import (
    EXECUTION_SHAPES,
    FUSION_MAX_PANEL,
    HANDOFF_EXHAUSTION,
    PipelineStep,
    RelayHandoff,
    RelayStore,
    StrategyIsASort,
    StrategyNotASort,
    ExecutionRefused,
    build_judge_prompt,
    chat_shape_refusal,
    combo_models_from_body,
    dispatch_combo,
    hops_for_model,
    hop_call_model,
    Hop,
    classify_hop_status,
    sse_wrap_text,
    relay_available_from_body,
    relay_handoff_from_body,
    remember_relay_handoff,
    resolve_relay_handoff,
    inject_handoff,
    pick_hop,
    pick_relay_target,
    plan_fusion,
    refuse_as_sort,
    resolve_auto,
    resolve_handoff_providers,
    run_fusion,
    run_pipeline,
    shape_from_chat_body,
    should_generate_handoff,
)


class RefuseAsSortTests(unittest.TestCase):
    def test_four_shapes_raise(self) -> None:
        for name in EXECUTION_SHAPES:
            with self.assertRaises(StrategyNotASort):
                refuse_as_sort(name)
            with self.assertRaises(StrategyNotASort):
                refuse_as_sort(name.replace("-", "_"))

    def test_sort_names_pass(self) -> None:
        refuse_as_sort("cache-optimized")
        refuse_as_sort("priority")


class FusionTests(unittest.TestCase):
    def test_empty_panel_400(self) -> None:
        with self.assertRaises(ExecutionRefused) as ctx:
            plan_fusion([])
        self.assertEqual(ctx.exception.code, 400)

    def test_single_model_is_direct(self) -> None:
        plan = plan_fusion(["p/only"])
        self.assertEqual(plan.mode, "direct")
        self.assertEqual(plan.judge, "p/only")

    def test_default_judge_is_first_panel(self) -> None:
        plan = plan_fusion(["p/a", "p/b"])
        self.assertEqual(plan.mode, "fanout")
        self.assertEqual(plan.judge, "p/a")
        self.assertFalse(plan.explicit_judge)

    def test_explicit_judge(self) -> None:
        plan = plan_fusion(["p/a", "p/b"], judge_model="p/judge")
        self.assertEqual(plan.judge, "p/judge")
        self.assertTrue(plan.explicit_judge)

    def test_oversized_panel_400(self) -> None:
        models = [f"p/{i}" for i in range(FUSION_MAX_PANEL + 1)]
        with self.assertRaises(ExecutionRefused) as ctx:
            plan_fusion(models)
        self.assertEqual(ctx.exception.code, 400)

    def test_tool_bearing_bypasses_fanout(self) -> None:
        plan = plan_fusion(
            ["p/a", "p/b"],
            judge_model="p/judge",
            tools=[{"name": "x"}],
        )
        self.assertEqual(plan.mode, "direct")
        self.assertTrue(plan.tool_bearing)

    def test_tool_choice_none_still_fans_out(self) -> None:
        plan = plan_fusion(
            ["p/a", "p/b"],
            tools=[{"name": "x"}],
            tool_choice="none",
        )
        self.assertEqual(plan.mode, "fanout")

    def test_run_fans_out_then_judge_with_source_n(self) -> None:
        seen: list[tuple[str, bool, object]] = []

        def call(model, *, user_text, stream, tools, tool_choice, **_k):
            seen.append((model, stream, tools))
            if model == "p/judge":
                self.assertIn("[Source 1]", user_text)
                self.assertIn("[Source 2]", user_text)
                self.assertIn("ans-a", user_text)
                return "FINAL"
            return f"ans-{model[-1]}"

        plan = plan_fusion(["p/a", "p/b"], judge_model="p/judge")
        out = run_fusion(plan, call, user_text="Q", stream=True, tools=[{"name": "x"}])
        self.assertEqual(out, "FINAL")
        self.assertEqual([row[0] for row in seen], ["p/a", "p/b", "p/judge"])
        self.assertFalse(seen[0][1])
        self.assertIsNone(seen[0][2])
        self.assertTrue(seen[2][1])
        self.assertEqual(seen[2][2], [{"name": "x"}])

    def test_run_one_survivor_no_explicit_judge_skips_synthesis(self) -> None:
        def call(model, **_k):
            return "only" if model == "p/a" else ""

        plan = plan_fusion(["p/a", "p/b"])
        self.assertEqual(run_fusion(plan, call, user_text="Q"), "only")

    def test_run_zero_answers_503(self) -> None:
        def call(_model, **_k):
            return ""

        plan = plan_fusion(["p/a", "p/b"])
        with self.assertRaises(ExecutionRefused) as ctx:
            run_fusion(plan, call, user_text="Q")
        self.assertEqual(ctx.exception.code, 503)

    def test_judge_prompt_anonymizes(self) -> None:
        text = build_judge_prompt(["alpha", "beta"])
        self.assertIn("[Source 1]", text)
        self.assertIn("[Source 2]", text)
        self.assertNotIn("p/a", text)


class PipelineTests(unittest.TestCase):
    def test_empty_400(self) -> None:
        with self.assertRaises(ExecutionRefused) as ctx:
            run_pipeline([], lambda *_a, **_k: "x", user_text="hi")
        self.assertEqual(ctx.exception.code, 400)

    def test_two_steps_thread_output(self) -> None:
        seen: list[tuple[str, str, bool, object, str | None]] = []

        def call(model, *, user_text, stream, tools, tool_choice, system=None):
            seen.append((model, user_text, stream, tools, system))
            if model == "p/a":
                return "OUT_A"
            return "FINAL_B"

        out = run_pipeline(
            [PipelineStep("p/a"), PipelineStep("p/b", prompt="SUMMARIZE")],
            call,
            user_text="hi",
            stream=True,
            tools=[{"name": "x"}],
        )
        self.assertEqual(out, "FINAL_B")
        self.assertEqual(seen[0][0], "p/a")
        self.assertEqual(seen[0][1], "hi")
        self.assertFalse(seen[0][2])
        self.assertIsNone(seen[0][3])
        self.assertEqual(seen[1][0], "p/b")
        self.assertEqual(seen[1][1], "OUT_A")
        self.assertTrue(seen[1][2])
        self.assertEqual(seen[1][3], [{"name": "x"}])
        self.assertEqual(seen[1][4], "SUMMARIZE")

    def test_skips_hidden(self) -> None:
        seen: list[str] = []

        def call(model, **_k):
            seen.append(model)
            return f"out-{model}"

        out = run_pipeline(
            [
                PipelineStep("p/a"),
                PipelineStep("p/hidden", hidden=True),
                PipelineStep("p/b"),
            ],
            call,
            user_text="hi",
        )
        self.assertEqual(seen, ["p/a", "p/b"])
        self.assertEqual(out, "out-p/b")

    def test_empty_intermediate_fails_chain(self) -> None:
        def call(model, **_k):
            return "" if model == "p/a" else "ok"

        with self.assertRaises(ExecutionRefused) as ctx:
            run_pipeline(
                [PipelineStep("p/a"), PipelineStep("p/b")],
                call,
                user_text="hi",
            )
        self.assertEqual(ctx.exception.code, 502)
        self.assertIn("p/a", str(ctx.exception))


class ContextRelayTests(unittest.TestCase):
    def test_first_available(self) -> None:
        self.assertEqual(
            pick_relay_target(["openai/a", "claude/b"]),
            "openai/a",
        )

    def test_skips_unavailable(self) -> None:
        self.assertEqual(
            pick_relay_target(
                ["codex/x", "openai/a"],
                available={"codex/x": False, "openai/a": True},
            ),
            "openai/a",
        )

    def test_all_unavailable_none(self) -> None:
        self.assertIsNone(
            pick_relay_target(["a", "b"], available={"a": False, "b": False})
        )

    def test_default_providers_codex(self) -> None:
        self.assertEqual(resolve_handoff_providers(None), ["codex"])

    def test_explicit_empty_disables(self) -> None:
        self.assertEqual(resolve_handoff_providers([]), [])
        self.assertFalse(
            should_generate_handoff(
                provider="codex",
                percent_used=0.9,
                handoff_providers=[],
                session_id="s",
                connection_id="c",
            )
        )

    def test_warning_band_only(self) -> None:
        common = dict(
            provider="codex",
            handoff_providers=["codex"],
            session_id="s",
            connection_id="c",
        )
        self.assertFalse(should_generate_handoff(percent_used=0.84, **common))
        self.assertTrue(should_generate_handoff(percent_used=0.85, **common))
        self.assertTrue(should_generate_handoff(percent_used=0.94, **common))
        self.assertFalse(
            should_generate_handoff(percent_used=HANDOFF_EXHAUSTION, **common)
        )

    def test_wrong_provider_skips(self) -> None:
        self.assertFalse(
            should_generate_handoff(
                provider="openai",
                percent_used=0.9,
                handoff_providers=["codex"],
                session_id="s",
                connection_id="c",
            )
        )

    def test_inject_prepends_blob(self) -> None:
        store = RelayStore()
        store.put(RelayHandoff("s", "combo", "keep going", "acct"))
        text = inject_handoff("hello", store.get("s", "combo"))
        self.assertTrue(text.startswith("<context_handoff>"))
        self.assertIn("keep going", text)
        self.assertTrue(text.endswith("hello"))


class AutoTests(unittest.TestCase):
    def test_missing_resolved_refuses(self) -> None:
        with self.assertRaises(ExecutionRefused) as ctx:
            resolve_auto(None)
        self.assertEqual(ctx.exception.code, 400)

    def test_resolves_to_sort(self) -> None:
        self.assertEqual(resolve_auto("cache-optimized"), "cache-optimized")
        self.assertEqual(resolve_auto("lkgp"), "lkgp")

    def test_cannot_resolve_to_execution_shape(self) -> None:
        for name in EXECUTION_SHAPES:
            with self.assertRaises(ExecutionRefused):
                resolve_auto(name)

    def test_unknown_refuses(self) -> None:
        with self.assertRaises(ExecutionRefused):
            resolve_auto("quota-share")


class DispatchTests(unittest.TestCase):
    def test_sort_name_is_not_a_dispatcher(self) -> None:
        with self.assertRaises(StrategyIsASort) as ctx:
            dispatch_combo("cache-optimized", ["a"], lambda *_a, **_k: "x")
        self.assertEqual(ctx.exception.strategy, "cache-optimized")

    def test_auto_without_resolved_refuses(self) -> None:
        with self.assertRaises(ExecutionRefused):
            dispatch_combo("auto", ["a"], lambda *_a, **_k: "x")

    def test_auto_with_resolved_is_a_sort(self) -> None:
        with self.assertRaises(StrategyIsASort) as ctx:
            dispatch_combo(
                "auto", ["a"], lambda *_a, **_k: "x", resolved="priority"
            )
        self.assertEqual(ctx.exception.strategy, "priority")

    def test_fusion_dispatch(self) -> None:
        seen: list[str] = []

        def call(model, **_k):
            seen.append(model)
            return f"ans-{model}"

        out = dispatch_combo(
            "fusion",
            ["p/a", "p/b"],
            call,
            user_text="Q",
            judge_model="p/judge",
        )
        self.assertEqual(seen[:2], ["p/a", "p/b"])
        self.assertEqual(seen[2], "p/judge")
        self.assertEqual(out, "ans-p/judge")

    def test_pipeline_dispatch_from_dicts(self) -> None:
        seen: list[str] = []

        def call(model, *, user_text, **_k):
            seen.append(model)
            return "OUT" if model == "p/a" else user_text + "-B"

        out = dispatch_combo(
            "pipeline",
            [{"model": "p/a"}, {"model": "p/b", "prompt": "SUMMARIZE"}],
            call,
            user_text="hi",
        )
        self.assertEqual(seen, ["p/a", "p/b"])
        self.assertEqual(out, "OUT-B")

    def test_relay_dispatch_skips_unavailable(self) -> None:
        def call(model, *, user_text, **_k):
            self.assertEqual(model, "openai/a")
            self.assertIn("keep going", user_text)
            return "ok"

        out = dispatch_combo(
            "context-relay",
            ["codex/x", "openai/a"],
            call,
            user_text="hello",
            available={"codex/x": False, "openai/a": True},
            handoff=RelayHandoff("s", "c", "keep going", "acct"),
        )
        self.assertEqual(out, "ok")


class ChatBodyTests(unittest.TestCase):
    def test_model_auto_is_not_omniroute_auto(self) -> None:
        self.assertIsNone(
            shape_from_chat_body(
                {"model": "auto", "messages": [{"role": "user", "content": "hi"}]}
            )
        )
        self.assertIsNone(chat_shape_refusal({"model": "auto"}))

    def test_model_fusion_is_a_shape(self) -> None:
        self.assertEqual(shape_from_chat_body({"model": "fusion"}), "fusion")
        payload = chat_shape_refusal({"model": "fusion"})
        assert payload is not None
        self.assertEqual(payload["error"]["type"], "openvault_execution_shape")

    def test_combo_auto_is_omniroute_auto(self) -> None:
        self.assertEqual(
            shape_from_chat_body({"model": "gpt-4", "combo": {"strategy": "auto"}}),
            "auto",
        )

    def test_body_strategy_pipeline(self) -> None:
        self.assertEqual(shape_from_chat_body({"strategy": "pipeline"}), "pipeline")

    def test_combo_models_skip_refusal(self) -> None:
        body = {
            "model": "auto",
            "combo": {"strategy": "fusion", "models": ["a", "b"]},
        }
        self.assertEqual(shape_from_chat_body(body), "fusion")
        self.assertIsNone(chat_shape_refusal(body))
        self.assertEqual(combo_models_from_body(body), ["a", "b"])

    def test_relay_available_from_combo(self) -> None:
        body = {
            "combo": {
                "strategy": "context-relay",
                "models": ["codex/x", "gpt-mini"],
                "available": {"codex/x": False, "gpt-mini": True},
            }
        }
        self.assertEqual(
            relay_available_from_body(body),
            {"codex/x": False, "gpt-mini": True},
        )
        self.assertIsNone(relay_available_from_body({"combo": {"strategy": "context-relay"}}))

    def test_relay_handoff_requires_session_and_summary(self) -> None:
        self.assertIsNone(
            relay_handoff_from_body({"combo": {"handoff": {"summary": "x"}}})
        )
        got = relay_handoff_from_body(
            {
                "combo": {
                    "handoff": {
                        "sessionId": "s1",
                        "summary": "keep going",
                        "fromAccount": "acct",
                    }
                }
            }
        )
        assert got is not None
        self.assertEqual(got.session_id, "s1")
        self.assertEqual(got.summary, "keep going")
        self.assertEqual(got.from_account, "acct")

    def test_stored_handoff_used_when_body_omits_blob(self) -> None:
        store = RelayStore()
        first = {
            "combo": {
                "strategy": "context-relay",
                "handoff": {
                    "sessionId": "s1",
                    "summary": "keep going",
                    "fromAccount": "acct",
                },
            }
        }
        caller = relay_handoff_from_body(first)
        remember_relay_handoff(store, caller)
        second = {
            "combo": {
                "strategy": "context-relay",
                "sessionId": "s1",
            }
        }
        got = resolve_relay_handoff(store, second)
        assert got is not None
        self.assertEqual(got.summary, "keep going")
        self.assertIsNone(relay_handoff_from_body(second))

    def test_caller_blob_wins_over_store(self) -> None:
        store = RelayStore()
        remember_relay_handoff(
            store, RelayHandoff("s1", "", "old summary", "acct")
        )
        body = {
            "combo": {
                "strategy": "context-relay",
                "sessionId": "s1",
                "handoff": {
                    "sessionId": "s1",
                    "summary": "new summary",
                },
            }
        }
        got = resolve_relay_handoff(store, body)
        assert got is not None
        self.assertEqual(got.summary, "new summary")

    def test_no_session_does_not_invent_a_handoff(self) -> None:
        store = RelayStore()
        remember_relay_handoff(
            store, RelayHandoff("s1", "", "keep going", "acct")
        )
        self.assertIsNone(
            resolve_relay_handoff(store, {"combo": {"strategy": "context-relay"}})
        )

    def test_relay_dispatch_all_unavailable_503(self) -> None:
        with self.assertRaises(ExecutionRefused) as ctx:
            dispatch_combo(
                "context-relay",
                ["a"],
                lambda *_a, **_k: "nope",
                available={"a": False},
            )
        self.assertEqual(ctx.exception.code, 503)


class HopWalkTests(unittest.TestCase):
    def test_picks_matching_model(self) -> None:
        hops = [
            Hop("k1", "gpt-mini", "openai", True),
            Hop("k2", "gpt-big", "openai", True),
        ]
        picked = pick_hop(hops, "gpt-big")
        assert picked is not None
        self.assertEqual(picked.execution_key, "k2")

    def test_skips_unhealthy(self) -> None:
        hops = [
            Hop("k1", "gpt-mini", "openai", False),
            Hop("k2", "gpt-mini", "openai", True),
        ]
        picked = pick_hop(hops, "gpt-mini")
        assert picked is not None
        self.assertEqual(picked.execution_key, "k2")

    def test_serves_callback(self) -> None:
        hops = [Hop("k1", "", "openai", True)]
        hop = pick_hop(hops, "gpt-4o", serves=lambda h, m: h.provider == "openai")
        assert hop is not None
        self.assertEqual(hop.execution_key, "k1")

    def test_call_model_posts_picked_hop(self) -> None:
        hops = [Hop("k1", "p/a", "openai", True), Hop("k2", "p/b", "openai", True)]
        seen: list[str] = []

        def post(hop: Hop, *, model: str, **_k: object) -> str:
            seen.append(f"{hop.execution_key}:{model}")
            return f"ans-{model}"

        call = hop_call_model(hops, post)
        self.assertEqual(call("p/b", user_text="Q"), "ans-p/b")
        self.assertEqual(seen, ["k2:p/b"])

    def test_missing_hop_returns_empty(self) -> None:
        call = hop_call_model([Hop("k1", "p/a", "openai", True)], lambda *_a, **_k: "x")
        self.assertEqual(call("p/missing", user_text="Q"), "")

    def test_empty_first_hop_falls_through(self) -> None:
        hops = [
            Hop("k1", "gpt-mini", "openai", True),
            Hop("k2", "gpt-mini", "openai", True),
        ]
        seen: list[str] = []

        def post(hop: Hop, *, model: str, **_k: object) -> str:
            seen.append(hop.execution_key)
            return "" if hop.execution_key == "k1" else "ok"

        call = hop_call_model(hops, post)
        self.assertEqual(call("gpt-mini", user_text="Q"), "ok")
        self.assertEqual(seen, ["k1", "k2"])

    def test_hops_for_model_lists_all_matches(self) -> None:
        hops = [
            Hop("k1", "gpt-mini", "openai", True),
            Hop("k2", "gpt-big", "openai", True),
            Hop("k3", "gpt-mini", "openai", True),
        ]
        keys = [h.execution_key for h in hops_for_model(hops, "gpt-mini")]
        self.assertEqual(keys, ["k1", "k3"])

    def test_job_dead_is_not_swallowed(self) -> None:
        hops = [
            Hop("k1", "gpt-mini", "openai", True),
            Hop("k2", "gpt-mini", "openai", True),
        ]

        def post(hop: Hop, *, model: str, **_k: object) -> str:
            raise ExecutionRefused(400, "request rejected by upstream (non-retryable)")

        call = hop_call_model(hops, post)
        with self.assertRaises(ExecutionRefused) as ctx:
            call("gpt-mini", user_text="Q")
        self.assertEqual(ctx.exception.code, 400)

    def test_anthropic_only_hops_name_the_skip(self) -> None:
        hops = [Hop("k1", "claude", "anthropic", True)]
        seen: list[str] = []

        def post(hop: Hop, *, model: str, **_k: object) -> str:
            seen.append(hop.execution_key)
            return "should-not-post"

        call = hop_call_model(hops, post)
        with self.assertRaises(ExecutionRefused) as ctx:
            call("claude", user_text="Q")
        self.assertEqual(ctx.exception.code, 503)
        self.assertIn("anthropic chat not via /v1 proxy yet", str(ctx.exception))
        self.assertEqual(seen, [])

    def test_anthropic_hop_is_skipped_when_openai_can_serve(self) -> None:
        hops = [
            Hop("k1", "gpt-mini", "anthropic", True),
            Hop("k2", "gpt-mini", "openai", True),
        ]
        seen: list[str] = []

        def post(hop: Hop, *, model: str, **_k: object) -> str:
            seen.append(hop.execution_key)
            return "ok"

        call = hop_call_model(hops, post)
        self.assertEqual(call("gpt-mini", user_text="Q"), "ok")
        self.assertEqual(seen, ["k2"])


class HopClassifyTests(unittest.TestCase):
    def test_success_keep(self) -> None:
        out = classify_hop_status(200)
        self.assertEqual(out.attempt_class, "success")
        self.assertEqual(out.job, "done")
        self.assertFalse(out.trip_provider_breaker)

    def test_429_parks_without_trip(self) -> None:
        out = classify_hop_status(429)
        self.assertEqual(out.attempt_class, "rate_limit")
        self.assertEqual(out.candidate, "park")
        self.assertEqual(out.job, "continue_chain")
        self.assertFalse(out.trip_provider_breaker)
        self.assertFalse(out.counts_as_hard_fail)

    def test_500_trips_and_continues(self) -> None:
        out = classify_hop_status(500)
        self.assertEqual(out.attempt_class, "hard_fail")
        self.assertTrue(out.trip_provider_breaker)
        self.assertEqual(out.job, "continue_chain")

    def test_400_kills_job_not_key(self) -> None:
        out = classify_hop_status(400)
        self.assertEqual(out.attempt_class, "non_retryable")
        self.assertEqual(out.job, "dead")
        self.assertFalse(out.counts_as_hard_fail)

    def test_401_quarantines(self) -> None:
        out = classify_hop_status(401)
        self.assertEqual(out.candidate, "quarantine_key")
        self.assertEqual(out.job, "continue_chain")

    def test_transport_trips(self) -> None:
        out = classify_hop_status(None)
        self.assertEqual(out.attempt_class, "hard_fail")
        self.assertTrue(out.trip_provider_breaker)

    def test_sse_wrap_is_buffered_not_a_second_call(self) -> None:
        first, done = sse_wrap_text("hello")
        self.assertTrue(first.startswith(b"data: "))
        self.assertIn(b"hello", first)
        self.assertEqual(done, b"data: [DONE]\n\n")


if __name__ == "__main__":
    unittest.main()
