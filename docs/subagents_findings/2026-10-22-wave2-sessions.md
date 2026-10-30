# 2026-10-22 - stage 2 wave 2 session shape

Preflight: KB `D:\Netie-KB` absent in this cloud box. `docs/subagents_findings/INDEX.md`
read with all three wave 1 findings (airgpt, freeide, freeroute). PREFLIGHT: PARTIAL.

## Shape

Why sessions and not Workflow agents or Task lenses: same reason as wave 1. Each fork needs
its own checkout, install and build. Wave 1 measured one Next.js build at about 11.6 GB
resident on a 15 GB box, so eight builds in one container would OOM or exhaust the disk
allowance. One container per fork isolates both.

| Count | Lens (one per session) | Context | Model |
|---|---|---|---|
| 8 | freeide-ext, control, crew-agent, crew-edge, crew-harness, netie-wiki, freeroute-core, freebuild | Isolated: own checkout of this repo at `claude/netie-ecosystem-rebrand-uq9q3z`, own `/tmp` upstream clone, no shared state | Fable (execute). Planning and the per-fork gate brief were done by the parent (Opus) from the catalog and the wave 1 findings |

- Sessions: `session_017vGA1rsUtXWmRz5DmfE78d` (freeide-ext), `session_01TJZnX9tpzwbLarSKjVJ5fC`
  (control), `session_018ZvvmbN2JWHKQt8j1cdxfY` (crew-agent), `session_01JdfwhiUb4QNWqxSX8mgg14`
  (crew-edge), `session_01Tm2EkZXF4yg5dde37bKqJ1` (crew-harness), `session_018d5qymgPn4fKMZ9t1JvELs`
  (netie-wiki), `session_01XUFERAzUWZRhx67FWADi2L` (freeroute-core), `session_01YBk1woSdFDqopTWUGBHjJf`
  (freebuild). Parent: `session_0168dMM52yirXZgXMymEBTNv`.
