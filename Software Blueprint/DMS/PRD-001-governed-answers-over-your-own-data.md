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
production caller. Portable contract in Netie `scripts/dms_space_acl.py`: named warehouse
bind, SQL required, row copy, abstain a row that declares another table, abstain Cortex
DuckDB for a DMS-bound Space, abstain SQL that names an ungranted table. **Two customers in one room is a demo we cannot currently
give** until that contract is the production caller.

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
> the SQL that ran, and a drillthrough token that reproduces them. A Space with no
> warehouse bind, or an answer with no SQL, abstains. SQL that names a table
> outside the Space grant abstains. A Cortex DuckDB ask for a
> DMS-bound Space abstains. Row copies so a caller mutation cannot punch the warehouse.

Measured on the DMS envelope from `POST /v1/chat/ask`, not on Cortex-side state.

Licensed bootstrap when `Netie-AI/dms` is reachable:

```
uv add git+https://github.com/Netie-AI/Netie.git
from netie.dms import answer_or_abstain, browse_or_abstain
```

`chat_mode=True` abstains (AnythingLLM overlay). SQL that names an ungranted table abstains. A Cortex DuckDB warehouse id on a DMS-bound Space abstains. Do not overlay AnythingLLM.

---

## 5. Epic decomposition

Ordered by **irreversibility**, not value. Two in flight at a time, at least one visible.

### Wave 1 - trust the instruments, then hold the boundary

