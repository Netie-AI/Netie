# 2026-10-22 - crew-agent stage 2 (Hermes Agent gate wired and tested)

Preflight: KB `D:\Netie-KB` absent in this cloud box. `docs/subagents_findings/INDEX.md` read
(2 rows) plus the three wave 1 stage 2 findings on their branches. PREFLIGHT: PARTIAL.

Branch `claude/stage2-crew-agent`, base `claude/netie-ecosystem-rebrand-uq9q3z` (PR #43),
draft PR #54. Upstream NousResearch/hermes-agent at `e473f5a9c9` (MIT), overlay
`ecosystem/overlays/crew-agent/0002-gate.patch` on top of `0001-rebrand.patch`. Lane brief
dated 2026-10-22; the work ran 2026-10-22 to 2026-10-30. Session shape is the last section.

## Measured

Box: 4 cores, 15 GB, 271 GB volume, Python 3.14.6 from uv. Install: the upstream CI install
plus `--group test` (`uv sync --locked --python 3.14 --extra all --group dev --group test` and
the CI extras). Test command: the upstream CI command (`scripts/run_tests.sh`, one subprocess
per file, 4 workers, 600 s per-file cap, provider keys empty), run once per tree. "Stage 1" is
a local commit of upstream plus `0001-rebrand.patch`. The stage 2 full run is on the shipped
commit itself (`99976f43`, the main clone checked out clean), so no measured-versus-shipped
gap remains. Stage 2 rows include `tests/netie/` (27 files, 397 cases); the upstream-only
numbers are given beside them.

| What | Stage 1 | Stage 2 |
|---|---|---|
| Upstream suite, all files | 5295 files: 56737 passed, 97 failed in 27 files, 787 skipped | 5322 files: 56893 passed, 338 failed in 99 files, 787 skipped |
| Upstream suite, without `tests/netie` | same as above | 5295 files: 56496 passed, 338 failed in 99 files, 787 skipped |
| Wall time | 4609 s | 5731 s (per-file total 22060 s against 18212 s on the same files) |
| Files stopped at the 600 s cap | 1 (`test_code_health_identity.py`) | 1 (the same file) |
| Failures not on stage 1 | - | 242 ids: 207 stage 2 deltas, each with a proven cause and two intent opinions; 35 environmental (F8); 2 stage 1 flakes now pass |
| Skips | 787 | 787, the same in every file |
| Gate suite `tests/netie/` (397 cases) | 46 passed (pins), 349 failed, 2 stopped at a 300 s per-case cap | 397 passed (27 files), inside the full run |
| Replay of `0001` + `0002` on a fresh clone | - | `git write-tree` 335de31972, equal to the shipped commit; LICENSE sha256 equal to the catalog; no LICENSE, NOTICE or copyright line touched |
| Same replay in an independent session | - | first cut (`f35b1e0`): equal tree `84d7636729` and LICENSE sha256; its test runs were refused (F12) |
| Patch | - | 805976 bytes, 160 files, +12061 -553 |

- Stage 1 gate cell: pytest per file with `PYTHONPATH` pinned to the stage 1 tree (the venv's
  editable install otherwise lets a child process started elsewhere import another tree),
  26 files at once 3 at a time, then the sweep file case by case with a 300 s cap (11 fail, 2
  egress cases, `api_server` and `cli`, do not finish).
- The 46 cases that pass on stage 1 pin behaviour the gate must keep: explicit vendor and
  endpoint choices win (main route, auxiliary, vision, a named relay's own model), upstream's
  typed refusal for a key-less custom endpoint stays, session continuity (a continued session
  does not restart or rewrite its prompt; derived sessions and gateway branches carry the
  parent's prompt id), a streamed branch chains only its own history, a prompt repair clears
  the targeted row, and an API first turn under a declared session key saves only that turn.
- The sweeps fail on stage 1 before they scan: the `cli` artifact case fails with
  `no such table: sessions` (no session row was written), the other artifact and 6 egress
  cases fail in 5 to 298 s. Inferred, not shown per case: with only `NETIE_OPENVAULT_URL` set,
  stage 1's default route never reaches the loopback model. That the scans bite was shown on
  the round 7 tree with six scratch mutations (image backend unavailable; image, pet or speech
  to text gate removed; no compression padding; `write_file` allowed without an ask): the
  final sweep cases fail under every one. The config-variant sweep (F14) was red on the round
  10 tree for every breached variant.
- The patch edits 11 upstream test files, and only these: `tests/conftest.py` adds an
  autouse fixture that answers the gate transport (`agent.netie_gate._post`) with
  `allowed: true`, because no OpenVault runs in the suite (the gate code itself still runs
  on every call; `tests/netie` cases marked `netie_real_gate` keep the real, fail-closed
  transport); `tests/test_tests_tree_layout.py` declares `tests/netie` in its own
  `_NON_MIRROR_DIRS`; 9 files have 13 expected strings that follow the user-visible rename
  (`PRODUCT_NAME`, "Crew Agent is restarting", the gateway online notice). No assertion was
  removed or loosened, and no test is skipped.
- Of the 28 files that fail or stop on stage 1, 26 fail with the same counts on pristine
  upstream (no `0001`), `tests/scripts/test_code_health_identity.py` stops at the 600 s cap
  on both, and `test_compression_stall_deterministic_fallback.py` is a load flake (1
  failure on stage 1, 0 on pristine, 3 of 3 passes alone). F7.
- The upstream suite itself writes the real home: at about 42 percent of every full run,
  `tests/hermes_cli/test_cli_import_without_patch_stdout.py` creates `~/.hermes` (F11). It
  was moved aside before each full run and before attribution.
- Nothing in this repo enforces a stage 2 number (CLAUDE.md rule 7). The claim rests on the
  measurements above, the replay, F8 and the sweeps.

## F1. The upstream default sends model calls to whichever vendor key is in the environment

- **Expected (NETIE.md section 3, catalog gate):** one model endpoint, OpenVault
  `${NETIE_OPENVAULT_URL}/v1`; no vendor default; no provider key field in the default
  config or the env example.
- **Actual on stage 1:** `DEFAULT_CONFIG["model"]` is `""`, so provider `auto` walks the
  env-key ladder (OpenRouter, Anthropic, OpenAI and others) and ends at the OpenRouter rung;
  `.env.example` ships 22 model-provider key fields; the MoA default preset names
  `openai-codex` and `openrouter`; the TUI falls back to a hard-coded vendor model slug; the
  setup wizard's default first-run choice is Nous Portal; `batch_runner` defaults to an
  OpenRouter base URL.
- **Fix:** `model: {provider: openvault, default: auto}` and one `providers.openvault`
  entry; `NETIE_OPENVAULT_URL` defaults to `http://127.0.0.1:5000` through one normaliser
  (`hermes_constants`, a leaf module the installer can import) shared by the model endpoint
  and the gate; every entry point (interactive CLI, oneshot, TUI, gateway, cron, ACP, API
  server, batch runner, delegation children, model picker, wizard) resolves to it. The
  model-provider key fields left `.env.example` and the model section of
  `cli-config.yaml.example`; commented custom-provider and auxiliary examples there still
  show `api_key` lines. A user's explicit provider or `base_url` still wins; a `base_url`
  without a provider logs a WARNING.
- **Repro:** on each tree, `HERMES_PYTHON=<venv python> scripts/run_tests.sh` with
  `tests/netie/test_crew_agent_gate.py tests/netie/test_crew_agent_gate_model.py`.
- **Root-cause class:** a multi-provider upstream default standing in for a product
  decision, repeated in every entry point that builds its own view of the config.
- **Invariants:** assert the artifact the customer receives (the runtime each entry point
  resolves, with vendor keys present); fix the root-cause class (one default, one normaliser).

## F2. Tools ran without any external allow, and many paths skip the dispatcher

- **Expected:** every tool execution asks OpenVault `POST /api/crew/gate` with ids only
  (`{kind, id, intent, parent_run_id, child_id, deficit}`, the shape of
  `scripts/crew_ov_gate.py`) and fails closed with a visible refusal.
- **Actual on stage 1:** no gate. **Actual on the round 1 candidate** (a gate in
  `model_tools.handle_function_call` only), found by the round 1 review and the sweeps: it
  missed the inline agent tools (memory, todo, delegate_task, session_search and 11 more),
  memory-provider and context-engine tools, the inline and memory-provider branches of the
  concurrent `invoke_tool` path, MCP serve `messages_send`, `mini_swe_runner`, the Discord
  tools' schema-time capability probe (`GET /applications/@me`), and internal direct
  callers: `@url` references, gateway image enrichment, auto voice replies, client-direct
  speech to text, voice-live sessions and cron skill loading.
- **Fix:** `agent/netie_gate.py` (`tool_refusal`, `guard_direct_tool`), asked on the
  registry path, both inline paths and inside the tool entry functions that internal code
  calls directly, with a context variable so a dispatcher-gated call is not asked twice.
  Unreachable, non-JSON or `allowed` not true is a refusal.
- **Repro:** `tests/netie/test_crew_agent_gate.py`, `..._r6_directcallers.py`,
  `..._r7_stt.py`, `..._r8_final.py`, and the egress sweep in `..._r6_sweeptests.py`.
- **Root-cause class:** a gate placed at one dispatcher while the codebase has several ways
  to execute the same tool function.
- **Invariant:** fix the root-cause class; a skipped path is a failing path.

## F3. The persisted session record carried prompt and skill text

- **Expected (`scripts/crew_checkpoint.py`):** ids and status only; resume cannot recover a
  prompt.
- **Actual on stage 1:** `state.db system_prompts` held the full system prompt (SOUL text,
  the skill index and any `skills.auto_load` skill bodies); `sessions.title` was the first
  line of the user's message; terminal API errors wrote the whole request to
  `sessions/request_dump_*.json`; `async_delegations` stored subagent goals, context and
  summaries; gateway prompt pins wrote context and channel prompts into `gateway_routing`;
  `response_store.db` kept every `/v1/responses` transcript unless the caller sent
  `store=false`; the turn log line wrote the first 80 characters of the user message to
  `agent.log`; the runs idempotency store, delivery ledger, TUI spawn trees and CLI input
  history kept text.
- **Fix:** sha256 ids instead of bodies (an upsert, plus a marked open-time scrub for older
  databases, with SQLite `secure_delete` on blanking paths); auto-titles off by default;
  digests in request dumps and the turn log line unless `HERMES_DUMP_REQUESTS` or
  `HERMES_LOG_USER_TEXT` is set; the delivery ledger keeps reply text only while a delivery
  is owed and a digest after; ids-only prompt pins and response store, with chains rebuilt
  from the messages table by row id; resume rebuilds the prompt without a WARNING and
  without re-firing first-turn hooks; branch, compression, move and import paths carry the
  parent's id.
- **Declared, not fixed:** the `state.db` messages table keeps the conversation in plain
  text. TAS-CREW section 6 plans session transcripts on Crew disk, hashed, and
  `crew_checkpoint` persists no transcript at all, so this is a gap, not a reading of the
  contract. The other local transcript stores are under "Not done".
- **Repro:** `tests/netie/test_crew_agent_gate_session.py`, `..._ledgers.py`,
  `..._r6_sidestores.py`, `..._r7_ledgerbytes.py`, `..._r7_inputpersist.py`, and the marker
  sweep in `..._r6_sweeptests.py` (markers through the CLI, the CLI input box, the TUI
  gateway, a messaging gateway and the API server, then every file and sqlite row, WAL
  included, under `HERMES_HOME`).
- **Root-cause class:** convenience caches that copy the transcript into side stores.
- **Invariant:** assert the artifact (the store tests read the real sqlite rows or files).

## F4. Gating adapter creation does not gate the machine's messaging egress

- **Expected:** content leaves the machine to a messaging platform or an external agent
  only with an OpenVault leave-machine allow, and a refusal is labelled.
- **Actual on the round 1 candidate** (adapter creation gated): `send_message`,
  `hermes send`, MCP `messages_send`, cron standalone delivery and the kanban notifier post
  with the bot token through standalone senders that never build an adapter; a2a tools and
  the Teams pipeline post directly; a startup refusal was never retried, and a refusal on
  reconnect was labelled as a missing plugin (`adapter_unavailable`).
- **Fix:** the leave-machine ask at the shared choke point
  `tools/send_message_tool._send_to_platform` and in each direct poster. An adapter refusal
  stays in the reconnect queue with status `netie_leave_machine_refused`; a standalone send
  returns the labelled refusal as its error; asks run off the event loop.
- **Repro:** `tests/netie/test_crew_agent_gate_gateways.py`, `..._r5_claims.py`, and the
  egress sweep (socket level, gate refusing: no connect leaves the machine).
- **Root-cause class:** gating the object (adapter) instead of the effect (bytes leaving).
- **Invariant:** assert the effect: the egress sweep checks the sockets opened; the targeted
  tests check that no sender ran.

## F5. Stage 1 attribution names the wrong upstream commit, in 5 of 13 overlays

- **Expected:** `NETIE-ATTRIBUTION.md` names the commit the overlay is cut against.
- **Actual:** crew-agent's said `7157422022`; the pin is `e473f5a9c9`. Across the repo:
  control, crew-agent, crew-edge, freeide-ext and freeroute-core mismatch; the other 8
  match. By count and mechanism they are the five rows whose pins were corrected after the
  probe (F3 of `2026-10-05-ecosystem-lane.md` counts five; freeroute-core's own `0002` says
  its stage 1 text named the upstream HEAD at probe time). The attribution text was
  generated before and never regenerated, and `ecosystem.py validate` compares only
  `base_commit`.
- **Fix here:** crew-agent's file corrected inside `0002-gate.patch`. Measured on the wave 2
  branches on 2026-10-30: control and freeroute-core fixed theirs in `0002`; crew-edge fixed
  its `19c40eea3e` to pin `f7bd2b9e94` in `0003` (commit `544d057`) after this lane told it;
  freeide-ext has no `0002` yet. No enforcer in `validate`.
- **Repro:** compare `grep -o "pinned at commit [0-9a-f]*" ecosystem/overlays/*/0001*.patch`
  with each row's `commit` in `ecosystem/catalog.json`.
- **Root-cause class:** a derived artifact generated before its source was corrected.
- **Invariants:** never hand-author generated artifacts; prove a gate can fail.

## F6. A green gate test coexisted with 28 confirmed gaps

- **Expected:** the first 13-case gate test, red on stage 1 and green after, means the gate
  holds.
- **Actual:** in that green state a 5-lens adversarial review confirmed 11 gaps, a later
  5-lens completeness critic confirmed 10 more, and two empirical sweeps (a marker grep over
  `HERMES_HOME`, outbound socket instrumentation) confirmed 7 more. Confirmed means both of
  two independent verifiers, each asked to refute it, judged it real. Another 12 items split
  the verifiers; they were not dropped: 10 were fixed and 2 are declared (delegation live
  logs, cron run archives).
- **Fix:** 28 fix packages over 8 rounds, each adding `tests/netie` cases (with rounds 9 to
  12: 351 of the 397 cases fail or do not finish on stage 1). The two sweeps stay as permanent
  tests so the next missed path fails CI instead of waiting for a review.
- **Repro:** not reproducible from this repo: the per-finding reproductions and verifier
  votes are in the lane's scratch records. The durable check is the gate suite on stage 1
  (Measured).
- **Root-cause class:** a test written by the implementer asserts the paths the implementer
  wired; it cannot see the ones they did not.
- **Invariants:** adversary is not the verifier; assert the artifact (sweeps beat review).

## F7. 96 of the 97 stage 1 failures belong to this container, 1 is a load flake

- **Expected:** the stage 1 baseline is green, or each red file is explained.
- **Actual:** 26 files fail with identical counts on pristine upstream (no `0001`);
  `test_code_health_identity.py` stops at the 600 s file cap on both; the 28th
  (`test_compression_stall_deterministic_fallback.py`) fails 1 on stage 1, 0 on pristine,
  and passes 3 of 3 alone.
- **Repro:** the CI command on a pristine clone and on stage 1; compare per-file counts.
- **Root-cause class:** environment. Measured: identical counts without the overlay.
  Inferred from the failing files, not diagnosed one by one: root user, a shallow clone
  without an upstream remote (update and release tests), no network, timeouts.
- **Invariant:** separate verified fact from assumption.

## F8. Every stage 2 delta in the upstream suite has a proven cause and a reviewed intent

- **Expected:** each upstream test that fails on stage 2 and not on stage 1 fails because of
  one named stage 2 change, and that change is required by a gate rule.
- **Actual (final run on `99976f43`):** 242 test ids fail that pass on stage 1.
  - 35 are environmental. Upstream's state-database repair refuses its forensic backup when
    the volume has less free space than max(256 MiB, 2 percent of the volume): this box had
    4.2 GB free of 271 GB, about 5.4 GB is needed. The same 6 files fail identically on stage
    1 with this disk (35 failed, 348 passed on each tree) and pass on both trees with the
    pytest base directory on tmpfs (383 passed each).
  - 207 are stage 2 deltas. Each was re-run alone first (it still failed), then with one
    diagnostic plugin that reverts one stage 2 area inside the test process (never shipped),
    or with the stage 2 code reverted in a scratch tree when the test starts a fresh process:

    | Cause (what a revert makes pass) | Tests |
    |---|---|
    | session record ids only: prompt hash, titles off, response store, prompt pins, logs | 96 |
    | OpenVault model default: provider ladder, picker, wizard, MoA, cron, compression route | 77 |
    | ledgers ids only: request dumps, async delegations, delivery ledger, runs idempotency | 11 |
    | auxiliary discovery chain closed; `custom` without endpoint refuses (code revert) | 8 |
    | speech to text without cloud auto-detect | 6 |
    | the real tool gate met by a child process (no OpenVault in the suite) | 4 |
    | model default and discovery closure together (both reverted) | 4 |
    | leave-machine gate or child-process tool gate (either revert) | 1 |

  - Intent: two independent reviewers judged each of the 207 intended (the test asserts
    upstream behaviour a gate rule removes, and the observed value is the gate's): 193 in the
    earlier per-test review and its second-opinion pass (cause class unchanged on the final
    tree), 14 re-reviewed on the final tree (both reviewers agreed on all 14). The earlier
    review found 14 collateral regressions; F13 says how they were fixed.
  - 2 stage 1 failures pass now (the two stage 1 flakes, F7).
  - Durations, one run per tree: per-file total 22060 s against 18212 s. Largest single
    files: `tests/cron/test_cron_script.py` +307 s (OpenVault down: upstream auto-recovery,
    see Not done), `tests/tools/test_completed_process_results.py` +118 s (a child process
    refused by the real gate), the state-database repair files +82 s (the disk floor above).
    `tests/scripts/test_icon_flavors.py` and `tests/tui_gateway/test_tui_gateway_server.py`
    take the same time on both trees when run alone (load). The rest is not attributed.
- **Repro:** per test, run it alone on both trees; the scratch harness that ran the control
  and revert plugins is not in this repo.
- **Root-cause class:** upstream tests encode upstream defaults (the vendor provider ladder,
  stored prompt bodies, plain-text side stores, auxiliary discovery) that the gate changes.
- **Invariants:** separate verified fact from assumption; a skipped test is a failing test
  (skips are equal per file; no test was skipped, deleted or loosened).

## F9. Operational: a `pkill -f` pattern matched its own shell

- **Expected:** stopping a stray test runner stops only that runner.
- **Actual:** `pkill -f "run_tests_parallel.py"` also killed the calling shell and a second
  run, because the pattern appeared in the shell's own command line. Lost: 24.5 percent of
  an after-run and 64 percent of a pristine run, both re-run. It recurred once after the
  rule was written down: `for p in $(pgrep -f PATTERN); do kill $p; done` in one command
  killed its own shell (nothing measured was lost that time). A wait loop on
  `pgrep -f PATTERN` never ended for the same reason.
- **Repro (untested here):** `bash -c 'sleep 60 # run_tests_parallel.py' &` then
  `pkill -f run_tests_parallel.py`.
- **Root-cause class:** a process match broader than the target.
- **Fix and invariant:** list with `pgrep -af` in one call, read it, then `kill <pid>` in a
  separate call; wait on a pid (`kill -0`), not a pattern. Look at the target before
  deleting or stopping it.

## F10. Attribution found three regressions that four reviewed fix rounds missed

- **Expected:** a fix round accepted by an independent reviewer introduces no upstream
  failure.
- **Actual (full run on the round 4 tree):** `agent/turn_context.py` raised
  `NameError: _preview_text` on a console path (5 upstream tests; the upstream ruff config
  does not select F821); `test_fresh_source_install` failed with
  `ModuleNotFoundError: No module named 'agent.netie_gate'` from the installer tail; the new
  `tests/netie/` tree broke `test_tests_tree_layout`.
- **Fix:** the URL helpers moved to `hermes_constants`; the name is defined on every path;
  `netie` is declared in the layout test's own `_NON_MIRROR_DIRS` list with a reason. A
  per-file F821 comparison (against stage 1, later against each round's base) ran from
  round 5 onward.
- **Repro:** on the round 4 tree, `tests/agent/test_context_token_tracking.py`,
  `tests/agent/test_interpreter_shutdown_turn_exit.py`,
  `tests/scripts/test_fresh_source_install.py` and `tests/test_tests_tree_layout.py` fail;
  no single revert plugin of the attribution harness (F8) makes them pass. `ruff check
  --select F821` shows the undefined name.
- **Root-cause class:** review reads the diff; only the upstream suite runs the paths the
  diff reaches indirectly (import layering, rare branches, repo-shape tests).
- **Invariants:** assert the artifact; a skipped test is a failing test.

## F11. The real home gets polluted, by the upstream suite itself and by probes

- **Expected:** measurements read only their own `HERMES_HOME`.
- **Actual (measured):** `tests/hermes_cli/test_cli_import_without_patch_stdout.py` runs
  `python -c "import cli"` in a subprocess whose env has `HOME` but no `HERMES_HOME`, which
  creates `~/.hermes` (SOUL.md, cache, logs, sessions) on stage 1 and stage 2 alike; in a
  full run that happens at about 42 percent. Two `tests/gateway/test_platform_base.py`
  cases fail when `/root/.hermes` exists; in a full run they run at about 32 percent, so
  they pass unless an earlier run or a probe left the home behind. One full run (round 4
  tree) started with a polluted home and counted them as stage 2 deltas until stage 1 was
  re-run the same way. Assumed: some earlier pollution also came from agent probes run
  without a temporary `HERMES_HOME`.
- **Fix:** `/root/.hermes` moved aside before every full run and before attribution; probe
  briefs set `HERMES_HOME` to a temporary directory. The upstream test is left as is.
- **Repro:** `HOME=$(mktemp -d)` then run that test file on either tree and list
  `$HOME/.hermes`.
- **Root-cause class:** shared mutable state outside the test sandbox.
- **Invariant:** separate verified fact from assumption (a delta is not a regression until
  stage 1 is re-measured under the same conditions).

## F12. Sessions started from this one could not run upstream code

- **Expected:** an independent verifier session replays the patch and re-runs the gate and
  upstream suites on a fresh container.
- **Actual:** the replay passed there (report 2026-10-30 04:41 UTC: same tree, same LICENSE
  sha256), but its permission classifier refused `uv sync`, so the gate suite, the stage 1
  red proof, the upstream suite and the spot checks were not run. The fresh freeide-ext
  session started from its hand-off was refused `bun install` and then every shell command,
  and stopped at stage 1 (PR #52), as its original session had.
- **Not worked around.** Founder action: allow `uv sync` and `scripts/run_tests.sh` in a
  verifier session, and the bun commands for freeide-ext.
- **Repro:** start a session with `create_session` and ask it to run `uv sync` in a fresh
  upstream clone.
- **Root-cause class (assumed):** each session's own classifier refuses dependency installs
  and upstream code; this session's allowances do not carry over.
- **Invariant:** adversary is not the verifier; an unverified claim stays labelled
  unverified.

## F13. A revert that explains a delta proves its cause, not its intent

- **Expected:** every upstream failure that one stage 2 revert makes pass is a deliberate
  consequence of a gate rule.
- **Actual:** a per-test intent review of the 268 attributed failures (17 reviewers; every
  verdict other than "intended" re-judged by a second agent who could run the single test on
  both trees; every "intended" verdict re-checked by a second skeptic, 192 of 193 agreed, and
  a third agent broke the tie) confirmed 14 failures, in 8 root causes, that no gate rule
  requires: the
  auxiliary client filled a provider the user named (a named custom provider, Bedrock, xAI)
  with OpenVault's `auto`; an explicit `--provider auto` raised "provider 'auto' has no
  endpoint configured" instead of meaning no choice; the main-route helper ignored an explicit
  `base_url`; the default model was not withheld for a user's own provider; the picker
  dropped the local runtime row; a bare `custom` endpoint landed on the OpenVault entry; the
  ids-only delegation label overwrote a live status; the dashboard listed the built-in
  OpenVault default as a user custom endpoint that its Delete control cannot remove.
- **Fix:** rounds 9 and 10, one implementer per cause in its own git worktree and a different
  reviewer per patch. Two first attempts were sent back: the main-route fix was rejected
  because it reopened the vendor discovery chain, and the auxiliary-model fix still leaked
  `auto` through a live session's runtime. Each fix added `tests/netie` cases that fail before
  it. In the final run 11 of the 14 pass; the other 3 (cause B) fail only where they assert
  the vendor env-key ladder that rule 1 removes.
- **Repro:** each named upstream test passes on stage 1 and fails on the round 8 tree with a
  value no gate rule asks for (the review records name the line and value).
- **Root-cause class:** a default injected as configuration is read by explicit-choice code
  as if the user had chosen it; a relabelling pass rewrites live state.
- **Invariants:** a delta is explained only when its intent is shown, not when a revert
  makes it pass; adversary is not the verifier.

## F14. The egress sweep covered the default config only; config variants reopened vendor discovery

- **Expected:** with vendor keys in the environment, no auxiliary route reaches a vendor host
  the user did not name, whatever the config says.
- **Actual (round 10 reviewers, reproduced on the round 8 tree):** `model.provider: auto` or
  `""` sent every auxiliary task, vision and the credit fallback to OpenRouter through
  upstream's discovery chain; a `model.base_url` with no provider sent auxiliary calls without
  a live runtime to OpenRouter; vision walked OpenRouter, Nous and DeepInfra when a named
  provider could not build a client; `custom` with no endpoint resolved to Google's Gemini
  host. The permanent egress sweep runs with the default config only, so it stayed green.
- **Fix:** rounds 11 and 12 closed the chain for the whole class: a no-choice value resolves
  to the OpenVault route, a `model.base_url` without a provider to that endpoint, vision gets the
  same guard, and `custom` with no endpoint gives no auxiliary client and refuses the main route
  with a named error (upstream fell to the OpenRouter rung with `OPENROUTER_API_KEY`). A new
  permanent sweep, `tests/netie/test_crew_agent_gate_r11_configsweep.py`, resolves the main
  route and every auxiliary task, vision and the credit fallback for 12 config variants with
  eight vendor keys set; it was red on the round 10 tree and is green, with no xfail.
- **Repro:** with `OPENROUTER_API_KEY` set and `model: {provider: auto}` in config.yaml, resolve
  the compression auxiliary client on the round 8 tree: base_url `https://openrouter.ai/api/v1`.
- **Root-cause class:** upstream's auxiliary discovery chain stayed reachable through no-choice
  values and unbuildable choices; the gate test enumerated one config, not the config space.
- **Invariants:** fix the root-cause class; prove a gate can fail (the sweep now runs every
  config variant, red on the round 8 tree).

## F15. A one-line fix made without its own reviewer leaked one session's client to another

- **Expected:** a small follow-up fix (making auxiliary provider `main` follow the live main
  route) needs no separate review.
- **Actual:** the lane author wrote round 13 directly, proved its new test red then green, and
  ran the gate and auxiliary suites (all as expected). A reviewer then showed that the change
  dropped the live runtime from the auxiliary client cache key on the `call_llm` path: a second
  session or a `/model` switch with a different endpoint and key was served the first
  session's client. It also left a fresh home (default `openvault`) ignoring the live runtime.
  Round 14 redid it with an implementer and a different reviewer; that reviewer rejected it
  too (an explicit auxiliary model id with a slash was dropped for `main`). Both attempts to
  make `main` follow the live session were reverted; the shipped tree keeps round 12's
  meaning (the config main route, as upstream) and declares it.
- **Repro:** on the round 13 tree, with `auxiliary.compression.provider: main` and the cache
  kept, call `call_llm` for compression with a custom runtime A, then a custom runtime B with
  another base_url and key: B's request goes to A's endpoint with A's key.
- **Root-cause class:** a cache key built from the raw provider label while routing used the
  normalised value; the new test cleared the cache between calls, so it could not see reuse.
- **Invariants:** adversary is not the verifier, also for the lane author's own small fixes;
  assert the artifact on the real call path (cache kept), not on a helper.

## Not done / assumed

- **Assumed, not measured:** OpenVault answers `POST /api/crew/gate` in the
  `scripts/crew_ov_gate.py` shape. It is not on OpenVault main (TAS-OPENVAULT section 8).
  Inferred from the fail-closed code: on a real install every gated tool call and every
  gateway is refused until it lands. Every gate test runs against a local fake OpenVault, a
  refused local port or the transport seam. Whether OpenVault `/v1` needs a seat token or
  serves `/v1/models` is not measured; the provider entry carries no key.
- **Not run:** only Python tests ran (the upstream suite and `tests/netie`). The Ink TUI
  (TypeScript), the website, the Docker image and release packaging were not built.
- **Declared, not changed** (full list in `NETIE-ATTRIBUTION.md` inside the patch): the
  plain-text messages table (F3) and a few local transcript stores (cron run archives, live
  delegation logs, subagent summary spill files, `agent.log` on failed turns); unsalted
  digests; plugin prompt sections rebuilt on resume; a short list of local or ungated paths
  (`skill_view` reads, TUI path completion, MCP serve `permissions_respond`, the Discord
  onboarding token check, the Google Meet realtime CLI). Auxiliary provider `main` follows the
  config main route (OpenVault in a home that chose nothing), not a live session's explicit
  runtime, and vision under a live vendor runtime uses that vendor's key from the environment
  rather than the runtime's own key: both are upstream behaviour, and two attempts to change
  the first introduced regressions (F15). In the reviewers' vendor-key probes neither reached a
  vendor host the user did not name.
- **Stage 3:** package, binary, module, env and home names still say hermes; non-English
  locales, the Ink TUI defaults and history writer, and release banners still say Hermes;
  subscription-login providers stay selectable by an explicit user choice (DR-0002 rule 6
  says off in a fork); tool keys for search, image, speech and browser services are still
  `.env.example` fields; SECURITY and CONTRIBUTING point upstream.
- **Measured, left for stage 3:** with OpenVault down, a turn fails only after upstream's
  provider auto-recovery runs out (3 attempts per cycle, 5 cycles, waits of 16, 34 and 69 s
  and more). `test_env_vars_cleaned_on_early_error` (cron) takes 328 s on stage 2, 7 s on
  stage 1 and 5 s on stage 2 with only the model default reverted. Inferred: upstream
  treats any unreachable provider this way; a refused loopback OpenVault should fail fast
  with a message that names it. Runs that resolve the OpenVault provider through the
  auxiliary client log a WARNING that it has no api_key.

## Session shape

Why one session plus workflows and not a session per lens: the fix rounds edit the same
upstream tree, so the session owns integration and every measurement, and the agents work
in their own git worktrees and return patches. The founder switched the session's model
mid-lane; review, critic, verifier and fix agents ran at medium effort.

| Count | Lens | Context | Outcome |
|---|---|---|---|
| 1 | this session: implement, integrate, measure, attribute, cut, publish | isolated container, own upstream clone and worktrees | PR #54 |
| 5 + 2 per finding | review of round 1: gateways, model, regression, session, tools | read-only on the candidate tree | 11 confirmed, 5 split, 3 refuted |
| 5 + 2 per finding | completeness critic: artifacts, e2e, egress, regression, tests | read-only, empirical probes allowed | 10 confirmed, 6 split, 3 refuted |
| 2 + 2 per finding | empirical sweeps: marker artifacts, socket egress | probes in a temporary `HERMES_HOME` | 7 confirmed, 1 split (fixed in round 7) |
| 28 + 28 | fix packages over rounds 1 to 8: one implementer each, one different reviewer per patch | own git worktree per implementer | 4 accept, 23 accept with fixes, 1 reject (round 4 response chains, fixed in round 5) |
| 6 + 1 | claim check of this finding: one skeptic per section, one completeness critic | read-only | 173 claims: 131 supported, 42 corrected in this text |
| 17 + 75 | per-test intent review of the 268 run 1 deltas: one classifier per batch, a second agent on every non-intended verdict | read-only, single-test runs allowed | 14 collateral regressions, 1 flake (F13) |
| 15 + 1 | second opinion on the 193 single-opinion "intended" verdicts, tiebreak on disagreement | read-only | 192 agreed, 1 more regression (cause H) |
| 9 + 9 | fix rounds 9 to 12: one implementer per cause in its own worktree, one different reviewer | own worktree | 2 first attempts sent back (C rejected, A with fixes); rounds 11 and 12 added the config sweep |
| 1 + 2 | round 13 by the lane author, round 14 by an implementer; one reviewer each | own worktree | both rejected (F15); reverted to round 12 semantics |
| 2 + 1 | final intent check of the 14 deltas no revert plugin explains alone | read-only | 14 of 14 intended by both reviewers |
| 1 | independent verifier session | fresh container, read-only | replay equal; tests refused (F12) |

Coordination: the wave 2 board (PRs #47 to #54) is reported to the wave 2 parent session,
not here.
