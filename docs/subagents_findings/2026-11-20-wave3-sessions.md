# 2026-11-20 - wave 3 session shape (recut 2, plus a personal tool)

Preflight: KB `D:\Netie-KB` absent in this cloud box. `docs/subagents_findings/INDEX.md` read,
with `2026-10-05-wave1-sessions.md`, `2026-10-22-wave2-sessions.md` and
`2026-11-12-sibling-recut.md`. PREFLIGHT: HIT (the wave shape, the "children do not edit
INDEX or STATUS" rule and the parent-replays rule were all reused as written).

Founder ask, verbatim: "Continue check scale improve build in more sessions scale buuild all
in workflows and multiple sessions".

## Shape

Why sessions for the patch lanes: the same reason as waves 1 and 2. Each lane needs its own
sibling clone, its own install and the sibling's whole test suite, twice (unpatched and
patched). On 2026-11-12 the dms suite did not finish inside a container shared by six lanes.
One container per lane isolates CPU and disk.

Why workflows for the personal tool: its lanes share one small codebase, so they ran in this
session, each lane in its own git worktree of the fork, with a different agent checking each.
Two of its lanes did need their own container and went to sessions: the Docker image is about
9 GB (this box had 9 GB free) and the audio run is an hour of four-core speech-to-text.

| Count | Kind | Lens (one each) | Context | Model |
|---|---|---|---|---|
| 5 | cloud session | Cortex, OpenVault, constructor, Control, dms patch lanes | Isolated: own checkout of this repo at `claude/friendly-feynman-x4hd1v`, own sibling clone, branch `claude/recut2-<lane>`, draft PR stacked on #59 | Fable (execute) |
| 2 | cloud session | Docker deploy, audio accuracy (personal voice-capture tool) | Isolated, branches `claude/voice-docker`, `claude/voice-audio-eval`, no PR | Fable (execute) |
| 3 + 3 | workflow agents | build lanes api, page, accuracy; then one independent check each | Shared container, one git worktree per lane | Fable builds, Opus checks |
| 4 + n | workflow agents | review areas store, page, sorter, honesty; then one skeptic per finding | Shared container, read-only worktree at the reviewed commit | Fable finds, Opus refutes |
| 1 | subagent | PRD Agent routing of the founder ask | This checkout, read-only | Opus (judge) |

- Patch-lane sessions: `session_01N6JxFUTyTbepQ5qdiuBTMK` (Cortex),
  `session_01N6JxFRJf2xdr4hMzD1Perx` (OpenVault), `session_01N6JxFSYHcoLjAnD1wjn37V`
  (constructor), `session_01N6JxFR7W5Kg9AX9JAxsrxG` (Control),
  `session_01N6JxFTRJhFJbVG6b948gYW` (dms). Personal-tool sessions:
  `session_01N6JxFTfYhKgBPvyRn6wMzX` (Docker), `session_01N6JxFSGbHjxDdt1xHNeKM2` (audio).
  Parent: `session_01N6JxFRYUjhsrEoe6MWTEmn`.
- Children may edit only their own lane: its patch files, its own method in
  `scripts/test_sibling_patches.py`, its stack entry, its README section, one finding file.
  The parent owns `STATUS.md`, `INDEX.md`, the decision record and the ledgers.
- Adversary is not the verifier: the parent replays each lane on a fresh checkout and reruns
  the gate before merging it. Workflow lanes are each checked by an agent that did not write
  them.
- The workflow tool caps concurrency at CPUs minus 2, which is 2 on this 4-CPU box. Two
  workflows were run side by side to get 4.

## F1. The first proposal was refused by the repo's own intake, correctly

- **Expected:** a founder ask to "scale build all" starts sessions.
- **Actual:** the parent first proposed five patch-lane sessions to the PRD Agent. It
  returned NEEDS-YOU: four of the five patch conflicts are product decisions a session may
  not settle, no PRD holds a cross-product "patch-health" epic, and DMS ledger row F-TBD-10
  ("keep ONE product, DMS ... everything else archived") was unanswered. No session was
  started until the founder ruled. The rulings are quoted in
  `docs/decisions/DR-PROPOSED-parked-patches-yield-to-sibling-tests.md`.
- **Repro:** give the `prd-agent` subagent the ask and the five conflicts from
  `2026-11-12-sibling-recut.md` F3.