| Epic | Repo | Contract | Depends on | Visible |
|---|---|---|---|---|
| **EPIC-001** Eval gate can fail | Cortex | none | - | no |
| **EPIC-003** Space boundary holds | DMS | `scripts/dms_space_acl.py` | founder decision | **yes** |

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
| F-TBD-4 | 2026-09-26 | DMS session (founder, relayed on dms#277) | Measure step: "suggest confirm while doing multiple adhoc sql". Cortex suggests measures, steward confirms; ad-hoc generated SQL may answer simple aggregates under a distinct non-certified badge with an "unconfirmed measure" line; research brief first. Auto-derived measures presented as certified stay refused | Netie-AI/dms#277 CONNECT-ASK umbrella (open), change 3 | decision recorded; lanes dms#282, dms#283, dms#284. No new ticket |
| F-TBD-5 | 2026-09-26 | DMS session (founder) | Learning loop: collect every failure reason (abstain, WRONG, adversary finding, steward correction) per Space and industry; solve, certify by deterministic verifier + independent adversary; distil survivors into per-industry frames (ontology templates, plan templates, verified queries); later distil a smaller planner by RL from verifier feedback | none - PRD amendment | NEEDS-YOU. Draft in section 9, AMEND-F-TBD-5. Conflicts with section 3 (single-tenant) and NETIE.md s1 ("intelligence is bought") for the planner part |
| F-TBD-6 | 2026-09-26 | DMS session (founder) | Defect: SQL-source ingest never syncs bronze to Cortex's serving warehouse; two-file topology cannot EXPLAIN/execute Space SQL until `scripts/sync_bronze_to_serving.py` is run by hand | Netie-AI/dms#277 (open) | BUILD_NOW - ticket for epic-agent. Verified: `apps/api/dms_api/wiring.py:247` `sql_source_ingest` has no sync call; only caller of `maybe_sync_bronze_to_serving` is `packages/executor/dms_executor/batch_ingest.py:252` |
| F-TBD-7 | 2026-09-26 | DMS session (founder) | Defect: one bronze name starting with a digit (`bronze.2024_sales`) makes every generated-SQL ask on that Space abstain `submit_failed`, even SQL not touching it | Netie-AI/dms#277 (open) | BUILD_NOW - ticket for epic-agent. Verified: `packages/executor/dms_executor/manifest.py:199,223` `cortex_row_predicates` raises `manifest_key_invalid` for the whole Space; `bronze.py:46` `_safe_table_stem` lets a digit-first stem land. Fix at landing or refuse named at ingest; never loosen the key rule |
| F-TBD-8 | 2026-09-26 | DMS session (founder) | Defect: a second Space ingesting the same source overwrites the shared bronze table; first Space abstains `validate:ungranted` and its stored ontology points at rewritten rows | Netie-AI/dms#277 (open); also breaks Netie-AI/dms#173 EPIC-020b acceptance "into bronze under the Space" | BUILD_NOW - ticket for epic-agent. Verified: `bronze.py:125` `_claim_table_name` treats same source string as same owner regardless of `space_id`; registry keyed on `table_name` (`bronze.py:85`, `:168`). If the registry key changes, DR first |
| F-TBD-9 | 2026-09-26 | DMS session (founder) | Defect: SQL-source ingest lands every bronze column as VARCHAR; generated SUM/AVG on numeric columns fail validation or need CASTs. Largest known BIRD accuracy cost (dms CHANGELOG 2026-09-26) | Netie-AI/dms#277 (open); lift measured under Netie-AI/dms#264 A1-02 | BUILD_NOW - ticket for epic-agent. Verified: `db_connector.py:481` `_fetch` str()s every value; `bronze.py:849` `write_bronze_rows` creates VARCHAR only. Types from the source catalog, not inferred from values |

Rows `F-TBD-n` carry provisional ids. The authoritative ledger (F1 to at least F83, cited in
`Netie-AI/dms` code and issues) is on the founder laptop and not yet pushed; dms#257 and
dms#265 already cite F-TBD-2 and F-TBD-3. The founder assigns the permanent F-numbers on
merge. No id is reused.

---

## 8. Review

Silent read, 15 minutes, before slicing. The FAQ's internal section is the part to read
properly - the external section is the part we cannot yet fully support.

**Nothing in the press release may appear in any external asset until it traces to a
passing gate.** Today, the quote and the drillthrough claim would both be premature.

---

## 9. Proposed amendments

### AMEND-F-TBD-5 - Failures become verified, reusable frames - PROPOSED - awaiting founder

> **Status: PROPOSED - awaiting founder.** Drafted by the PRD Agent from ledger row
> F-TBD-5. Tiers 0-4 are founder work: accept, edit or reject this block. Until you accept
> it, nothing here is in scope, nothing is sliced, and no ticket may cite it.

**In one line.** Every failure a Space produces becomes a candidate fix that only a
verifier can promote; promoted fixes become per-industry frames that a new Space may
*propose* from, never answer from.

**Why it maps to no epic.** Checked: Netie-AI/dms#277 (one Space's own ontology, no reuse
across Spaces), EPIC-019 Netie-AI/dms#38 (steward-registered verified queries for one
Space; no failure intake), EPIC-A1/A2/A3 Netie-AI/dms#257, #256, #265 (measure and
harden; A3 forbids tuning on its held-out set). None collects failures or reuses a fix
across Spaces.

