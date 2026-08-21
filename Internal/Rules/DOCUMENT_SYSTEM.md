# Netie document system

The naming law. Which documents may exist, what each answers, who owns it, where it
lives, and how it is numbered.

If a file does not fit one of the eight tiers below, it does not get created.

Version 1.0 - 2026-08-02. Supersedes the ad-hoc conventions in every repo.

---

## 0. The one-page answer

```
  TIER 0   CONSTITUTION      NETIE.md                        founder      almost never changes
     |
  TIER 1   ROADMAP           STATUS.md "Now / Next / Later"  founder      every session
     |
  TIER 2   WHITE PAPER       WP-###                          founder      per market thesis
     |
  TIER 3   PRD               PRD-###                         founder+mkt  per buyer-visible slice
     |
  TIER 4   TAS               TAS-<PRODUCT>                   tech lead    per product
     |
  TIER 5   DECISION RECORD   DR-####                         whoever      per irreversible choice
     |
  TIER 6   EPIC              EPIC-###                        founder      per slice of a PRD
     |
  TIER 7   TICKET            <REPO>-###                      anyone       per agent run
```

Read down, not up. A ticket that cannot name its epic is unscoped. An epic that cannot
name its PRD is a hobby.

---

## 1. Why this shape, and where it departs from textbook practice

The chain Vision -> Roadmap -> PRD -> RFC/ADR -> Epic -> Ticket exists to keep many
humans who cannot all talk to each other aligned across months. Netie is four humans in
one estate, and agents that execute in hours.

So three deliberate departures, each with a reason:

**RFC and ADR are one document, not two.** The textbook distinction is real - an RFC
proposes a change not yet made, an ADR records one already made - but at this size it
costs two documents to express one thing. Instead: open a Decision Record with
`status: proposed` **as a pull request**. The PR is the RFC. The discussion thread is the
review. On merge, flip to `status: accepted`. One file, one number, one history, and git
already stores the debate. This is Rust's mechanic (the PR number becomes the ID)
collapsed onto Nygard's file format.

**The PRD opens with a press release.** A PRD written by the person who will also approve
it is a memo to yourself with extra headings - this is Marty Cagan's charge against the
form, and it lands here with force given the estate is already eight workstreams at 80
percent. So Tier 3 uses Amazon's working-backwards shape: write the announcement first,
then the FAQ of questions you cannot yet answer. Rejection is the expected outcome. It
also produces marketing copy as a by-product, which matters when hiring a marketing
specialist before the first customer.

**Epics are thin.** An epic normally holds a quarter of human work together across a team
that cannot see each other's tickets; Atlassian calibrates two or three per team per
quarter. At agent speed the natural batch is hours. So an epic here is a **GitHub Issue
with the `epic` label and a task list**, not a document. It exists only to give tickets a
parent and to make cross-repo blocking visible.

What is skipped entirely, and why: sub-tasks (one more nesting level, zero coordination
bought), story points and velocity (estimating agent work is estimating token spend -
measure that directly), quarterly OKRs (pre-revenue, key results would be outputs wearing
outcome clothes), a Definition of Ready checklist (replaced by the prompt test in Tier 7),
and a wiki of any kind (Confluence, Notion-as-docs, GitHub Wiki all run parallel to the
repo, which is the structural reason they rot).

---

## 2. The tiers

### Tier 0 - CONSTITUTION

| | |
|---|---|
| **File** | `D:\Netie\NETIE.md` - exactly one, forever |
| **Answers** | What business are we in, which planes are ours, what will we refuse to build |
| **Owner** | Founder only |
| **Changes** | By pull request with a stated reason. A few times a year at most |
| **ID** | None. There is one |

Its value is that it is stable. Section 6 - what we deliberately do not build - is the
most valuable page in the estate, because it is the only one that closes arguments.

### Tier 1 - ROADMAP

| | |
|---|---|
| **File** | The `Now / Next / Later` block inside each repo's `STATUS.md` |
| **Answers** | What is in flight, what is being validated, what is a bet |
| **Owner** | Founder |
| **ID** | None |

Three headings. Problems, not features. **No dates.** Maximum three items in Now.

The rule that makes it work: anything sitting in Now for more than two appetites is
killed or moved to Later, automatically, without a meeting. State it so it fires on its
own.

**Do not create a roadmap document, buy Productboard, or write quarterly OKRs.** With four
people a roadmap tool is a mirror.

### Tier 2 - WHITE PAPER

| | |
|---|---|
| **Path** | `D:\Netie\White Paper - Why\WP-###-kebab-title.md` |
| **Answers** | Why does the world need this, and why can existing tech not do it |
| **Owner** | Founder |
| **Audience** | External - investors, design partners, technical buyers |
| **ID** | `WP-001`, `WP-002`, ... never reused |

