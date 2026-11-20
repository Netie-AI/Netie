# 2026-11-20 - recut 2, Cortex lane (sibling suite clean; one memo on the chat gate)

Preflight: KB `D:\Netie-KB` absent in this cloud box. `docs/subagents_findings/INDEX.md`
read; `2026-11-12-sibling-recut.md` F3 was the hit (43 Cortex failures behind a green gate).
PREFLIGHT: HIT. No subagents spawned: one session read, cut, ran and wrote this file.
Session `session_01N6JxFUTyTbepQ5qdiuBTMK`, branch `claude/recut2-cortex`, stacked on PR #59.

Cortex pin `304bf843cabfa1a2714c6a64ca0c4a9e4aac6099`. On 2026-11-20 `git ls-remote` showed
Cortex `main` at the same commit, so the pin is the live head. Nothing was pushed to Cortex.

Rulings applied (quoted in `docs/decisions/DR-PROPOSED-parked-patches-yield-to-sibling-tests.md`):
`web_fetch` "Both, if possible"; `/dms/query` "Keyless stays allowed".

## Result (measured)

Cortex's own suite, same command on an unpatched and a patched clone of the pin:

| Command | Unpatched | Patched (4 patches, gate order) |
|---|---|---|
| `uv run --all-extras pytest tests/dms tests/test_api tests/contract tests/harness tests/security -q -p no:cacheprovider` | 2729 passed, 0 failed, 12 skipped, 4 xfailed | 2745 passed, 0 failed, 12 skipped, 4 xfailed |
| `uv run --all-extras pytest tests -q -p no:cacheprovider` (whole suite) | 5280 passed, 0 failed, 13 skipped, 4 xfailed | 5296 passed, 0 failed, 13 skipped, 4 xfailed |

Every difference, by test id (`--collect-only` on both trees, 5296 against 5312 ids; nothing
is only in the baseline; all 16 are tests our patches add, and all 16 pass):

- `tests/dms/test_broker_no_skip.py`: `test_broker_source_has_no_web_or_discovery_skip`,
  `test_web_fetch_reaches_the_net_only_through_the_runner`,
  `test_web_fetch_internal_address_is_refused_and_ledgered`,
  `test_web_fetch_is_not_an_action_route_or_dag_tool`,
  `test_search_and_discovery_have_no_handler_and_deny[web_search]`, `[find_skills]`,
  `[find_mcp]`, `[find_subagents]` (8).
- `tests/dms/test_constitution_path.py`: `test_a2a_is_dms_pack_only`,
  `test_coding_tools_refused_even_via_tool_runner`, `test_export_pptx_needs_an_actor`,
  `test_observe_png_and_clipboard_refuse`, `test_tool_runner_refuses_bash`,
  `test_unverified_answer_is_refused` (6).
- `tests/dms/test_f7_rbac.py`: `test_execute_modules_require_a_key`,
  `test_dms_query_stays_keyless` (2).

One Cortex-written test passes on the patched tree only because a patch edits it:
`tests/dms/test_f2_chat.py::test_chat_api_routes`. See F3 and the memo. That is the one place
where this lane does not meet the "no sibling test edited" rule, and it is left as it was in
PR #59, undecided, on purpose.

## F1. web_fetch: both were possible

- **Expected:** every broker tool call goes through `run_tool_call`, and Cortex's 6
  `web_fetch` tests in `tests/harness/test_hx01_quick_fixes.py` pass unchanged.
- **Actual before:** the patch removed the built-in, so `web_fetch` answered "not a
  registered action type" and those 6 tests failed.
- **Fix (in `cortex-web-via-runner.patch`):** `tool_runner.py` gains
  `AGENT_BUILTINS = frozenset({"web_fetch"})` and a keyword `agent_builtins: bool = False`
  on `run_tool_call`. Only `default_broker` passes `agent_builtins=True`. For `web_fetch`
  the runner calls Cortex's own `web_tools.fetch` with `public_only=True` forced (the model's
  own `public_only` is dropped), raises a ledgered deny with verdict `public_only` when the
  guard refuses, ledgers `action.tool_call` otherwise, and returns Cortex's fetch result
  unchanged. `default_broker` is still one `run_tool_call` and names neither `WEB_TOOLS`
  nor `DISCOVERY_TOOLS`. No Cortex test is touched by this patch.
- **What did not change:** `web_search` and `find_skills` / `find_mcp` / `find_subagents`
  still deny as unregistered, as the README said before. The ruling named `web_fetch` only.
  No Cortex test in the whole suite calls them through `default_broker`.
  `POST /dms/actions/web_fetch` and DAG tool nodes still deny `web_fetch` (they do not pass
  the flag), and `allowed_action_tools()` is unchanged.
