# Patches for sibling repos this token cannot push (403)

Apply on a machine with write access. Do not vendor OpenWork or Grok Bot.

## Constructor (`Netie-AI/constructor`)

From the constructor repo root, on `landing-9-first-path`:

```
git apply docs/patches/constructor-compiler-tests.patch
git apply docs/patches/constructor-empty-graph.patch
git apply docs/patches/constructor-ir-refuse.patch
git apply docs/patches/constructor-ir-ids.patch
git apply docs/patches/constructor-ghost-refuse.patch
git apply docs/patches/constructor-ir-emit.patch
git apply docs/patches/constructor-tool-action.patch
git apply docs/patches/constructor-inspect-action.patch
git apply docs/patches/constructor-inspect-object.patch
git apply docs/patches/constructor-inspect-tier.patch
git apply docs/patches/constructor-chat-object.patch
git apply docs/patches/constructor-topo-leftover.patch
git apply docs/patches/constructor-ir-entry.patch
git apply docs/patches/constructor-ir-output.patch
git apply docs/patches/constructor-ir-object.patch
git apply docs/patches/constructor-ir-bind.patch
git apply docs/patches/constructor-ir-action-allow.patch
node --test tests/compiler.test.cjs
```

Adds `rankForKinds`, empty-graph IR (no invented Cortex nodes), refuse unknown kinds / cycles / dangling edges / missing ids / duplicate ids, `ghostWalk` that refuses those instead of walking a fake order, `EMIT` only on app/audit output (connector-only does not invent EMIT), unlabeled `tool_call` does not invent `export_pptx` (compileIR refuses; inspect shows `(pick)` not a silent first-choice), unlabeled object does not invent `inventory`, unlabeled tier does not invent `T0` (compileIR emits null; inspect shows `(pick)`), unlabeled `set point` does not invent `inventory`, `topo()` does not append leftover cyclic nodes, `compileIR` entry is the Kahn source not `nodes[0]`, `compileIR` output is the Kahn sink app (or last Kahn node when no app/audit) not array-last, `compileIR` drops unlisted `object_type` (`hr_notes` / `Insight` do not become Cortex ontology), `fetch_from` must name the node's listed object (not `warehouse.hr_notes` on inventory), `data_point` must be on that object (not `salary` on inventory), `tool_call` unknown action (`bash`) refuses, unlisted action on a non-tool node is dropped, `export_pptx` on foundry sets `requires_confirm`, node `--test`, and `.github/workflows/test.yml`.
Measured on this VM 2026-08-28: 40 passed.

## OpenVault (`Netie-AI/OpenVault`)

From the OpenVault repo root, on `main`:

```
git apply docs/patches/openvault-detect-stacks.patch
cd OpenMW && uv run pytest tests/test_detect_stacks.py -q
```

Also, in this order (lkgp edits StrategyName after strict-random):

```
git apply docs/patches/openvault-strict-random.patch
git apply docs/patches/openvault-lkgp.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py -q
```

Adds `strict-random` (9th) then `lkgp` (10th of 19 OmniRoute user-facing strategies). LKGP stickies the last *successful* `execution_key` and clears that pin on a later failure of the same key. Not OmniRoute SQLite provider+connection.

Then:

```
git apply docs/patches/openvault-context-headroom.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py -q
```

Adds `context-optimized` (11th: largest known `context_window` first; no model catalog) and `headroom` (12th: `1 - max(util_5h, util_7d)`; missing util = full headroom; no provider quota fetch).

Then:

```
git apply docs/patches/openvault-reset-window.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py -q
```

Adds `reset-window` (13th: soonest `reset_remaining_ms` first; unknown last; no quota fetch; tie-band rotation not ported).

Then:

```
git apply docs/patches/openvault-reset-aware.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py -q
```

Adds `reset-aware` (14th: session/weekly remaining mixed with reset-pressure; missing reset remaining => urgency 0, remaining-only; OmniRoute uses 0.5 there; `limit_reached` last).

Then:

```
git apply docs/patches/openvault-cache-optimized.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py -q
```

