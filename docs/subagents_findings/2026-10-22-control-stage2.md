# 2026-10-22 - control stage 2 (Orca gate wired and tested)

Preflight: KB `D:\Netie-KB` absent in this cloud box. `docs/subagents_findings/INDEX.md`
read: two prior findings (ecosystem lane, wave 1 sessions) plus the airgpt, freeide and
freeroute stage 2 findings on their branches. PREFLIGHT: PARTIAL.

Branch `claude/stage2-control`, base `claude/netie-ecosystem-rebrand-uq9q3z` (PR #43).
Upstream stablyai/orca at d17351401d (MIT), overlay `ecosystem/overlays/control/0002-gate.patch`.
Session shape: one lane session running Workflow
fan-outs: 2 read-only maps, 5 family implementers, 3 cross-family owners, 5 round-3/4 owners,
an adversary and a repair agent per owner, 9 whole-tree sweepers, 5 typecheck fixers. Disjoint
file ownership per agent, one shared tree. The lane was interrupted by two container restarts
and one 5-hour usage limit; each time the journal and the `/tmp` trees survived and work resumed.

## F1. Orca's fleet board read the local agent store, not the Netie contract

- **Expected (catalog gate):** the board reads ids only through `netie.control.project_board`,
  behind a config URL, not Orca's own store as source of truth.
- **Actual on the stage 1 tree:** every board surface (pop-out window, in-window drawer, sidebar
  counts) was built from the renderer's agent-status store, and cards carried prompt and
  assistant message text.
- **Fix:** `src/shared/netie-control-board.ts` admits only the `crew-board` shape with the same
  four refusals as `scripts/control_board.py` (body keys, remote-desktop kinds, unknown product,
  12000-char budget measured on Python's ASCII-escaped dump). The host reads
  `NETIE_CONTROL_BOARD_URL`; unconfigured, unreachable or refused gives an empty board whose
  `sourceLabel` says why. The pop-out refreshes on its own clock.
- **Repro:** `npx vitest run --config config/vitest.config.ts src/main/netie-control/netie-control-gate.test.ts`.
- **Root-cause class:** a local cache standing in for the system of record.
- **Invariants:** assert the artifact the operator receives (the relayed snapshot after the
  real dashboard validator); silent fallback is a lie (empty board is labelled).

## F2. "Launch off" at a few call sites left about 30 agent-start paths open

- **Expected:** agent launches go through the Crew ticket runner or are off by default with a
  visible label.
- **Actual:** the first cut gated four call sites (executor, worker start, RPC create, the
  renderer tab launcher). Read-only reviewers then traced, with file and line, agent starts
  through: both PTY spawn funnels, IPC workspace create, workspace create keeping
  `startupCommand`, terminal create and split, structured Claude and Codex sessions, OpenCode
  model servers, source-control text generation and model discovery, rate-limit and app-server
  probes, orchestration worker, federated and inject dispatch, `orchestration.run`,
  automations (renderer and serve-mode), external automations, cold-restore typed resume, mobile
  terminal create, Agent Teams, and app-typed `terminal.send` / plugin `sendText`.
- **Fix:** the decision (`src/shared/netie-crew-launch-gate.ts`) is enforced in the main
  process at each process or provider-session start, before any side effect; the refusal's
  message IS the label, and RPC passes the code through. An agent start is recognised by the
  upstream launch fields or by an agent command line (`src/shared/netie-agent-command-line.ts`,
  which sees through `sh -c`, `cmd /c`, PowerShell `&` and `-EncodedCommand`, `npx` packages).
  Workspaces are still created with the agent startup stripped and a warning.
- **Root-cause class:** a policy placed at callers instead of at the chokepoint every caller
  funnels through.
- **Invariants:** fix the root-cause class; adversary is not the verifier (every family was
  attacked by a separate agent after implementation, and 4 rounds closed what they proved).

## F3. Two controls that blocked legitimate work, found by their own adversaries

- **Actual:** (a) a line-editing emulator on app-typed text refused a phone user who typed
  `claude`, erased it and ran `ls`; (b) generic agent names refused non-agent tools
  (`goose ... up` migrations, the `kilo` editor, the Hermes JS compiler); (c) `command -v claude`
  was read as a launch; (d) a work-item launcher refused work that starts no agent.
- **Fix:** the phone keystroke stream is a person typing and is not judged; deleted text never
  counts; shared names count only bare or with an agent-shaped argument; `command -v` is a
  lookup; renderer pre-checks moved to where an agent start is actually decided.
- **Root-cause class:** a control widened to catch an adversary the threat model does not have.
- **Invariant:** a control that blocks legitimate work is itself a failure; re-check after
  hardening (each case is now a test asserting it is NOT refused).

## F4. Upstream ratchets caught two shortcuts the agents took

- **Actual:** `check-max-lines-ratchet` failed on an `oxlint-disable max-lines` header added to
  `stable-owner.ts` (upstream file already at its 300-line cap), and
  `check-runtime-electron-ratchet` failed on a new runtime module importing `electron`.
- **Fix:** `stable-owner.ts` is byte-identical to upstream again; its backstop moved to a
  provider wrapper both callers pass. The refusal dialog moved behind a host port
  (`src/main/host/electron-netie-launch-refusal-notifier.ts`), installed at startup next to the
  other Electron ports.
- **Root-cause class:** suppressing a gate instead of meeting it.
- **Invariant:** do not weaken, skip or delete a check to force green.

## F5. Test-only type errors hid behind green vitest runs

- **Actual:** after all families landed, vitest was green but `tsc` showed 1409 (node) and
  512 (web) errors, all from Netie test files importing across the main/renderer boundary.
- **Fix:** renderer cases moved to renderer test files with the same drivers and assertions
  (case counts recorded per file), the IPC strip helper moved to `src/shared`, and test type
  errors fixed. All three upstream typecheck projects are at 0 errors, as on the baseline.
- **Root-cause class:** a gate run in a subset (vitest transpiles without typechecking).
- **Invariant:** prove the gate you claim; vitest green is not typecheck green.

## Measured before and after

Box: 4 cores, 15 GB, Node 22.22.0, pnpm 12.8.1. Install needed two workarounds (install only,
never committed): the `oxlint-plugin-anti-slop` GitHub tarball is 403 through this proxy, so the
pinned commit was fetched with git and pointed at with `file:` for install, then `package.json`
and `pnpm-lock.yaml` were restored; `node-gyp` was missing, so it was installed globally to
build `node-pty`. `pnpm run` re-verifies dependencies and hits the 403, so script bodies were
called directly (same commands).

| Check | Baseline (0001) | Stage 2 (0001 + 0002) |
|---|---|---|
| Typecheck node / web / cli (tsc --noEmit) | 0 / 0 / 0 errors | 0 / 0 / 0 errors |
| Electron bundle build (`run-electron-vite-build.mjs`) | exit 0, 52.5 s, peak 4.83 GiB | exit 0, 39 s |
| Upstream repo gates (8 from `pnpm lint`: reliability, max-lines, ts-nocheck, runtime-electron, readme links, node pin, localization x2) | 8 pass | 8 pass |
| oxlint, anti-slop (deny warnings), oxfmt on 153 changed files | n/a | clean |
| Full unit suite, CI env, 6 shards: files | 10966 | PENDING |
| passed / failed / skipped | 105738 / 59 / 1112 | PENDING |
| Netie gate tests (21 files) | 21 of 21 files fail (46 cases run, all fail; the rest cannot load) | 21 of 21 pass, 335 cases |
| Replay: fresh clone + apply, `git write-tree` | | `34bbdd7759480e8c74925ef6ca7569ce17792080` on both |
| LICENSE sha256 | `ff1b611f...112f3` | unchanged |

Upstream tests edited (5), each with the reason in the file: tray tooltip and window title now
assert `APP_DISPLAY_NAME`; the dashboard pop-out relay and drawer now assert the Netie board,
not the local store; the sidebar nav test mocks the Netie board source instead of the local
counts hook. None was skipped or deleted. Every upstream suite that exercises the local launcher
runs under the documented development override through one setup file
(`config/scripts/vitest-netie-local-launch-override.ts`); the Netie tests clear it per case.

## Not done / assumed

- **Not measured:** whether OpenVault serves `/v1/audio/transcriptions` or needs a seat token.
  No live OpenVault or Netie board endpoint was on this box; both were driven with fakes.
- **Not done (stage 3):** routing a launch to the Crew ticket runner (no wire contract exists
  yet); package name `orca`, `app.setName('Orca')`, data paths, electron-builder ids and the
  ~800 `Orca` UI strings; packaging (`electron-builder`) and e2e.
- **Known limits, by design:** a person typing into a shell; account login commands;
  shared-name agents started by a bare raw command with no agent-shaped argument and no launch
  fields; sessions a terminal daemon hosted before the gate; clients of the daemon socket or
  SSH relay that bypass main.
- `scripts/test_sibling_patches.py` is red on base and on this branch: 10 tests, 9 failures,
  identical on an untouched worktree of base `196b9f2`. Not touched, not skipped.
