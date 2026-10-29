# 2026-10-22 - Crew Harness stage 2 (deepseek-harness gate wired and tested)

Preflight: KB `D:\Netie-KB` absent in this cloud box. `docs/subagents_findings/INDEX.md`
read: two prior findings (ecosystem lane, wave 1 session shape) plus the three wave 1
stage 2 findings on their branches. PREFLIGHT: PARTIAL. No subagents spawned; one session
did clone, install, edit, test and patch-cut directly. Started 2026-10-22, halted by the
founder the same day, resumed and finished 2026-10-28 in the same container.

Branch `claude/stage2-crew-harness`, base `claude/netie-ecosystem-rebrand-uq9q3z` (PR #43).
Upstream deepseek-ai/deepseek-harness at 5badb15009 (MIT), overlay
`ecosystem/overlays/crew-harness/0002-gate.patch`. The upstream is a developer preview:
root `package.json` says 0.2.1-alpha.1 at the pin; the catalog role text quotes the older
README figure 0.1.0-rc.5. Every claim below is a claim about that preview.

## F1. The default model route was the vendor's API with a vendor key field

- **Expected (catalog gate, NETIE.md section 3, DR-0002 rule 6):** one OpenAI-compatible
  model route, OpenVault `/v1`; no provider key field in the default config.
- **Actual on the stage 1 tree:** `packages/bundle/base/cordis.patch.yml` defaults new
  Agents to `provider: deepseek-official, model: deepseek-flash`, mounts the native
  DeepSeek adapter rows `llm-deepseek` and `llm-deepseek-account`, and keys its search
  route with `apiKeyEnv: DEEPSEEK_API_KEY`; `sdk-minimal` keys `llm-deepseek` the same
  way; `acp-app` selects `deepseek-official`. The multi-provider adapter `llm-pi-ai` was
  mounted dormant with zero routes.
- **Fix:** `llm-pi-ai` carries one hand-declared route `openvault` (`api:
  openai-completions`, `baseURL` from `NETIE_OPENVAULT_URL`, default
  `http://127.0.0.1:5000/v1`, one model `auto`, OpenVault's catalog pick per
  TAS-OPENVAULT); `agent-default-model` and the ACP row select `openvault`; the two direct
  DeepSeek rows and the keyed search row are not mounted; `web_search` stays listed and
  fails loud (`WEB_PROVIDER_UNAVAILABLE`) until a search route exists. The only
  credential reference left is `NETIE_OPENVAULT_KEY`, the caller's issued `ov_` identity
  (TAS-OPENVAULT section 3, metering); a missing reference fails the request with
  `MISSING_CREDENTIAL`, it does not fall back.
- **Repro:** `python3 scripts/ecosystem.py clone crew-harness D && python3
  scripts/ecosystem.py apply crew-harness D`, then in D `pnpm install && pnpm exec vitest
  run packages/bundle/base/tests/netie-defaults.spec.ts`. Baseline (0001 only, spec copied in): 17 of 17 cases fail.
  After 0002: 17 of 17 pass.
- **Root-cause class:** a vendor default standing in for a product decision; the adapter
  that could carry any gateway was shipped empty.
- **Invariants:** assert the artifact the customer receives (the shipped patch files,
  parsed with the upstream loader schema and its `!!js` evaluator); silent fallback is a
  lie (missing key is a named refusal).

## F2. Tools and the sandbox registered under nobody's gate

- **Expected (TAS-CREW section 3, DR-0002 rule 6):** tool execution goes through the Netie
  gate or the fork is not shipped; a plugin that registers tools or a sandbox outside the
  wrap is refused at registration with a visible error; the wrap sends ids only to
  OpenVault `POST /api/crew/gate`.
- **Actual:** `ctx.tools.register()` accepted any definition and `tools/pre-execute` had
  only the upstream approval policy; `dsh-sandbox-local` provided `ctx.sandbox` on
  construction. Nothing asked OpenVault anything.
- **Fix:** new package `packages/guard/crew-gate` (`@deepseek-ai/dsh-crew-gate`, 237
  source lines) ports the contract shape of `scripts/crew_ov_gate.py` and
  `scripts/crew_tool_wrap.py`: `allow({kind, id, intent, parent_run_id, child_id})`
  refuses before POST on a body key (`skill_body`, `prompt`, `instructions`,
  `transcript`), an unregistered kind (`skill` included), an empty id or missing run ids;
  refuses on an empty URL, a transport failure, a non-object reply or a reply without
  `allowed: true`. A `tools/pre-execute` listener asks `kind: service, id: <tool>,
  intent: tool, parent_run_id: <agent session id>, child_id: <call id>` before every
  tool body. `dsh-tools` gains `crewGate: required | off` (schema default `off`, base and
  every mode bundle set `required`) and refuses `register()` with a visible error while
  `ctx.crewGate` is absent; `dsh-sandbox-local` gains the same field and refuses before
  providing `ctx.sandbox`. The composition rows inject `crewGate`, so neither can activate
  before the gate exists.
- **Repro:** same clone, `pnpm exec vitest run packages/guard/crew-gate/tests/crew-gate.spec.ts`.
  Baseline: the file cannot load (`Cannot find package @deepseek-ai/dsh-crew-gate`), so 0 of its 13 cases run. After: 13 of 13 pass.
- **Root-cause class:** trust-the-LLM default. The upstream's approval policy is a user
  prompt, not a custody decision; absence of a gate read as a policy.
- **Invariants:** fail closed (no URL, no gate, no tool); a control that blocks legitimate
  work is itself a failure, so the schema default stays `off` and the upstream unit suite
  keeps running; prove a gate can fail (both files recorded red on the baseline).

## F3. What the build and the suite proved, and what they did not

- **Measured on this box** (Linux, 4 cores, 15 GB, Node 22.22.0, pnpm 11.7.0 via
  corepack): see "Measured before and after" below
- **Upstream tests that pinned the old defaults** (updated, none deleted or skipped):
  `scripts/client-build-environment.client.spec.ts` (6 literals `DeepSeek Harness` now
  read the exported `OFFICIAL_CLIENT_TITLE`), `packages/bundle/acp-app/tests/acp-app.spec.ts`
  (expected default route), `packages/bundle/sdk-minimal/tests/sdk-minimal.spec.ts`
  (expected row list and route config). Generated files regenerated with the upstream
  tools, never edited: `tsconfig.base.json` (`gen-tsconfig-paths`), `docs/config-catalog.md`
  and `.zh.md` (`gen-config-catalog`), `pnpm-lock.yaml` (`pnpm install`),
  `packages/guard/crew-gate/README.i18n.yaml` (`verify-translation-pairing --write`).
- **Not run:** the Web UI build (`pnpm run build:web`) and the Desktop app build; the typecheck includes the client build step that printed `built in 2.27s`.
- **Not measured:** whether OpenVault `/v1` refuses a call without `NETIE_OPENVAULT_KEY`,
  whether it serves `/v1/models`, whether `POST /api/crew/gate` is on OpenVault main (the
  Netie TAS says it is a patch, PR #44). A live OpenVault was not on this box.
- **Root-cause class:** a stage claim is only as wide as the suites that ran. Said in
  `NETIE-ATTRIBUTION.md` under "Not done yet (stage 3)".
- **Invariant:** say what is measured and what is assumed.

## F4. A baseline run on the tree being edited is not a baseline

- **Expected:** one `pnpm test` on the applied tree gives the "before" column.
- **Actual:** the suite reads source and patch files at test time; edits made while it ran
  would have been read by later files. Caught after about 15 minutes of the first run.
- **Fix:** killed it; `git worktree add /tmp/crew-harness-base <baseline commit>` with its
  own `pnpm install`, and the before column comes from that untouched tree.
- **Root-cause class:** adversary and verifier sharing a working tree.
- **Invariant:** adversary is not the verifier; the before and after columns come from
  two trees, and the parent replays the overlay on a third.

## F6. First stage 2 run found 12 regressions the targeted runs had missed

- **Expected:** every baseline pass still passes.
- **Actual:** 12 tests passed on the baseline and failed on the stage 2 tree: 5 in
  `apps/cli/tests/plugin.spec.ts` (inline snapshot pinned the old Desktop error text), 4 in
  `desktop-onboarding.client.spec.tsx` (snapshot files pinned the old brand), 3 in
  `packages/typert/generator/tests/cordis-catalog.spec.ts` (a real regression: the new
  `crewGate` service had no page in `scripts/gen-cordis-catalog.ts` and its `GateAsk` type
  was unclassified, so the catalog generator refused). 1 further failure
  (`out-of-process`) was upstream's, failing on the baseline too, and 1 baseline failure
  (`skill-office`) passed.
- **Fix:** the two snapshots updated to the new brand (tests kept); the onboarding
  introduction also now says Crew Harness so a page no longer mixes names; `crewGate`
  mapped to `docs/subsystems/sandbox.md`, `GateAsk` exempted (owner: the package README),
  `pnpm run gen-cordis-catalog` rewrote the generated docs.
- **Root-cause class:** verification ran on the files I touched, not on the consumers of
  what I touched (a new Service enters a generated catalog with a coverage gate).
- **Invariant:** a control that blocks legitimate work, and its mirror, a change that
  breaks a downstream gate, are found only by the full suite. Rerun the full suite after
  the last edit, not after the one before.

## F5. Patch replay

- `0002-gate.patch` is a plain `git diff --binary` against the stage 1 tree: 42 files changed, 1307 insertions, 90 deletions, 99 KB (under the 2 MB cap).
  A fresh `clone` plus `apply` (0001 then 0002) into a second directory gives the same
  `git write-tree` hash: `1eae41fe5ca3e40264a85347b4b0fb3587e7029e` in both. LICENSE sha256 unchanged
  (`ebb4f09972aee8608be255debaf78451a68e95c290f55c240dec2ecfa16ea6be`).
- Non-ASCII in the patch: upstream context lines and the zh README of the new package
  (CJK). Zero em dashes, en dashes or curly quotes in added English lines; the Netie docs
  gate scans `*.md` in this repo, not overlays.
- **Invariant:** never hand-author a generated artifact; the overlay is cut by git, and the
  catalog stage is set to 2 only because F1 to F5 held.

## F6. Stage 3 push: launch readiness, measured on 2026-10-29

The founder asked every lane to push toward stage 3 (shippable). What was done,
each with a test that failed first:

- **SDK code defaults** (`packages/sdk/client`, Python `deepseek_harness.api`,
  `subagent-dsh-sdk`): `deepseek-official` / `deepseek-v4-flash` -> `openvault` /
  `auto`. Pinned by `python/sdk/tests/test_client.py` (expectation updated) and the
  SDK server suite.
- **Hidden vendor fallback closed (F7).**
- **Product copy** (Models welcome notice, Office preview notice) says Crew Harness.
  Copy naming the DeepSeek account sign-in stays DeepSeek on purpose: it names the
  vendor account, not this product.
- **Launch readiness e2e**
  `apps/cli/tests/profiles/headless/tests/netie-launch.expected.e2e.ts` (2 cases,
  upstream `test:expected` runner): boots the shipped headless profile from source
  against a stand-in serving `/v1/chat/completions` and `/api/crew/gate`. Asserts
  the model request goes to `${NETIE_OPENVAULT_URL}/v1` with
  `Authorization: Bearer $NETIE_OPENVAULT_KEY` and model `auto`; the tool body runs
  only after the gate answered `allowed: true` to an ids-only ask whose
  `child_id` equals the logged tool call id; a refusal lands in the session log
  as `tool/result` with `error.code CREW_GATE_DENIED` and no `todo/write` event.
  Baseline: 0 of 2. Stage 3 tree: 2 of 2.
- **Build**: `pnpm run build` exit 0 (CLI, SDK runtime, web client, 355 client
  artifacts), 1m36s wall. Memory not measured (the sampler was wrong, numbers
  discarded). Built `dsh --help` says "boot a Crew Harness profile";
  `dsh --profile headless --dump-config` shows `agent-default-model` provider
  `openvault`, the `llm-pi-ai` openvault route, the `crew-gate` row and `tools`
  injecting `crewGate`.
- **Root-cause class:** a stage number is a claim; the proof is the artifact the
  operator launches, not the unit under test.
- **Invariant:** prove a gate can fail (0 of 2 on baseline, 2 of 2 after).

## F7. The SDK server mounted the vendor adapter behind the composition's back

- **Expected:** which routes exist is decided by the composition (DR-0002 rule 6).
- **Actual:** `packages/sdk/server/src/server.ts` `initialize()` mounted
  `dsh-llm-deepseek-api-key` on demand whenever a caller named `deepseek-official`
  and no adapter existed, so an SDK client with the old default would have got a
  DeepSeek route with `DEEPSEEK_API_KEY` even though no shipped profile mounts one.
- **Fix:** a provider without a mounted adapter is refused, whichever it is. Five
  upstream tests that relied on the fallback now mount the adapter explicitly
  (none deleted); one new case asserts `deepseek-official` is refused like any
  other unmounted provider.
- **Repro:** `pnpm exec vitest run packages/sdk/server/tests/server.spec.ts -t "no vendor fallback"`.
- **Root-cause class:** a convenience path that re-creates the default the
  composition removed. Silent fallback is a lie.

## F8. Recorded-session corpora replay without an OpenVault

- **Expected:** the upstream `test:snapshot` corpus (recorded headless and ACP
  sessions) replays unchanged.
- **Actual on the stage 2 tree:** ACP 8 of 16 and headless 120 of 139 replays failed (run stopped before the SDK corpus). Every tool call in a replay
  asked the default `http://127.0.0.1:5000/api/crew/gate`, nothing answered,
  the gate refused, and the replayed session diverged from the recording.
- **Fix:** the corpora's live compositions switch the gate off with the same
  mechanism the upstream already uses there for its permission mode
  (`danger-full-access` under `DSH_SNAPSHOT`): `crew-gate` disabled, `tools` and
  `sandbox` `crewGate: off` with `inject: []`, in `snapshots/session/text-turn/cordis.yml`,
  `snapshots/acp/escalation-approved/cordis.yml` and eleven `snapshots/sdk/*/cordis.yml`.
  The DeepSeek adapter and search provider the corpus was recorded against are
  inserted by those compositions instead of patched by id. A first attempt also
  deleted the per-scenario `llm-deepseek: disabled` replay rows as dead; they are
  not dead once the adapter is inserted (the replay adapter must own the route),
  so they were restored untouched. Turning `web_search` off in stage 2 had changed
  the model-facing tool list every recording pins, so the tool stays listed,
  unkeyed, failing loud at call time. No shipped profile carries any of this; the
  gate on the shipped profile is proven by F2 and F6.
- **ACP picker:** the ACP handshake records the model picker. With the shipped
  OpenVault route mounted beside the replay adapter the picker gained a second
  group whose order follows adapter activation order and flipped between runs
  (refreshing the eight expectations with `DSH_SNAPSHOT=refresh` recorded one
  order, the full run produced the other). The recorded ACP sessions were made
  with one provider group, so the ACP corpus compositions disable `llm-pi-ai`
  and the original expectations replay unchanged (16 of 16). The picker's
  group order on a two-route composition is a stage 3 item, listed below.
- **After the fix:** 5 failed, 176 passed, 2 skipped (183), the same five names as the baseline. Baseline: 5 failed, 176 passed, 2 skipped (183), 3m13s; the 5 are sandbox-as-root and browser fixtures.
- **CLI expected-output suite (`test:expected`):** the same cause, 16 of 111 cases
  on the stage 3 tree before the override (every one a `CREW_GATE_DENIED` tool
  result in place of the recorded one). The 22 fixture patches under
  `apps/cli/tests` that boot a shipped profile carry the same override, and the
  web plugin-manager scenario, which writes its patch inline, carries it in the
  test; the launch fixture `netie-openvault.patch.yml` does not. Baseline, built:
  5 failed, 104 passed (109). Stage 3 tree after the override: 4 failed, 107 passed (111).
  Four names fail on both (`provider-retry`, `agent-team`, `goal-tools`,
  `continuable child`: missing `.sessions` directory and persistence timing on
  this box); `DeepSeek defaults through the one-shot app` fails on the baseline
  only and passes on the stage 3 tree, where the fixture inserts the adapter it
  configures.
- **Nested dispatch:** one refusal was spurious: a sub-call dispatched inside an
  already gated root call (the `dsh-badge` skill load) carries no agent, so the ask
  had no parent id and the gate refused it. A nested call now names its root call
  id as `parent_run_id` (ids only, both real); a root call with no agent is still
  refused. Unit case added in `crew-gate.spec.ts` (14 cases now).
- **Root-cause class:** a corpus recorded before the gate existed. A test that
  exercises a path the gate turns off runs under the documented override, and the
  default-off path has its own test.
- **Invariant:** a skipped test is a failing test (none skipped); a control that
  blocks legitimate work is itself a failure (the replay corpus is legitimate work).

## Launch readiness: what an operator needs

| Need | Measured or assumed |
|---|---|
| OpenVault at `NETIE_OPENVAULT_URL` (default `http://127.0.0.1:5000`) serving streaming `POST /v1/chat/completions` | Assumed from TAS-OPENVAULT (FreeRoute is `/v1`); the wire shape the harness sends is measured against a stand-in |
| `/v1` accepting model `auto` as its catalog pick | Assumed from TAS-OPENVAULT ("model: auto stays catalog pick") |
| `NETIE_OPENVAULT_KEY` (issued `ov_` key) in the launching environment | Measured: sent as Bearer; whether `/v1` refuses without it is not measured |
| OpenVault serving `POST /api/crew/gate` with `allowed: true` for `kind: service` asks | NOT on OpenVault main (TAS-OPENVAULT section 8: PR #44 / `docs/patches/openvault-crew-gate.patch`). Until it lands every tool call is refused, visibly |
| `pnpm run build` artifacts | Measured, exit 0 |

The last row is why the catalog stage stays 2: a product whose every tool call
is refused against the current OpenVault main is not shippable tomorrow, and a
stage 3 claim needs that endpoint live, not a stand-in. The stage 3 evidence
(build, launch e2e, SDK defaults, copy) ships in the patch.

## Measured before and after

Stage 2 columns measured 2026-10-28, stage 3 columns 2026-10-29, same box (4 cores,
15 GB, Node 22.22.0, pnpm 11.7.0).

| Measure | Baseline (0001 only) | Stage 2 tree | Stage 3 tree |
|---|---|---|---|
| Gate specs (30 cases, `pnpm test` runner) | 17 failed; crew-gate.spec.ts unloadable (13 cannot run) | 30 passed | 30 passed |
| Launch e2e (2 cases, `test:expected` runner) | 0 of 2 | not present | 2 of 2 |
| `pnpm test`, full | 19 files / 24 tests failed, 39662 passed, 262 skipped, 34m08s | 15 files / 18 failed, 39709 passed, 251 skipped, 21m42s (after the F3 fixes) | 17 files / 21 tests failed, 39713 passed, 246 skipped (39981), 27m26s |
| `pnpm run test:snapshot` (recorded corpora, 183) | 5 failed, 176 passed, 2 skipped, 3m13s | ACP 8 of 16 and headless 120 of 139 failed before the F8 override | 5 failed, 176 passed, 2 skipped, 2m43s; the same five names as the baseline |
| `pnpm run test:expected` (CLI expected-output suite, built trees) | 5 failed, 104 passed (109), 3m39s | not run | 4 failed, 107 passed (111; the launch e2e adds 2), 3m17s |
| Python SDK `pytest` | 208 passed, 12 skipped (upstream's own skips) | not run | 208 passed, 12 skipped |
| `pnpm run typecheck` | exit 0, 6m10s | exit 0, 6m13s | covered by the build |
| `pnpm run build` (CLI, SDK runtime, web client) | exit 0, 2m18s | not run | exit 0, 1m36s |
| Lint on changed files (`run-oxlint`) | n/a | clean | clean, 28 files |
| Skips added | n/a | none | none |
| Patch | n/a | 42 files, +1307/-90, 99 KB | 90 files, +1995/-213, 177 KB; replay tree hash equal, LICENSE sha256 equal |

Failing in both baseline and stage 2 runs (upstream's, untouched): 23 tests, all
environment: this box runs as root so permission-denied tests do not deny
(`out-of-process`, `subagent-acp`, `agent-instructions`, `sqlite-backend`, `sandbox`),
plus Windows/IPv6/proxy/browser/real-product fixtures (`workflow-ptc`, `connection`,
`stagehand`, `claude-code real-product`, `migrate-sessions`, `prepare`, `project-doc-site`,
`spawn-runner`, `llm-mock-server`, `macos-notarization-proxy`, `review-tab`). Some flake
by load: 7 baseline failures passed in the final stage 2 run, and that run's one new
name, `linked-resolution-matrix` L0086, is a 5000 ms timeout that passes alone (4800 of 4800).
The final stage 3 full run shares every failing name with the baseline except two,
both reproduced identically on the built baseline worktree: `ui-trajectory
client-bundle` (reads the built client artifact, which the earlier unbuilt baseline
run did not have) and `subagent out-of-process` (root user, no permission denial).
The skipped count fell from 262 to 246 across runs; the skips are environment-
conditional in upstream suites and none was added or edited.
The corpus's 5 baseline failures (`bash-tool` sdk, `browser-use-stagehand-native`,
`ptc-node-read-only`, `ptc-node-workspace`, `workflow-confinement`) are the no-sandbox-
backend and browser fixtures and fail identically on the stage 3 tree.

## Not done / assumed

- Catalog stage stays 2. The blocker is outside this fork: OpenVault main does not
  serve `POST /api/crew/gate`, so every tool call is refused until PR #44 lands.
- Package scope, binary name, `DSH_*` env names, `~/.dsh` home, Desktop and container
  names: each needs a build and a rebase plan. About 190 further brand strings
  (package.json descriptions, zh locales, prompts) are listed in `NETIE-ATTRIBUTION.md`.
- The DeepSeek account sign-in platform row stays mounted: `account-controller` (web
  API) and `product-analytics` (client) inject it as a required service, so removing
  it hangs the Web app. It is a sign-in, not a model route; the `llm-deepseek-account`
  route is not mounted. Its copy still says DeepSeek on purpose.
- Sandbox `confine()` calls are not posted individually; the tool call that spawns them is.
- ACP `configOptions` lists provider groups in adapter activation order; with two
  routes mounted the order is not deterministic. Observed, not fixed in product code.
- `web_search` is listed but has no provider; a search route through OpenVault is not wired.
- Not measured: the Desktop app package, the Python SDK bundled runtime (its 12
  skips), whether OpenVault `/v1` refuses a call without `NETIE_OPENVAULT_KEY`,
  whether it serves `/v1/models`, and `/api/crew/gate` against a real OpenVault.
- The recorded corpora run with the gate switched off in their test compositions
  (F8); the shipped profile is what the launch e2e boots, gate on.
- `scripts/test_sibling_patches.py` is red on base and on this branch (9 of 10 failed
  when re-run here, identical with these changes stashed; the brief said 8 of 10; see
  F2 of `2026-10-05-ecosystem-lane.md`). Not touched, not skipped.
