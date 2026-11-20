---
status: proposed
date: 2026-11-20
decision-makers: founder
---

# DR (proposed, unnumbered) - Parked patches yield to the sibling's own tests

No number yet on purpose: the PRDs in this repo already cite `DR-0003` to `DR-0005` meaning
decision records that live in product repos. The founder assigns a number on acceptance.

The five answers quoted below are the founder's, given in session on 2026-11-20 to direct
questions. The general rule built on them (the numbered list under "Decision Outcome") is the
agent's proposal. Merging PR #59 accepts it; rejecting the PR reopens it.

## Context and Problem Statement

`docs/patches/` holds patch series for sibling product repos that this repo cannot push to.
`scripts/test_sibling_patches.py` proves each series applies on a pinned sibling commit and
that the patches' own tests pass. It does not run the sibling's own suite.

The 2026-11-12 re-cut (PR #59) measured what that gap hides. With our series applied:

- Cortex: 43 of its own tests fail (6 on the built-in `web_fetch`, 37 on a `/dms/query` gate).
- OpenVault: 2 fail, because a patch registers a second `POST /api/crew/gate`.
- constructor: its suite passes only because one of our patches rewrites one of its tests.
- Control: the patched board shows nothing past about 48 open issues.
- dms: the Netie access guard covers one answer path of several, and the patch fails dms lint.

The PRD Agent (`Internal/Agents/AGENT_SYSTEM.md` sections 1, 4, 5) routed four of these as
founder decisions, refused to let any re-cut session start before a ruling, and pointed at
DMS ledger row F-TBD-10 (2026-10-01, "keep ONE product, DMS ... everything else archived")
as unanswered.

## Considered Options

1. Hold the 2026-10-01 focus: freeze every non-DMS lane, fix only plain defects.
2. Scale all five lanes, one session per sibling, with a ruling per conflict.
3. Leave PR #59 as it is, conflicts listed, nothing started.

## Decision Outcome

Option 2. The founder's answers, verbatim:

| Question put to the founder | Answer |
|---|---|
| Does the F-TBD-10 focus still hold for the patch lanes? | "No, scale all five products" |
| Cortex `web_fetch`: built-in with its guard, or only through the tool runner? | "Both, if possible (Recommended)" |
| Cortex `/dms/query`: key required, or keyless? | "Keyless stays allowed" |
| constructor: which compiler is the real one? | "All can ur compilers also can" |
| Control: what should the board do past the budget? | "Check carefully if they will cause any issues soovle" |

How the two free-text answers are read (the agent's reading, open to correction):

- constructor: either compiler is acceptable, ours included. The session prefers the repo's
  own `core/constructor.js`, keeps our strict compiler only where a check cannot live in core,
  and never edits a test the constructor repo wrote.
- Control: solve it, after checking that the fix breaks nothing that reads the board.

The rule this sets for every lane, now and later:

1. A parked patch may not edit, reverse, skip or delete a test the sibling wrote. If keeping a
   behaviour needs that, the lane stops on that behaviour and writes a decision memo.
2. A lane is done when the sibling's own suite, run unpatched and patched on the pinned
   commit, shows no failure the baseline does not have. Gate green alone is not done.
3. Where a ruling retires a behaviour, the gate assertion for it is replaced by one that
   proves the new intent. It is not deleted and nothing else is loosened.
4. The five sessions are ticket runs that re-cut series already in this repo. They create no
   epic and no product. Nothing here is pushed to a sibling repo (`CLAUDE.md` rule 9).

## Consequences

- `/dms/query` stays reachable without a key in Cortex. The `require_role("viewer")` gate on
  it leaves `cortex-role-execute.patch`. DMS PRD-001 EPIC-004 is titled "Manifest enforced on
  `/dms/query`"; whether that epic also expects a key was not checked for this record.
- If `web_fetch` cannot go through the tool runner without changing Cortex's tests, the
  Cortex lane stops there and the question comes back to the founder.
- F-TBD-10 is answered for the patch lanes only. Its other clauses (no new router, crew,
  planner; OpenVault as key box) are not touched by this record.
- Seven cloud sessions ran at once on 2026-11-20 (five patch lanes, two for a personal tool).
  `DR-0001` item 9 counts epics, not sessions; the PRD Agent's reading is in
  `docs/subagents_findings/2026-11-20-wave3-sessions.md`.

## Confirmation

Each lane's finding (`docs/subagents_findings/2026-11-20-recut2-<lane>.md`) carries the
sibling suite counts, unpatched and patched. The parent replays each lane on a fresh checkout
before merging it. There is no automated enforcer for rule 2 yet: `make ci` still runs only
the gate. Until one exists, rule 2 is checked by replay and stated as such.
