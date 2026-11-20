# 2026-11-12 - sibling patch gate re-cut (6 lanes, PR #59)

Preflight: KB `D:\Netie-KB` absent in this cloud box. `INDEX.md` read; the 2026-10-05
ecosystem-lane row ("sibling patch gate is red on base") was the hit. PREFLIGHT: PARTIAL.

## Shape and why

6 background agents, one per sibling repo (constructor, OpenVault, Cortex, dms, Pointer,
Control). Isolated contexts, one shared checkout. Each lane could edit only its own
`docs/patches/<lane>-*.patch`; the parent owned `scripts/test_sibling_patches.py` and
`docs/patches/README.md` and applied shared edits from the reports. No commits or pushes by
agents. Why this shape: the 9 failures were independent per repo, and the only shared files
were two the parent could serialise. No judge agent: the parent re-ran each lane's gate test
before committing, then the whole of `make ci`. Wall time about 60 minutes, dms the slowest.

## Result (measured)

`make ci`: 30 files, laptop-ASCII clean, 46 script tests passed. GitHub `governed-docs`
green on `c4403b1`. Heads cut against: Pointer `b42b98d`, Control `93959c6`, constructor
`bfc7d3b`, OpenVault `3ba51cd`, Cortex `304bf84`, dms `ebe65cc`.

## F1. The parent said the gate could not be fixed from here, without checking

- **Expected:** check what the session can reach before reporting a blocker.
- **Actual:** the parent told the founder and wrote on PR #59 that the sibling repos were
  out of reach. They are public and the gate clones them itself. Corrected on the PR.
- **Repro:** read `scripts/test_sibling_patches.py`; every lane starts with a plain clone.
- **Root-cause class:** a blocker asserted from an access rule, not from a probe.
- **Invariant:** separate verified fact from assumption.

## F2. The parent committed a lane before its agent reported

- **Expected:** a lane is committed after its agent reports and the parent re-runs the gate.
- **Actual:** a stop hook asked for a commit while dms was mid-work. The gate test passed, so
  the parent committed the first cut (`c4403b1`). That cut turned one dms test red
  (`test_name_echo_01`, the `warehouse_<table>` lake alias). The agent's final cut fixed it and
  was committed after.
- **Repro:** apply `dms-netie-acl.patch` from `c4403b1` on dms `ebe65cc`, run
  `tests/test_name_echo_01.py`.
- **Root-cause class:** green gate read as done. The gate checks that a patch applies and its
  own tests pass; it does not run the sibling suite.
- **Invariant:** uncommitted is not done, and committed is not verified. Assert the artifact
  the sibling actually receives.

## F3. Green here hides sibling regressions

- **Expected:** a patch that applies does not break the sibling's own tests.
- **Actual (agents' measurements on patched clones):** Cortex 43 of its own tests fail (6
  web_fetch, 37 `/dms/query` 401). OpenVault 2 fail (duplicate `POST /api/crew/gate`).
  constructor passes only because one patch flips the sibling's script-order test.
- **Repro:** per lane, apply the series on the head above and run the sibling suite.
- **Root-cause class:** the gate's scope is narrower than the claim people read into it.
- **Invariant:** prove a gate can fail before trusting it green. This one cannot fail on a
  sibling regression. Open decisions are listed in `docs/patches/README.md`.

## F4. One assertion was retargeted, not loosened

The Cortex gate looked for `require_role("steward")` as a string in `dag_run.py`. Cortex now
injects the dependency. The test asserts three links instead: the route dependency, `app.py`
injecting `require_spend_key`, and `require_spend_key` being a steward check. The parent read
all three in the Cortex source before editing. R4 held: no check was weakened.
