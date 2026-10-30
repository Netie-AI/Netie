# 2026-10-05 - AirGPT stage 2 (LibreChat gate wired and tested)

Preflight: KB `D:\Netie-KB` absent in this cloud box. `docs/subagents_findings/INDEX.md`
read: one prior finding (ecosystem lane). PREFLIGHT: PARTIAL. No subagents spawned; one
session did clone, build, edit, test and patch-cut directly.

Branch `claude/stage2-airgpt`, base `claude/netie-ecosystem-rebrand-uq9q3z` (PR #43).
Upstream danny-avila/LibreChat at f10b1d91f1 (MIT), overlay
`ecosystem/overlays/airgpt/0002-gate.patch`.

## F1. Upstream defaults expose eight model endpoints and ship provider-key fields

- **Expected (NETIE.md section 3, catalog gate):** AirGPT is a thin client of OpenVault.
  One endpoint, OpenVault `/v1`; no provider key anywhere in the default config.
- **Actual on the stage 1 tree:** `getEnabledEndpoints()` defaults to openAI, agents,
  assistants, azureAssistants, azureOpenAI, google, anthropic, bedrock plus every custom
  entry; `librechat.example.yaml` ships xAI and Anthropic-compatible custom endpoints and
  Azure and Bedrock examples; `.env.example` ships `OPENAI_API_KEY=user_provided`,
  `ANTHROPIC_API_KEY=user_provided`, `GOOGLE_KEY=user_provided`,
  `ASSISTANTS_API_KEY=user_provided` and a 15-key "known endpoints" list.
- **Fix:** endpoints block replaced by one custom endpoint `OpenVault` at
  `${NETIE_OPENVAULT_URL}/v1`; `.env.example` sets `ENDPOINTS=custom,agents` and
  `NETIE_OPENVAULT_URL=http://127.0.0.1:5000` (the port TAS-OPENVAULT measures for
  FreeRoute); every model-provider key field deleted, active or commented.
- **Repro:** `python3 scripts/ecosystem.py clone airgpt D && apply airgpt D`, then
  `cd D/packages/data-provider && npx jest specs/airgpt-gate.spec.ts`. On the stage 1
  tree it fails 7 of 8; after `0002-gate.patch` it passes 8 of 8.
- **Root-cause class:** a multi-provider upstream default standing in for a product
  decision. The shell inherits the vendor's "bring every key" posture unless a gate
  refuses it.
- **Invariants:** assert the artifact the customer receives (the two files an operator
  copies, parsed by the real `configSchema`); prove a gate can fail before trusting it
  green (baseline run recorded red).

## F2. Memory is "off" upstream only by omission

- **Expected:** cross-chat and user memory off by default with a visible label saying it
  is ungoverned until it routes through Cortex actions.
- **Actual:** upstream has no `memory:` block, so memory is inert, but one uncommented
  line turns on a memory agent that writes user facts to MongoDB outside any ledger or
  manifest. Nothing in the UI says so.
- **Fix:** `memory: {disabled: true, personalize: false}` in the default yaml with the
  label in the config, a `role="note"` line at the top of the Memories panel
  (`com_ui_memory_ungoverned`) and a sentence appended to the agent memory capability
  text. The gate test asserts both fields.
- **Root-cause class:** silent default. Absence of a block read as a policy.
- **Invariant:** silent fallback is a lie; degradation has to show in the output.

## F3. What the build proved and what it did not

- **Measured on this box** (Node 22.22.0, npm 10.9.4; `@librechat/agents` warns it
  wants Node 24, the build still passes): `npm ci` exit 0; `npm run build:packages`
  (data-provider, data-schemas, api, client package) exit 0 before and after the patch;
  `packages/data-provider` jest before: 54 suites, 2254 passed, 1 skipped (upstream's own
  skip, unchanged); after: 55 suites, 2262 passed, 1 skipped, delta is exactly the new
  gate suite; client jest on the four touched areas (About, documentTitle,
  ChatTitleInTab, Memories): 31 tests, 3 failed on the first run because
  `documentTitle.test.ts` hardcoded the default title `LibreChat`; those three now
  assert the exported `DEFAULT_APP_TITLE` and all pass; client `tsc --noEmit` exit 0;
  eslint and prettier on every changed source file clean (one prettier nit and one
  no-assertion warning in the new spec, fixed before the patch was cut).
- **Not run:** the full client jest suite, the `api` jest suite (needs
  mongodb-memory-server), the Vite client build, e2e. Bounded on purpose: the four
  package builds cover every file the patch touches that is compiled, and the three
  `api/server` edits are string fallbacks checked with `node --check`.
- **Not measured:** whether OpenVault `/v1` wants a seat token (the literal
  `apiKey: 'openvault'` is a schema filler, not custody) and whether it serves
  `/v1/models` (`fetch: false` until it does). A live OpenVault was not on this box.
- **Root-cause class:** a claim ("stage 2, gate wired and tested") is only as wide as
  the suites that ran. Said in `NETIE-ATTRIBUTION.md` under "Not done yet (stage 3)".
- **Invariant:** say what is measured and what is assumed.

## F4. Patch replay

- `0002-gate.patch` is a plain `git diff --binary` against the stage 1 tree, 78,717
  bytes, 18 files, 149 insertions, 905 deletions. A fresh `clone` plus `apply` (0001
  then 0002) reproduces the edited tree byte for byte: `git write-tree` over both
  checkouts gives `dfebb01381513652c214f4960befd04f340f73eb`. LICENSE sha256 unchanged
  (`1ce5c9d51e5ab764b44142cd44d1e687f5bfe32f807c7221c14d061007309b97`).
- Four em dashes appear in the patch as upstream context lines; zero in added lines.
  `scripts/check_docs.py` scans only `*.md`, so overlays carry upstream text as is
  (every existing `0001-rebrand.patch` already does).
- **Invariant:** never hand-author a generated artifact; the overlay is cut by git,
  and catalog stage 2 is set only because F1 to F4 held.

## Unchanged, reported as asked

- `scripts/test_sibling_patches.py` is red on base and on this branch: 10 tests, 8
  failures, same as finding F2 of `2026-10-05-ecosystem-lane.md`. Not touched, not
  skipped. `make ci` therefore stays red for that one reason only.
