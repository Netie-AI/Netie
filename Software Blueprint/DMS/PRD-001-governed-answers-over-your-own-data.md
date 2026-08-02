# PRD-001 - Governed answers over your own spreadsheets and databases

**Product:** DMS / Spaces
**Owner:** founder
**Status:** draft - not yet sliced
**Repos in scope:** `Netie-AI/dms`, `Netie-AI/Cortex`
**Created:** 2026-08-02

---

## 1. Press release

### Ask your company's data a question and get an answer you can put in front of an auditor

**Netie DMS turns the spreadsheets and databases an SME already runs on into something
you can ask questions of - and every answer arrives with the rows it came from, the query
that produced it, and a record of who was allowed to see it.**

Malaysian logistics and distribution SMEs run on Excel. The numbers that go into a
monthly report are assembled by hand, and when someone asks "where did this figure come
from" three weeks later, the honest answer is usually that nobody knows.

General AI assistants make this worse rather than better. They will answer confidently
from a spreadsheet they have half-read, and there is no way to tell a correct answer from
a fluent one.

DMS is built the other way around. A **Space** is a sandbox over the sources a person is
actually allowed to see. Ask a question inside it and you get a number, the rows behind
it, and the SQL that ran. Ask something the data cannot support and it **says so** rather
than guessing. Every change to the underlying records goes through an action that lands
in a tamper-evident ledger.

> "I stopped keeping a parallel spreadsheet to check the system's numbers, because I can
> click any figure and see the rows." - *warehouse operations lead, pilot customer*

Available as a hosted pilot or self-hosted on your own infrastructure. Your data does not
leave your machine unless you say it can.

---

## 2. FAQ

### External

**How is this different from asking ChatGPT to read my spreadsheet?**
Three things. Access is enforced in the data plane, not by asking a model nicely - a
question that reaches outside your Space is refused, not answered. Every answer carries
its rows and its SQL. And the system is measured on how often it is *confidently wrong*,
with the target at zero; it abstains rather than guesses.

**What happens when it does not know?**
It abstains and says what it would need. This is the feature, not a limitation. A system
that always answers cannot be trusted on the answers that matter.

**Does my data leave my machine?**
Only if you allow it. Model routing and the leave-machine decision are a separate gate
you control.

**Can it change my data, or only read it?**
Both, but writes go through a proposal you confirm, and the confirmation lands in the
ledger with what changed and who approved it.

**What does it run on?**
Excel and CSV today, Postgres for the control plane. Your existing files, not a migration.

### Internal - the questions we cannot answer yet

**Q: Is our answer quality good enough to sell?**
Not proven. `wrong=0` on a 376-item corpus, but only **47 items are human-verified**, so
under the rule of three the true error rate is bounded at **6.4 percent**, not under 1
percent. The corpus also caught **none** of the last five confidently-wrong defects found
in live use. We do not have a trustworthy quality number, and the first thing this PRD
buys is one.

**Q: Does the Space boundary actually hold?**
No. `live_ask` mints its manifest from `demo_acl()`, which allowlists every table
regardless of `space_id`. The correct functions exist, are unit-tested, and have no
production caller. **Two customers in one room is a demo we cannot currently give.**

**Q: Can the system write?**
Barely. The action registry has 25 entries and **one** is invocable - it exports a
PowerPoint. Amend proposes and confirms but changes no warehouse data. The USP chain
"Ask -> Clarify -> Answer -> Amend -> ledger" is missing its last two links.

**Q: Is the generated-SQL path ready?**
No, and this is the strategic risk. Answers today come from a hand-written keyword
cascade (~240 lines of regex). The intended replacement measured **17 confidently wrong
against a floor of zero** and is switched off. We cannot honestly sell either state, and
we cannot resolve it without a real user's questions - our own paraphrases are
self-confirming.

**Q: How close is the Palantir-style ontology?**
Closer than the marketing claim, further than the ambition. Real object types, link
types, action types with read/propose/apply classes, and a function registry exist and
are load-bearing. What is missing is lineage and the write path. **We do not say
"Palantir" externally** until there is a paying client and the F-gates are hardened -
that stays parked.

**Q: What would make us abandon this?**
No user in four weeks. The failure mode here is not capability, it is eight workstreams
at 80 percent and nothing finished.

---

## 3. Out of scope