Adds `cache-optimized` (15th: SHA-256 rendezvous of caller `cache_key` onto connection/execution identity; empty key leaves order; no prefix analyzer, no OAuth occupancy). Measured on this VM 2026-08-27: 22 passed. Push 403.

Then:

```
git apply docs/patches/openvault-execution-shapes.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py tests/test_execution_shapes.py -q
```

Adds the last 4 OmniRoute *names* as execution shapes, not sorts: `fusion` (panel + judge), `pipeline` (sequential thread), `context-relay` (first available + warning-band handoff), `auto` (must resolve to a sort). `apply_strategy` raises `StrategyNotASort`. PUT `/api/route/strategy` returns 400. Chat `/v1` is not wired to `run_fusion`. No autoCombo engine, no Codex quota fetch, no quorum-grace timers. Measured 2026-08-27: 35 passed. Push 403.

Then:

```
git apply docs/patches/openvault-chat-dispatch.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py tests/test_execution_shapes.py tests/test_execution_chat.py tests/test_freeroute_acceptance.py -q
```

`dispatch_combo` runs the 4 shapes. `/v1` fail-closes (`openvault_execution_shape`) so `model: fusion` is 400, not a key walk. `model: auto` stays the catalog alias (empty pool still 503). Measured 2026-08-27: 43 passed. Push 403.

Then:

```
git apply docs/patches/openvault-hop-walk.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py tests/test_execution_shapes.py tests/test_execution_chat.py tests/test_freeroute_acceptance.py -q
```

Hop-walk `call_model`: first healthy hop that can serve the panel model, sequential httpx.Client posts. `combo.models` present -> dispatch. Missing models still 400. Streaming shapes still 400. No quorum-grace, no breaker park on this path. Measured 2026-08-27: 47 passed. Push 403.

Then:

```
git apply docs/patches/openvault-hop-failover.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py tests/test_execution_shapes.py tests/test_execution_chat.py tests/test_freeroute_acceptance.py -q
```

Empty first hop falls through to the next hop that can serve the model. Pipeline `/v1` threads step output. Still sequential, not parallel quorum-grace. Measured 2026-08-27: 50 passed. Push 403.

Then:

```
git apply docs/patches/openvault-hop-park.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py tests/test_execution_shapes.py tests/test_execution_chat.py tests/test_freeroute_acceptance.py -q
```

Execution-shape posts use the same `classify_attempt` / `_apply_outcome` as the key walk: 429 parks, 5xx trips, 401 quarantines, 422 kills the job, OPEN breaker skips the post. Empty dispatch is 503, not a fake 200. Measured 2026-08-27: 53 passed. Push 403.

Then:

```
git apply docs/patches/openvault-hop-stream.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py tests/test_execution_shapes.py tests/test_execution_chat.py tests/test_freeroute_acceptance.py -q
```

Last hop may SSE (panel and intermediate pipeline steps stay buffered). Nameless `model: fusion` with `stream: true` is still 400. 500 on the stream hop falls through. One-survivor skip wraps buffered text as SSE (no second call). Not OmniRoute parallel quorum-grace. Measured 2026-08-27: 57 passed. Push 403.

Then:

```
git apply docs/patches/openvault-hop-relay.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py tests/test_execution_shapes.py tests/test_execution_chat.py tests/test_freeroute_acceptance.py -q
```

`/v1` context-relay reads caller `combo.available` and `combo.handoff` (or `contextHandoff`). Skip unavailable; inject the handoff blob; all-unavailable is 503. No Codex quota fetch. Not OmniRoute SQLite contextHandoffs. Measured 2026-08-27: 62 passed. Push 403.

Then:

```
git apply docs/patches/openvault-hop-trace.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py tests/test_execution_shapes.py tests/test_execution_chat.py tests/test_freeroute_acceptance.py -q
```

Usage ledger names the last successful hop (`vault_key_id` / provider / model_served), not `provider=dispatch`. Panel members before the judge are not each a ledger row (one request, one row). Measured 2026-08-27: 64 passed. Push 403.