- **Choices made here, for review (assumptions, not rulings):**
  - A runner built-in, not an ontology `action_types.yaml` row. A row would have made
    `web_fetch` callable from `/dms/actions`, the agent SDK and DAG tool nodes, would have
    needed the `title_required` compliance rule changed, and would not reach installs whose
    ops DB was compiled earlier. Not tried; rejected on reading the code.
  - The URL is not passed through `sanitize_params` and the `tool_call` compliance ruleset
    is not run for `web_fetch`: the ruleset has one rule (a title for `export_pptx`), and
    the guard must judge the exact URL that is fetched.
  - The ledger row stores `params_hash`, not the URL, the same as `export_pptx`.
  - A ledger write now sits on the `web_fetch` path. On a default install it goes to
    `data/dms_ops.db`. A ledger error would surface as an exception from the broker, where
    the old built-in had no ledger at all.
- **Repro:** clone the pin, apply the four patches in gate order, run
  `uv run --all-extras pytest tests/harness/test_hx01_quick_fixes.py tests/dms/test_broker_no_skip.py -q`.
  20 passed.
- **Root-cause class:** a control cut against an older head removed a behaviour the sibling
  had since hardened and tested.
- **Invariant:** a control that blocks legitimate work is itself a failure; re-check after
  hardening. Assert the artifact the caller receives (the broker's return value and the
  ledger row), not the source text alone.

## F2. /dms/query is keyless again; the write routes in the same file stay gated

- **Expected (ruling 2):** `POST /dms/query` answers without a key.
- **Actual before:** `require_role("viewer")` on the route; 37 Cortex tests got 401.
- **Fix (in `cortex-role-execute.patch`):** the `/dms/query` dependency is gone. Kept: the
  steward gate on `/dms/propose-edit`, `/dms/analyse-entry`, `/dms/add-entry`, and the
  `chat_routes` gates. The brief said "the dms_query.py hunks"; I removed only the
  `/dms/query` hunk and kept the three write-route hunks, because the ruling is about
  `/dms/query`, the brief also says to keep what still applies, and no Cortex test in the
  whole suite fails with them in place. This is my reading; say so if all of
  `dms_query.py` was meant to go.
- **Patch's own test:** in `tests/dms/test_f7_rbac.py` the line asserting `/dms/query` 401
  is removed from `test_execute_modules_require_a_key`; that test now also asserts 401 on
  the three write routes and on both remaining chat routes. New
  `test_dms_query_stays_keyless` asserts the keyless status is neither 401 nor 403.
- **Repro:** `uv run --all-extras pytest tests/dms/test_f7_rbac.py -q` on the patched clone,
  10 passed. Put the viewer dependency back on the route: 1 failed
  (`test_dms_query_stays_keyless`).
- **Root-cause class:** a gate added without running the sibling's callers of that route.
- **Invariant:** a control that blocks legitimate work is itself a failure.

## F3. The chat gate needs a Cortex test edited. Stopped here; decision memo

- **Expected (rule 1 of the proposed DR, acceptance 3 of the brief):** no patch edits a test
  Cortex wrote.
- **Actual:** `cortex-role-execute.patch` adds `headers={"X-API-Key": "pytest-steward-key"}`
  to three calls in Cortex's `tests/dms/test_f2_chat.py::test_chat_api_routes` (5 lines
  changed). This edit was already in the patch on PR #59; it was not counted on 2026-11-12
  because the test passes once edited.
- **Repro:** on the patched clone run `git checkout 304bf84 -- tests/dms/test_f2_chat.py`
  then `python -m pytest tests/dms/test_f2_chat.py -q`: 1 failed, 2 passed
  (`assert 401 == 200` on `POST /dms/threads`).
- **Root-cause class:** a green suite that is green because the patch rewrote the test.
- **Invariant:** never weaken or edit a check to force green; prove a gate can fail.

### Decision memo: chat routes gated, or Cortex's chat test untouched

The two behaviours that cannot both hold:

1. `POST /dms/threads`, `POST /dms/threads/{id}/messages` (steward) and
   `GET /dms/threads/{id}/messages` (viewer) need a key. The brief for ruling 2 names this
   gate as one to keep, and the README lists it as what the patch is for.
2. Cortex's `test_chat_api_routes` calls all three routes with no key and expects 200. It
   must not be edited.

Evidence: the repro above (401 against 200). There is no way to gate a route and have an
unkeyed caller get 200; the test does not set `DMS_AUTH_DISABLED`. Baseline behaviour on
the pin is that anyone who can reach the engine can create a thread and append a message,
which writes `thread.created` / `message.inbound` rows to the ledger.

Options:

- **A. Keep the gate and the 3-header test edit (what is committed now).** The route is
  protected. Rule 1 is broken for one test, in the open. The test still proves the routes
  work, now with a steward key.
