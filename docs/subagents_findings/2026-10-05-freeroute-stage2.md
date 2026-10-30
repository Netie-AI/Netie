# 2026-10-05 - freeroute stage 2 (OmniRoute gate)

Preflight: KB `D:\Netie-KB` absent in this cloud box. `docs/subagents_findings/INDEX.md`
had one row (ecosystem lane), which was read. PREFLIGHT: PARTIAL. No subagents were
spawned; everything below was run directly on a clone of upstream `23a1148486`.
Full detail and the OpenVault custody contract: `ecosystem/overlays/freeroute/PLAN.md`.

## F1. The upstream ships 42 providers the catalog row says must be off

- **Expected:** a handful of OAuth entries to switch off.
- **Actual:** 9 subscription-login ids across three catalog sections (oauth, noauth,
  apikey), plus a 33-entry web-cookie section whose whole purpose is "paste a consumer
  session, call private endpoints". `codex-app-server` and `cursor-api` were in the named
  class without carrying the upstream's `subscriptionRisk` marker: one calls itself safe
  because the Codex CLI holds the token, the other because it is "an API key" that bills a
  Cursor plan.
- **Repro:** `node --import tsx/esm` a script printing `Object.keys(AI_PROVIDERS)` on the
  baseline tree: 358 ids; on the stage 2 tree without the flag: 316.
- **Root-cause class:** a vendor-side risk label used as the gate list. The upstream's own
  `subscriptionRisk` flag is a UI banner, not a control, and it misses two of the nine.
- **Invariants:** assert the artifact the customer receives (the listing, the `/v1/models`
  response, credential selection), not the label; fix the root-cause class (gate at the
  catalog, the executor registry, the OAuth map and the runtime retirement set, one module).

## F2. A test registered after a top-level await never runs under the upstream runner

- **Expected:** 4 tests in the new gate test file.
- **Actual:** 2 ran. The upstream `test:unit` passes `--test-force-exit`; the process
  exited after the two tests registered before `await import(...)` of the DB-backed
  modules. Without the flag all 4 ran.
- **Repro:** put a `test()` after a top-level `await import()` and run with
  `node --test --test-force-exit`.
- **Root-cause class:** a runner flag that treats "no pending tests" as "done". A test that
  silently never runs is a skipped test.
- **Invariants:** a skipped test is a failing test; prove a gate can fail (the file was run
  on the baseline: 0 of 4 pass, then on stage 2: 4 of 4).
- **Fix:** imports moved inside the test bodies so all four register synchronously.

## F3. The full Next build does not fit this container

- **Expected:** `npm run build` as the step 2 build proof.
- **Actual:** OOM-killed by the memory cgroup at about 11.6 GB resident on the untouched
  baseline tree (`dmesg`: `Killed process ... next-build`). The upstream's
  lighter `build:backend` profile was OOM-killed the same way. Both on the untouched
  baseline. Catalog stage therefore stays 1; the gate patch, its test and the custody
  contract ship in the overlay as a plan.
- **Root-cause class:** environment capacity, not code; measured before any change.
- **Invariants:** say what is measured and what is assumed; do not weaken a check to force
  green (no `--max-old-space-size` games, no stubbing beyond the upstream's own documented
  profile).

## F4. R4 held on the gate itself

- 294 upstream tests in the 16-file subset pass on baseline; 250 pass on stage 2 without
  the flag, 294 with it. The 44 are presence assertions for gated providers, reported, not
  skipped or edited. The gate test fails on baseline (0 of 4) and passes after (4 of 4).
  Replay from a fresh clone gives a byte-identical tree (git tree hash equal).
- **Not verified:** vendor terms of service for Claude Code, Codex, Copilot, Cursor,
  Antigravity, and counsel review. Not a stage 3 claim, not "sellable".
