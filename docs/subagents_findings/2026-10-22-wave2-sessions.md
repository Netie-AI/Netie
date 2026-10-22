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

## Not done

- The three wave 1 PRs (#44, #45, #46) and PR #43 still wait on founder review. Nothing here
  merges them.
- `scripts/test_sibling_patches.py` stays red on the base (F2 of `2026-10-05-ecosystem-lane.md`).
  No wave 2 child was asked to fix it.
- freeroute (OmniRoute) stays at stage 1: its baseline build does not fit this box.