**What exists today (verified in `Netie-AI/dms`).** Named abstain reasons on the envelope
(`packages/executor/dms_executor/gen_path_refuse.py`); per-Space verified queries
(`packages/executor/dms_executor/verified_queries.py`); a versioned ontology store
(ONTO-STORE-01 dms#279, closed). No module or table stores failure reasons per Space
(searched `apps/` and `packages/`).

**Constraints the founder already holds, carried unchanged.** WRONG=0 and named abstain.
A learned pattern may only propose; the verifier always decides. Measures are suggested
by Cortex and confirmed by a steward; auto-derived measures stay refused (F-TBD-4).
Cross-tenant learning carries schema shape only, never rows (PDPA).

**Conflicts you must resolve before accepting.**
1. Section 3 says self-host and single-tenant pilot only. Frames learned across tenants
   need shape to move between installs. Choose (a) frames authored by Netie from
   consenting pilots and shipped into installs as packs, one-way, or (b) installs report
   shapes upward through the OpenVault leave-machine gate. Recommended: (a).
2. The RL-distilled planner competes on intelligence; NETIE.md section 1 says
   "intelligence is bought". That is a constitution question, not a PRD one. Recommended:
   out of scope here; amend NETIE.md first if you want it.
3. NETIE.md section 6: verticals are packs added when a customer pays. The first frame
   ships only for an industry with a pilot (logistics and distribution, per section 1).
4. dms#265 acceptance: a question set used for tuning is no longer held out. Failures
   from an EPIC-A3 run never enter the loop.

**Success assertion (proposed).** WHEN a steward connects a second source in an industry
that has a certified frame THE SYSTEM SHALL answer at least one question that an earlier
Space in that industry abstained on before its fix, after one-click confirmation only,
with WRONG=0 over the run and n and the rule-of-three bound printed; and no failure
record or frame SHALL contain a value from a customer row.

**Epic outline (not sliced; ordered by irreversibility).**

| Epic | Tier | Repo | Contract | Depends on | Visible |
|---|---|---|---|---|---|
| EPIC-L1 Every failure is recorded with its reason | 1 FOUNDATION | Cortex + dms | additive (split per AGENT_SYSTEM s4) | dms#277 | no |
| EPIC-L2 Nothing learned is used until verified | 2 BOUNDARY | Cortex | none | L1, dms#272 PII-01 | partially |
| EPIC-L3 A new Space is proposed a frame | 3 CAPABILITY | Cortex + dms | additive | L2, dms#283 ONTO-CONFIRM-01 | yes |
| EPIC-L4 The steward sees and corrects failures | 4 SURFACE | dms | none | L1 | yes |
| EPIC-L5 Second-Space demo | 5 DEMO | dms | none | L1-L4 | yes |

Wave pairing: L1 with L4's read-only list (one visible), then L2 with L3, then L5.
Appetite: 2 weeks per epic; cancelled, not extended, if it misses.

Acceptance, per epic, on the envelope from `POST /v1/chat/ask` or the Studio view:
- **L1.** WHEN an ask on a Space ends in ABSTAIN, a WRONG grade, an adversary finding or a
  steward correction THE SYSTEM SHALL store one failure record naming the Space, the
  industry tag, the reason code and the envelope `audit_id`, and the record SHALL contain
  no cell value from the customer's rows.
- **L2.** WHEN a candidate fix or frame item has not passed the deterministic verifier AND
  a verification run different from the one that produced it THE SYSTEM SHALL NOT use it
  on any ask; and WHEN a frame leaves an install THE SYSTEM SHALL refuse any payload
  holding a row value and send nothing without the leave-machine gate's allow.
- **L3.** WHEN a steward connects a source in an industry with a certified frame THE SYSTEM
  SHALL offer frame items (objects, links, plan templates, verified queries) as
  `proposed` only, and an ask that needs an unconfirmed item SHALL abstain with its named
  reason.
- **L4.** WHEN a steward opens a Space's failure view THE SYSTEM SHALL list each failure
  with its reason, its fix candidate, and whether the verifier and the independent run
  passed it.
- **L5.** WHEN the demo's second Space is connected THE SYSTEM SHALL answer, after
  one-click confirm, a question the first Space abstained on, with the ledger trail shown.

**Out of scope for this amendment.**
- Training or distilling any planner model, RL included (NETIE.md s1; constitution first)
- Any row, cell value or sample leaving an install; pooling tenant data
- Promoting a fix or frame item without verifier, independent run and steward confirm
- Auto-derived measures (F-TBD-4 refusal stands)
- Tuning on an EPIC-A3 held-out set
- A frame for an industry with no pilot customer
- Multi-tenant hosting (section 3 stands)

**Founder decisions.** (1) Accept, edit or reject. (2) Direction of frames, (a) or (b).
(3) Whether the planner goes to a NETIE.md amendment.