- Palantir/AIP marketing parity, lineage, full column-level provenance (`H6`, parked)
- Google Sheets, or any source that is not a local file or Postgres
- CRAG / BIRD external benchmarks (parked behind Spaces)
- WASM or microVM isolation (host `tool_runner` is the path)
- The messaging/Closer vertical
- Multi-tenant hosting - self-host and single-tenant pilot only

---

## 4. Success assertion

> **WHEN** a person who is not the founder starts the stack from documented steps, opens
> a Space scoped to a subset of sources, and asks a question whose answer requires a
> table outside that Space, **THE SYSTEM SHALL** return an abstention naming the refusal
> - and when the question is inside the Space, return the answer, the contributing rows,
> and a drillthrough token that reproduces them.

Measured on the DMS envelope from `POST /v1/chat/ask`, not on Cortex-side state.

---

## 5. Epic decomposition

Ordered by **irreversibility**, not value. Two in flight at a time, at least one visible.

### Wave 1 - trust the instruments, then hold the boundary

| Epic | Repo | Contract | Depends on | Visible |
|---|---|---|---|---|
| **EPIC-001** Eval gate can fail | Cortex | none | - | no |
| **EPIC-003** Space boundary holds | DMS | none | founder decision | **yes** |

`EPIC-001` first because every number downstream is currently unfalsifiable. `EPIC-003`
paired with it so the wave produces something you can open and react to.

### Wave 2 - close the ungoverned paths

| Epic | Repo | Contract | Depends on | Visible |
|---|---|---|---|---|
| **EPIC-002** Contract identity + wheel | Cortex | additive | - | no |
| **EPIC-004** Manifest enforced on `/dms/query` | Cortex | none | EPIC-001 | partially |

`EPIC-002` is split per the contract-stability rule: the identity fix ships alone before
any packaging, because publishing a wheel over a dual module identity turns a latent
divergence into a live one inside `canonical_manifest_bytes`.

### Wave 3 - make it write

| Epic | Repo | Contract | Depends on | Visible |
|---|---|---|---|---|
| **EPIC-005a** `amend.apply` action type + tool_runner branch | Cortex | **additive** | EPIC-002 | no |
| **EPIC-005b** Confirm invokes `call_action`, receipt shows the diff | DMS | none | EPIC-005a | **yes** |

Three-epic contract pattern collapsed to two because the change is additive: the engine
gains an action, the contract gains an endpoint, DMS adopts it. `EPIC-005b` cannot ship
against the published contract, so it is genuinely blocked - not merely sequenced.

### Wave 4 - one surface, then the asset

| Epic | Repo | Contract | Depends on | Visible |
|---|---|---|---|---|
| **EPIC-007** One UI, not two | DMS | none | EPIC-005b | **yes** |
| **EPIC-008** Two-minute demo asset | DMS | none | all above | **yes** |

`EPIC-007` deletes `demo/dms-ui` in Cortex. Two UIs for one product is a maintenance tax
already causing stale cross-references.

### Deferred, with the condition stated

| Epic | Why not now |
|---|---|
| **EPIC-006** C7 - replace the keyword cascade | **Blocked on one real user.** 17 confidently wrong vs a floor of 0, and our own paraphrases cannot settle it. Revisit the day a customer asks questions we did not write. |
| **EPIC-009** Column lineage (`C9-full`) | Ontology depth. After a paying client. |
| **EPIC-010** `claim_n` 47 -> 310 | Not an epic - it is **1.5 days of your attention**, TTY-gated by design. Schedule it, do not assign it. |

---

## 6. Cross-product acknowledgement

Epics in this PRD that land in Cortex are engine work that other consumers inherit:

```
Serves: PRD-001 (DMS) EPIC-001, EPIC-002, EPIC-004, EPIC-005a
```

That line belongs in the Cortex PRD when it is written. AirGPT and Pointer both consume
the same manifest enforcement from `EPIC-004`, so it is engine work, not DMS work that
happens to live in the engine.

---

## 7. Feedback ledger

Append only. This table is the PRD's memory - it is how feedback given weeks ago lands in
the right epic instead of becoming a duplicate.

| # | Date | Raised in | Feedback | Routed to | Outcome |
|---|------|-----------|----------|-----------|---------|
| | | | | | |

---

## 8. Review

Silent read, 15 minutes, before slicing. The FAQ's internal section is the part to read
properly - the external section is the part we cannot yet fully support.

**Nothing in the press release may appear in any external asset until it traces to a
passing gate.** Today, the quote and the drillthrough claim would both be premature.