- **B. Drop the chat gate.** Delete the `CortexOS/api/chat_routes.py` and
  `tests/dms/test_f2_chat.py` sections from the patch, and the two `/dms/threads` lines
  plus the two `t1/messages` lines from the patch's `test_execute_modules_require_a_key`.
  Rule 1 holds everywhere. The patch then gates only the three dms write routes, and
  chat writes stay open, as they are on Cortex today. The gate test's three `chat`
  assertions would be replaced by one asserting the routes are left as Cortex has them.
- **C. Keep the gate out of the parked patch and raise it with Cortex's owners**, who can
  change their own test in their own repo. From this repo that is a note, not a push
  (`CLAUDE.md` rule 9).

Recommendation: B now, with C recorded as the follow-up. The rule the founder is being
asked to accept is that a parked patch never rewrites a sibling test; an exception on the
first lane makes the rule a wish. Keyless chat writes are Cortex's current, tested
behaviour, the same kind of thing ruling 2 just kept for `/dms/query`. If the founder
weighs the open write path as worse than the exception, A is already what is committed.
Not decided here.

## F4. Gate assertions changed (every edit under scripts/)

All in `scripts/test_sibling_patches.py`; nothing else under `scripts/` changed.
`apply_product_patches.py` and `test_apply_product_patches.py` needed no edit (same four
patches, same order, same verify command).

- `test_cortex_role_execute_applies_on_main`: removed
  `assertIn('require_role("viewer")', query)` (retired by ruling 2). Added in its place:
  the `/dms/query` decorator line carries no dependency; `require_role("viewer")` is absent
  from `dms_query.py`; each of the three write routes carries the steward dependency;
  `chat_routes.py` has exactly two steward and one viewer dependency; `test_f7_rbac.py`
  holds `test_dms_query_stays_keyless` with its status assertion and no longer holds the
  401 assertion on `/dms/query`.
- `test_cortex_web_via_runner_applies_on_main`: added (nothing removed) `agent_builtins=True`
  in `default_broker`, and in `tool_runner.py` the `AGENT_BUILTINS` set, the forced
  `public_only=True` call and the default-off keyword.
- `test_cortex_netie_path_applies_on_main`: unchanged.
- Proved able to fail: with the two old patch files restored from `HEAD`, both edited
  tests fail (`agent_builtins=True` not found; ungated `/dms/query` line not found).
- The gate is source-text only; it has no Cortex install. The behaviour is proved by the
  patch's own tests on Cortex's stack, counted above. R4 held: no check that still applies
  was loosened.

## Measured

- `python3 scripts/test_sibling_patches.py SiblingPatchTests.test_cortex_netie_path_applies_on_main SiblingPatchTests.test_cortex_web_via_runner_applies_on_main SiblingPatchTests.test_cortex_role_execute_applies_on_main`:
  3 tests, OK.
- `make ci`: 30 files, laptop-ASCII clean, 46 script tests passed.
- The two suite commands in the table, each on an unpatched and a patched clone of the pin,
  Python 3.13.18, `uv run --all-extras`. The four runs overlapped on one 4-CPU box.
- A fresh clone of the pin with the four committed patch files applied in gate order has
  the same git tree (`729e1dd`) as the tree the patched suites ran on.
- `cortex-web-via-runner.patch` applies alone on the pin and after `cortex-netie-path.patch`.
  Its `tool_runner.py` hunks carry one line of context so that both hold.
- README verify command on the patched clone
  (`python -m pytest tests/dms/test_constitution_path.py tests/dms/test_broker_no_skip.py tests/dms/test_f7_rbac.py -k "not tool_runner" -q`):
  22 passed, 2 deselected.
- Mutations on the patched clone: `AGENT_BUILTINS` emptied, 8 of 20 fail; `public_only`
  taken from the model, 7 of 20 fail; viewer gate restored on `/dms/query`, 1 of 10 fails.

## Not run

- Each suite ran once per tree. No repeat for flakiness; with 0 failures in 5296 tests
  there was nothing to re-run. Zero observed failures is not a zero failure rate.
- No real network fetch: every `web_fetch` test stubs the socket layer, as Cortex's do.
- No run against a Postgres ledger (`DMS_LEDGER_DSN`), and no run with an ops DB that has a
  compiled `ontology_action_types` table.
- No live engine: nothing was started with uvicorn and called over HTTP; route behaviour is
  from FastAPI `TestClient`.
- `scripts/apply_product_patches.py --product cortex` was not run. Its verify step uses the
  system Python, which has no FastAPI here, so `test_f7_rbac.py` cannot be collected. That
  was already so before this lane. `test_broker_no_skip.py` now also needs Cortex's
  dependencies (it was a file read before).
- Cortex lint, type check and import-linter were not run on the patched tree.
- Option B of the memo was not cut or run as a patch; its only evidence is the repro in F3.
- DMS PRD-001 EPIC-004 was not checked against the keyless ruling.