One per thesis, not one per product. `WP-001` is the ecosystem argument: why custody,
governance and applications belong to one company and what the combination does that
neither does alone.

### Tier 3 - PRD

| | |
|---|---|
| **Path** | `D:\Netie\Software Blueprint\<Product>\PRD-###-kebab-title.md` |
| **Answers** | If this shipped and worked, what would the announcement say - and what can we not answer yet |
| **Owner** | Founder; marketing hire co-writes from month two |
| **ID** | `PRD-001` upward, globally unique across products |

Structure, in order:

1. **Press release** - one page. Headline. Subheading naming the customer and the
   benefit. The problem in the customer's own words. The solution. A quote from a
   customer who does not exist yet. Call to action.
2. **FAQ** - allowed to be longer than the release. External questions, then internal
   ones. **The internal FAQ is where the honesty lives**: what could make this fail, what
   we are assuming, what we would have to be right about.
3. **Out of scope** - an explicit list. A PRD without this is a wish.
4. **Success assertion** - one sentence, testable, in the customer's terms.

**Review ritual:** the silent read. Fifteen minutes reading and annotating with nobody
talking, then discussion. Once a fortnight, immediately before the betting table. It is
the only recurring meeting needed.

**Hard rule** (NETIE.md rule 1): every claim in a PRD must be traceable to a passing gate
before it appears in any external asset. The `README` WASM claim already in the Cortex
tree is the counter-example - a public claim of a control that has zero production
callers.

### Tier 4 - TAS (Technical Architecture Specification)

| | |
|---|---|
| **Path** | `D:\Netie\TAS\TAS-<PRODUCT>.md` - one per product, no number |
| **Answers** | How is this built, what are its boundaries, what does it depend on |
| **Owner** | Technical specialist |
| **ID** | `TAS-CORTEX`, `TAS-OPENVAULT`, `TAS-DMS`, `TAS-SPACE`, `TAS-AIRGPT`, `TAS-POINTER` |

Required sections: purpose in one line; the plane it occupies; the HTTP or library
surface it exposes; what it depends on and what depends on it; data stores; trust
boundaries and what enforces each; what is **shipped vs scaffold**, marked honestly; and
the verify commands that prove it.

A TAS is a living document, updated when the architecture changes. It is **not** a plan -
plans are Tier 6. If a section describes something that does not exist, it is marked
`PLANNED` inline or it does not appear.

### Tier 5 - DECISION RECORD

| | |
|---|---|
| **Path** | `<repo>/docs/decisions/DR-NNNN-kebab-title.md` - in the repo the decision binds |
| **Answers** | Why is it this way, what did we reject, what would make us reverse it |
| **Owner** | Whoever made the call |
| **ID** | `DR-0001` upward per repo. Four digits, zero-padded, sequential, **never reused** |

Frontmatter: `status`, `date`, `decision-makers`.
Statuses: `proposed` | `accepted` | `superseded by DR-NNNN`. Three, not eight.

Body: Context and Problem Statement / Considered Options / Decision Outcome /
Consequences (including the negative ones) / **Confirmation**.

**Confirmation is the section that earns its keep.** It names the test that proves the
decision is still honoured, and it must resolve to a real file. The estate already
contains the failure mode: rule `R-0001` names `tests/invariants/test_envelope.py`, which
does not exist. A decision that names a non-existent enforcer is a wish.

**Superseded records are kept and marked. Never deleted, never edited.**

**Threshold - write a DR only when at least one holds:**
- it crosses a repo boundary
- it touches the contract, the ledger, the manifest enforcer, or a protected path
- it is expensive to reverse
- an agent will otherwise re-litigate it next session

Everything else is a commit message.

**Review rule, stolen from Squarespace and worth more than any template field:** a
blocking comment must be written as **"Yes, if ..."**, not "No, because ...". A blocker
has to state what would make it a yes. The failure mode here is not shallow review, it is
a comment thread with no end date.

`DR-0001` in every repo is always "Record decisions in this repo" - the bootstrap record.

### Tier 6 - EPIC

| | |
|---|---|
| **Where** | GitHub Issue with label `epic`, in the repo that owns the most work |
| **Answers** | Which buyer-visible slice does this cluster of tickets deliver |
| **Owner** | Founder |
| **ID** | `EPIC-###` in the title, e.g. `EPIC-004: Space boundary actually holds` |

An epic is a **task list of ticket links** plus four lines: the PRD it serves, the
acceptance assertion in customer terms, the appetite (see cadence), and the cross-repo
dependencies.

Cross-repo blocking is expressed in the epic body as an explicit list, because GitHub's
native blocking does not cross repositories:

```markdown
Blocked by: Netie-AI/Cortex#412, Netie-AI/OpenVault#88
Blocks: Netie-AI/dms#31
```

#### No orphan tickets, ever (founder, 2026-08-21)

**Every ticket has a live parent epic. There is no exception and no grace period.**

A ticket whose parent is closed is an orphan, and an orphan is unscoped work that will be
re-derived from memory by whoever finds it next. Closing an epic over unfinished work
orphans every open child, so **an epic may not be closed until each open child has been
re-parented, closed, or parked with an unlock condition.**

When a ticket classifies under no existing epic, a new epic is generated to hold it -
**subject to the amendment gate below, which wins.**

#### The amendment gate wins over the no-orphan rule

**A generated epic may hold only work that an existing PRD clause already authorizes.**
Work with no PRD clause still stops at the founder as a PRD amendment.

Without this line the no-orphan rule repeals the amendment gate by side effect: an agent
forbidden to widen a PRD would be *required* to manufacture a parent for anything handed
to it, and the appetite becomes meaningless. Both rules hold together: **no ticket may be
an orphan, and no agent may invent scope.**

Repo-infrastructure defects that serve no PRD clause - a malformed `.gitmodules`, a broken
CI runner - are **exempt**. Generating a Tier 6 for a one-line infra fix manufactures fake
structure. Fix them and close them.

#### Open epic vs in-flight epic - they are counted differently

| State | Means | Counted against WIP? |
|---|---|---|
| **Open** | A live parent of record. Its children are not orphans | **No** |
| **In flight** | A ticket runner is authorized to work it now | **Yes** |
| **Queued** | Open, parented, deliberately not being built | **No** |

The WIP limit constrains **in-flight** epics only. This is not a loosening: it is the only
way both laws can hold at once, because the no-orphan rule requires as many live parents as
the board has ticket clusters, while the WIP limit deliberately allows two active lanes.

An epic moved to queued **keeps its children**. Closing it to free a slot re-creates the
orphans this rule exists to prevent.

### Tier 7 - TICKET

| | |
|---|---|
| **Where** | GitHub Issue in the repo where the work happens |
| **Answers** | What is broken, what does done look like from the customer's seat, what exactly should the agent do |
| **Owner** | Anyone |
| **ID** | GitHub's own number, referenced as `<REPO>-###` in prose |

**Sizing rule: one ticket is one agent run plus one adversarial verification.**

Required body sections:

```markdown
## Problem
What is wrong, with file:line evidence. Not a feature description.

## Acceptance
WHEN <condition> THE SYSTEM SHALL <observable behaviour>.
Asserted on the artifact the customer receives, never an intermediate one (R-0001).

## Why it is not a one-liner
The trap. If there is no trap, this may be a commit rather than a ticket.

## Step
current: 3 / 7 - "gate wired, corpus not re-run"

## Agent prompt
> The literal prompt to paste. Names the files, the acceptance signal, and the
> failure mode. If this cannot be written, the ticket is not ready.
```

**Definition of Ready** is a writing test, not a checklist: *can the agent prompt be
written?* If not, the ticket is not ready.

**Definition of Done** is two conditions, both required:
1. The acceptance assertion goes green when a **different** agent run verifies it
   (NETIE.md rule 3 - the adversary is never the verifier).
2. The full corpus is re-run and nothing valid became refused (rule 5).

A ticket moves to closed **only** by editing its parent epic's task list in the same
action. Closing without updating the parent is how a plan silently drifts from reality.

**A ticket with no live parent may not be worked.** It goes back to the PRD Agent for
re-parenting first. "It was obviously in scope" is how a closed epic's remainder becomes
permanent unscheduled work.

---

## 3. Netie-KB is not in this chain

**Netie-KB is the distillation record, not the ticket system.** It captures what was
learned from Claude and Cursor sessions and promotes recurring lessons into rules. Its
record types stay as they are:

| Prefix | Type | What it is |
|---|---|---|
| `R-####` | rule | A binding invariant |
| `W-####` | workflow | A repeatable procedure |
| `F-####` | finding | Something learned, with evidence |
| `A-####` | attack | A proven way to break something |

The relationship runs one way: **a ticket may cite a rule; a finding may become a rule; a
rule may be the `Confirmation` of a decision record.** Tickets never live in Netie-KB, and
KB records never live in GitHub Issues.

Before it can be cited at anyone, `kb.py validate` must exit 0. It currently exits 1 with
roughly 33 errors, including laptop-ASCII violations inside the rule corpus itself. **A
rules engine that fails its own rules cannot be quoted in a code review.** Fix that before
adding any new record type.

---

## 4. Plan-to-ticket automation