Then:

```
git apply docs/patches/openvault-hop-usage.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py tests/test_execution_shapes.py tests/test_execution_chat.py tests/test_freeroute_acceptance.py -q
```

Last-hop upstream `usage` is copied onto the dispatch JSON so the ledger is measured, not a reservation. Panel tokens are not summed. No usage on the last hop stays estimated. Measured 2026-08-27: 65 passed. Push 403.

Then:

```
git apply docs/patches/openvault-hop-persist.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py tests/test_execution_shapes.py tests/test_execution_chat.py tests/test_freeroute_acceptance.py -q
```

`/v1` context-relay remembers a caller-supplied handoff blob in process memory so the next request can omit the blob (`combo.sessionId`). Caller blob wins over the store. No Codex quota fetch. No generated summary. Not OmniRoute SQLite. Measured 2026-08-27: 68 passed. Push 403.

Then:

```
git apply docs/patches/openvault-hop-anthropic.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py tests/test_execution_shapes.py tests/test_execution_chat.py tests/test_freeroute_acceptance.py -q
```

Execution-shape hop-walk skips Anthropic hops (same as the key walk). If they were the only matches, `/v1` returns 503 `anthropic chat not via /v1 proxy yet` and does not post. Not a Messages API. Measured 2026-08-27: 70 passed. Push 403.

Then:

```
git apply docs/patches/openvault-hop-scope.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py tests/test_execution_shapes.py tests/test_execution_chat.py tests/test_freeroute_acceptance.py -q
```

In-process handoff store is keyed by issued-seat identity (`tenant`) plus session. Same `sessionId` on another seat does not inject. Empty tenant does not persist. Not OmniRoute SQLite. Measured 2026-08-27: 72 passed. Push 403.

Then:

```
git apply docs/patches/openvault-hop-serve.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py tests/test_execution_shapes.py tests/test_execution_chat.py tests/test_freeroute_acceptance.py -q
```

No matching hop raises 503 `no hop can serve model` instead of empty-dispatch. Not a fake 200. Measured 2026-08-27: 73 passed. Push 403.

Then:

```
git apply docs/patches/openvault-hop-bound.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py tests/test_execution_shapes.py tests/test_execution_chat.py tests/test_freeroute_acceptance.py -q
```

In-process handoff store keeps at most 32 blobs per issued seat; oldest session is evicted. Other seats are untouched. Not OmniRoute SQLite. Measured 2026-08-27: 74 passed. Push 403.

Then:

```
git apply docs/patches/openvault-hop-catalog.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py tests/test_execution_shapes.py tests/test_execution_chat.py tests/test_freeroute_acceptance.py -q
```

Execution-shape `serves()` is catalog membership, not `resolve_model` first-choice rewrite. Garbage ids and other-provider ids are 503 `no hop can serve model`. Empty catalog (anthropic) still owns a concrete id so the named skip can fire. Key walk is unchanged. Measured 2026-08-27: 77 passed. Push 403.

Then:

```
git apply docs/patches/openvault-quota-share.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py tests/test_execution_shapes.py tests/test_execution_chat.py tests/test_freeroute_acceptance.py -q
```

`combo.strategy: quota-share` (and PUT `/api/route/strategy`) is 501 `openvault_unported`, not unknown 400 and not a key walk. Body flags `parallel` / `quorumGrace` / `fetchQuota` / `persist: sqlite` / `autoCombo` / `compress` / `mcp` / `a2a` are the same 501, not a silent sequential walk. OmniRoute-internal quota-share is not a 16th sort. Measured 2026-08-28: 86 passed. Push 403.

Independent of routing:

```
git apply docs/patches/openvault-crew-gate.patch
cd OpenMW && uv run pytest tests/test_crew_gate.py tests/test_contract.py -q
```

Adds `POST /api/crew/gate`: location + allowed, never a skill body. Unknown kinds (including `skill` until a registry row exists) refuse. This is not OpenVault PR #44 (that RFC also adds Netie-KB signposts). Measured 2026-08-27: 17 passed with contract tests.