- Output branches: `claude/stage2-<slug>`, each a draft PR with base
  `claude/netie-ecosystem-rebrand-uq9q3z` (stacked on PR #43).
- Change from wave 1: children do not edit `docs/subagents_findings/INDEX.md` or `STATUS.md`.
  Wave 1 had an INDEX conflict on every child PR; with eight it would be eight. The parent adds
  the rows after verifying.
- Adversary is not the verifier: the parent replays `clone` + `apply` and runs each child's
  gate test on a fresh checkout before accepting a stage 2 claim.
- Wave 1 lessons passed into every brief: tests after a top-level await never run under
  `--test-force-exit`; measure the baseline build before claiming one; gate on behavior, not
  an upstream risk label.

## F1. Two catalog rows were left out on the catalog's own words

- **Expected:** "build all" covers every forkable row still at stage 1.
- **Actual:** `freeroute-9router` is `superseded_by: freeroute` ("do not ship both") and
  `crew-desk` says "ship only if a buyer asks for the desk". Neither was started.
- **Root-cause class:** YAGNI. A stage claim on a row nobody will ship is cost with no buyer.
- **Invariant:** a control that blocks legitimate work is a failure; the reverse also holds,
  work the catalog itself defers is not legitimate work yet. Founder can reopen either.

## F2. Catalog row `netie-memory` contradicts `scripts/ov_memory.py`

- **Expected:** one memory policy. The catalog row says mode `depend`, "depend on the
  package (mem0), wrap it, brand the wrapper", gate "See scripts/ov_memory.py".
- **Actual:** `scripts/ov_memory.py` lists `mem0` in `VENDORS` and `refuse_vendor` raises
  `MemoryDenied` for it ("fourth store refuse"). The file the row points to refuses the
  package the row says to depend on.
- **Repro:** `grep -n mem0 scripts/ov_memory.py`; compare with the `netie-memory` row in
  `ecosystem/catalog.json`.
- **Root-cause class:** two sources of truth for one policy, written at different times.
- **Invariant:** say what is measured and what is assumed. Not started; stays stage 0 until
  the founder picks one. `cortex-haystack` (mode `depend`) also stays 0: no caller needs it yet.

## Verification by the parent (2026-10-30)

The scheduled verification check-in (trigger `trig_01W6q9EbhwfiKoDWaTZWnnfv`) was disabled at
2026-10-22 23:48 UTC without firing, not by this session. The pass below was run by hand from
this session, which wrote none of the patches.

Replay: each branch's own `scripts/ecosystem.py clone` + `apply` into a fresh directory, then
`git add -A && git write-tree`, compared with the hash in that child's finding. LICENSE sha256
compared with the catalog row.

| PR | Row | Claimed stage | Replay tree | Matches claim | LICENSE |
|---|---|---|---|---|---|
| #48 | netie-wiki | 2 | `214d44def7a6` | yes | equal |
| #49 | freebuild | 2 | `c1d72e5f318b` | yes | equal |
| #50 | crew-harness | 2 | `1746a25167e4` | yes after `7035d25` (F3) | equal |
| #51 | crew-edge | 2 (series 0001-0003) | `731efbaed1bb` | yes | equal |
| #53 | control | 2 | `0f8422e1a84d` | yes | equal |
| #54 | crew-agent | 2 | `335de3197226` | yes | equal |

Not re-run by the parent: the upstream suites and gate tests of these six (the children's
numbers stand as reported, unverified here). Replay proves the patch is what the finding
describes, not that its tests pass.

## F3. crew-harness finding states the hash of a superseded cut

- **Expected:** the replay hash in a finding belongs to the patch on the branch.
- **Actual:** commit `0179612` recut `0002-gate.patch` (99 KB to 177 KB). The finding still
  states `1eae41fe5ca3` from the first cut; the recut replays to `1746a25167e4`. Replaying
  `9f6d8c1` gives `1eae41fe5ca3` exactly, so the old number was true for the old patch.
- **Repro:** worktree at each commit, `clone` + `apply crew-harness`, `git write-tree`.
- **Root-cause class:** a measured number that outlives the artifact it measured.
- **Invariant:** say what is measured and what is assumed. Sent to the crew-harness session
  to restate; no stage change.
- **Resolved:** `7035d25` on `claude/stage2-crew-harness` names both cuts with their own
  hashes (`1eae41fe5ca3` for `9f6d8c1`, `1746a25167e4` for `0179612`). Parent checked: that
  commit touches only the finding, the overlay is unchanged since the replay above.

## F4. freeroute-core gate test fails its own case once go test is allowed

- **Expected:** PR #47 keeps stage 1 only because its box could not run `go build` / `go test`.
- **Actual:** this box can. go1.24.7: `go build ./...` rc 0 on both trees. `go test ./...`
  stage 1: 48 packages ok, 0 fail; stage 2: 47 ok, `internal/proxy` FAIL. Gate tests
  (`-run TestNetieGate`): 0 of 17 pass on stage 1 (red, as required), 16 of 17 on stage 2.
  The failure is `TestNetieGate_Fail2BanAndFallbackOnIssuedCredentials`, 5 of 5 with
  `-count=5`: call 0 gets 401 instead of the fallback's 200.
- **Repro:** `ecosystem.py clone freeroute-core D && ecosystem.py apply freeroute-core D &&
  cd D && go test ./internal/proxy/ -run TestNetieGate_Fail2Ban -count=5 -v`.
- **Root-cause class:** a test that never ran. It was written and shipped without one run,
  so its first run is the first time anyone could see it fail.
- **Invariant:** a skipped test is a failing test; prove a gate can fail before trusting it.
- **Hypothesis, not proven:** upstream fallback tests use credential type `proxy` (the
  `IsProxyLike()` retry branch in `internal/proxy/proxy.go`); this test uses `openai`. Sent to
  the freeroute-core session. Stage stays 1, now for a measured reason.
- **Resolved:** the hypothesis held. `8318d9a` rewrote case 10 to the retry upstream really
  does for `openai` credentials (no `is_fallback`, `WithMaxProviderRetries(2)`); every
  issued-key assertion kept. Parent re-run, `-count=1`: `go test ./...` 48 packages ok, 0
  fail on both trees; 5304 passing on stage 1 (gate cases excluded), 5321 on stage 2 (5304
  plus 17); 71 skips on both, all upstream's; gate 0 of 17 on stage 1, 17 of 17 on stage 2,
  85 of 85 at `-count=5`; replay tree `a3447787dfdf` matches. Stage 2 holds. The row is
  raised by the freeroute-core session on its own branch, not here.

## Not done

- The three wave 1 PRs (#44, #45, #46) and PR #43 still wait on founder review. Nothing here
  merges them.
- `scripts/test_sibling_patches.py` stays red on the base (F2 of `2026-10-05-ecosystem-lane.md`).
  No wave 2 child was asked to fix it.
- freeroute (OmniRoute) stays at stage 1: its baseline build does not fit this box.
