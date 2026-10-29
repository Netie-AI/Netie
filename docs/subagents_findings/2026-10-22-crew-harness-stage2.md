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
  DeepSeek rows and the keyed search row are not mounted; `web_search` is off. The only
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

## Measured before and after

| Measure | Before (baseline worktree) | After (stage 2 tree) |
|---|---|---|
| Gate specs (30 cases) | 17 failed; crew-gate.spec.ts unloadable (13 cases cannot run) | 30 passed |
| `pnpm test`, first full run | 19 files / 24 tests failed, 39662 passed, 262 skipped, 34m08s | 21 files / 35 tests failed, 39681 passed, 262 skipped, 32m07s |
| `pnpm test`, final full run (after the fixes in F6) | same as above | 15 files / 18 tests failed, 39709 passed, 251 skipped, 21m42s |
| `pnpm run typecheck` (build proof) | exit 0, 6m10s | exit 0, 6m13s |
| Lint (`tsx scripts/run-oxlint.ts`) | not run | clean |
| Skips added | n/a | none (skipped count fell 262 to 251 between runs; environment-conditional, not edited) |

Failing in both baseline and first stage 2 run (upstream's, untouched): 23 tests, all
environment: this box runs as root so permission-denied tests do not deny
(`out-of-process`, `subagent-acp`, `agent-instructions`, `sqlite-backend`, `sandbox`),
plus Windows/IPv6/proxy/browser/real-product fixtures (`workflow-ptc`, `connection`,
`stagehand`, `claude-code real-product`, `migrate-sessions`, `prepare`, `project-doc-site`,
`spawn-runner`, `llm-mock-server`, `macos-notarization-proxy`, `review-tab`). Some flake
by load: 7 baseline failures passed in the final stage 2 run, and the final run's one new
name, `linked-resolution-matrix` L0086, is a 5000 ms timeout that passes alone (4800 of 4800).
`skill-office checkers` failed in the baseline run and in a targeted rerun of the stage 2 tree,
passed in the first full stage 2 run: environment, not this patch.

## Not done / assumed

- Package scope, binary name, `DSH_*` env names, `~/.dsh` home, Desktop and container
  names: stage 3, each needs a build and a rebase plan. About 190 further brand strings
  (package.json descriptions, zh locales, prompts) are listed in `NETIE-ATTRIBUTION.md`.
- SDK code defaults (`packages/sdk/client`, `subagent-dsh-sdk`) still say
  `deepseek-official` when a caller passes no provider; 33 upstream tests pin them.
- Sandbox `confine()` calls are not posted individually; the tool call that spawns them is.
- `web_search` is off rather than routed through OpenVault; a search route is not wired.
- The DeepSeek account sign-in platform row and the Web Models page onboarding dialog
  remain; they are not a model route.
- Assumed, not measured: the Web UI (`pnpm run build:web`) and the Desktop app build.
- `scripts/test_sibling_patches.py` is red on base and on this branch (9 of 10 failed when re-run here, identical with my changes stashed; the brief said 8 of 10; see
  F2 of `2026-10-05-ecosystem-lane.md`). Not touched, not skipped.