The requirement: when Claude or Cursor produces a plan, it should become a parent issue
plus step issues automatically, each step carrying its own prompt, each tracking which
step it reached, and closing a step should update the original plan.

### The shape

```
  Claude/Cursor writes    ->   plan file in repo      ->   sync script    ->   GitHub Issues
  a plan                       docs/plans/PLAN-###.md      (idempotent)        1 epic + N tickets
                                     ^                                              |
                                     |                                              |
                                     +---------- status written back ---------------+
```

### Rules that make it not become a mess

1. **The plan file is the source of truth, the issues are the projection.** Never the
   reverse. A human closing an issue in the GitHub UI triggers a write-back to the plan
   file; the plan file is what gets reviewed in a PR.
2. **Idempotent by stable key.** Each step carries a `key:` in the plan file. The sync
   matches on that key, so re-running never duplicates issues. Without this, every
   re-run doubles the backlog.
3. **One step = one agent run.** If a step's prompt cannot be written in one paragraph,
   split it before syncing.
4. **The step counter lives in the issue body**, not in a label. Labels are for filtering,
   not state.
5. **Closing requires a verification reference.** The close comment must link the run that
   verified it, and it must be a different run than the one that implemented it.

### Where it runs

Not a new service. A script in each repo (`scripts/sync_plan_issues.py`) plus a GitHub
Action on push to `docs/plans/**`. GitHub Projects gives the board view for free and reads
the issues directly.

**Do not build a dashboard page in OpenVault for this.** OpenVault is plane 2 - keys,
routing, and the leave-machine gate. A project-management surface there would be the
third orchestrator problem in a different costume.

---

## 5. Cadence

**Appetite, not sprints.** Two weeks. The number comes first and the design fits inside
it. A slice that does not land in its appetite is **cancelled by default, not extended.**

The betting table is the founder alone, thirty minutes, every second Friday, straight
after the PRD silent read.

No standups, no sprint planning, no story points, no retro ceremony. When something goes
wrong, file a finding.

The circuit breaker exists to fix one specific named pathology: eight workstreams between
60 and 90 percent and none at 100. Adopt it for that reason and say so out loud, or it
will be the first thing dropped.

---

## 6. Tooling

| Need | Use | Not |
|---|---|---|
| Roadmap | `Now / Next / Later` in `STATUS.md` | Productboard - solves inbound feedback volume, a problem at customer 50 |
| Decision debate | GitHub PR on the DR file | Confluence, Google Docs - they run parallel to the repo, which is why they rot |
| Tickets and epics | GitHub Issues + Projects | Jira - its value is permissions across many teams; you are four people who all have root. Linear free tier caps at 250 issues |
| Distilled learning | Netie-KB in git | anything else |
| Comms | One Slack workspace, one channel per slice | a channel per repo *and* per initiative - four people cannot populate eight channels |

Accept that Slack free-tier history disappears. Durable knowledge belongs in Netie-KB, not
in chat.

---

## 7. Naming rules that apply everywhere

1. **IDs are never reused.** Not after deletion, not after supersession.
2. **No dates in filenames** outside `docs/bin/` or an archive folder. A dated filename is
   a snapshot pretending to be a document.
3. **kebab-case** for the title portion; the ID prefix stays uppercase. `PRD-003-space-boundary.md`.
4. **Laptop-ASCII only** in every document listed here (R-0012). No em dash, no curly
   quotes, no arrow glyphs. Use `-`, `->`, `'`, `"`, `...`.
5. **Generated files carry a generated marker** in the first three lines and are never
   hand-edited (R-0009).
6. **One churn file per repo.** `STATUS.md`, capped at 60 lines. Everything else in the
   repo is stable or generated.
7. **Every artifact is a file in git, changed by pull request, checked by CI.** The moment
   an artifact lives somewhere CI cannot see it, it starts drifting.

---

## 8. What makes this work, rather than becoming shelf-ware

Three mechanisms. Without them this is just more markdown.

1. **`enforced_by` resolves to a real file, checked in CI.** For rules, decision records
   and tickets alike. This turns doc drift into a build failure rather than a discipline
   problem. It is the single highest-leverage line in this document.
2. **The agent that wrote the code never verifies it.** Encoded in the ticket lifecycle,
   not in a habit: a ticket moves to done only through a verification event attributed to
   a different run.
3. **Every claim traces to a passing gate before it goes external.**

The reason this chain is shaped differently from a normal company's is worth stating
plainly. In an organisation where humans implement, documents exist to align people
*before* work starts. Here, work starts almost instantly and cheaply - so the documents
exist to prove the work was right *after* it finishes. That is why the weight sits on
acceptance assertions and verification, and why the planning tiers are deliberately thin.