- **Root-cause class:** a broad ask read as a work order. On 2026-11-12 the same parent had
  re-cut six lanes without running the intake at all.
- **Invariant:** a control that blocks legitimate work is a failure; this one blocked
  illegitimate work and cost one question round. R4 held.

## F2. Two founder answers were free text and are being acted on as read

- **Expected:** each ruling is one of the offered options.
- **Actual:** constructor got "All can ur compilers also can" and Control got "Check
  carefully if they will cause any issues soovle". The parent read them as "either compiler
  is fine, ours included" and "solve it after checking for side effects", wrote both readings
  into that decision record and into the two session briefs, and told both sessions to stop and write a
  memo if a sibling test would have to change.
- **Repro:** read the two briefs (session ids above) against the quoted answers.
- **Root-cause class:** an interpretation recorded as a ruling.
- **Invariant:** separate verified fact from assumption. The readings are labelled as the
  agent's in the decision record. If either is wrong, the lane's PR is the place to say so.

## Results

Not known when this file was first committed. The parent appends them here, per lane, after
replaying each one.

State at 2026-11-20 03:05 UTC. Every child of this wave ran on Fable and hit the account's
Fable limit at about 01:59. The founder then ruled that nothing runs on Fable. A replacement
parent (`session_01N6JxFRqgMNSLVYd5A1tK96`, Opus) rebuilt the state from the transcripts and
pushed branches, and on the founder's 02:10 ask ("too many branches") folded the five patch
lanes into one track, branch `claude/recut2`, draft PR #63, executor
`session_01N6JxFSgYhMwLMkHASHXL38` (Opus). The voice capture lanes became one track, branch
`claude/voice-capture`, executor `session_01N6JxFSe19mgswm8NxDVbZh` (Sonnet).

| Lane | Built by | Carried into #63 | Verified by | Result |
|---|---|---|---|---|
| OpenVault | Fable lane, PR #60 (closed into #63) | 39d3199 | earlier parent replay | OpenMW suite unpatched 1504 passed, patched 1619 passed, 0 failed. Gate now also runs `tests/test_access_routing.py` (bb0103f): old cut 2 failed, new 20 passed |
| Control | Fable lane, PR #61 (closed into #63) | 4e930aa | not yet replayed by a second agent | Lane report: sibling suite unpatched 173 passed, patched 194 passed |
| Cortex | Fable lane, PR #62 (closed into #63) | 71eb2a0, 8fcb420 | T1 executor (d79b82a) | Wide 2729 vs 2745 passed, whole 5280 vs 5296 passed, 0 failed both; the diff is the 16 added test ids |
| constructor | T1 executor (7d2ed1b) | 95ac504 | independent T1 subagent (fcbabd2) | 26 patches cut to 3; unit 118/118 both, e2e 52/52 both, 62 compiler tests, no pin `tests/` file touched |
| dms | T1 executor | not yet | not yet | In progress at 03:05 |
| Voice audio eval | Fable lane, woke on its own at 02:59, e4e831c | to `claude/voice-capture` | T2 executor, asked to replay | Claimed: breeze-asr-25 52/59, large-v3-turbo 48/59 end to end, clean text 57/59 |
| Voice Docker | T2 executor | not yet | not yet | In progress at 03:05 |

Open founder decisions: D1 (OpenVault skill and mcp signpost rows), Control withheld rows,
Cortex F3 (chat gate needs one Cortex test edited, or drop the gate), constructor strict
`emit` on app nodes, and acceptance of the proposed DR via PR #59.

### F3. Background tasks woke two stopped Fable sessions

- **Expected:** a session stopped at a usage limit, then idle, does no more work.
- **Actual:** the Cortex lane (02:13) and the audio lane (02:59) each resumed on Fable when
  a background task they had started before the limit finished, and each pushed. The
  founder's rule was that nothing runs on Fable. The work was usable and is being verified,
  but it ran on the excluded model and raced the replacement lanes on the same branches.
- **Repro:** start a long `run_in_background` command in a session, let the session go
  idle on a usage limit that resets before the command ends.
- **Root-cause class:** a stop that covers turns but not the timers and tasks that start
  turns.
- **Invariant:** a control that blocks legitimate work is a failure, and the converse: a
  stop that does not stop is not a control. Archiving the session (which releases its
  container) is the stop that holds; an interrupt is not.
