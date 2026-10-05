# 2026-10-05 - stage 2 wave 1 session shape

Why sessions and not Task lenses: each fork needs its own checkout, install and build, which
is hours of isolated work. Why only three: stage 2 cost per fork is unmeasured, and the
three forks below feed the products STATUS.md names first. The result sets the estimate for
the other ten.

| Count | Lens (one per session) | Context | Model |
|---|---|---|---|
| 3 | freeide (opencode), freeroute (OmniRoute), airgpt (LibreChat) | Isolated: own checkout of this repo at branch `claude/netie-ecosystem-rebrand-uq9q3z`, own `/tmp` upstream clone, no shared state | Fable (execute). Opus was not used: planning was done by the parent from the catalog |

- Sessions: `session_01MfJGni7VgpRR7pobcdJWC8` (freeide), `session_0128EZhGFeJFKbhZSFx71x6m`
  (freeroute), `session_0168dMM52yirXZgXMymEBTNv` (airgpt). Parent: `session_01G3NMN2aqRy1S8LcV6Wo7Lg`.
- Output branches: `claude/stage2-freeide`, `claude/stage2-freeroute`, `claude/stage2-airgpt`,
  each a draft PR with base `claude/netie-ecosystem-rebrand-uq9q3z` (stacked on PR #43).
- Adversary is not the verifier: the parent verifies each child's stage claim by replaying
  `clone` + `apply` and running its test on a fresh checkout, not by reading its report.
- Preflight: none of the three sessions can read `D:\Netie-KB`. PREFLIGHT: MISS.
- Not started: the other 10 forks, and any nightly routine. Both wait for PR #43 to merge,
  because a routine fires against `main`, where `ecosystem.py` does not exist yet.
