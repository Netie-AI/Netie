# PRD-001 - Local assistant, vault-first

**Product:** AirGPT
**Owner:** founder
**Status:** draft - vault-first not yet sliced; **F1 founder YES - Wave Demo-0 in flight**
**Repos in scope:** `jian-hong/AirGPT`
**Created:** 2026-08-03
**Amended:** 2026-08-03 evening (F7-F9 routing); 2026-08-03 night (founder YES F7a+F8a MVP -> EPIC-D03); 2026-08-03 (F10-F12: reveal UI extend #14, Docs thin YES / secure PARK P9, strong reasoning extend #15); 2026-08-03 (F13: laptop-safe ~50MB 4-workbook SIRA+hybrid bench — amend #13; P2/P6 untouched); 2026-08-03 (F14: continuous SQL after workbook locate — new RAG-BENCH-10 under D01; DMS regex standards PARK P10); 2026-08-03 (F15: Excel-native Copilot/orchestration wave — EPIC-D04 surface + DMS EPIC-016; P3 superseded; not F14/#21); 2026-08-03 (F16: Settings post-create depth/arch/adaptive + rebuild — new RAG-BENCH-11 under D01); 2026-08-03 (F15 NEEDS-YOU resolved: Pointer-primary paste + Excel Copilot path dependency YES; MCP secondary); 2026-08-06 (F17-F20 intake logged, **all four NEEDS-YOU** - none maps to an open epic; no epic filed, no ticket filed; recommend a new PRD-002 for the agent surface rather than widening this one); 2026-08-07 (F21 tunnel reachability defect -> **EPIC-D03 filed as [#26](https://github.com/jian-hong/AirGPT/issues/26)**, authorized 2026-08-03 but never on GitHub; D03 acceptance amended with a reach clause; ticket sketch HOST-DEMO-03. F22 per-device access grants **split**: F22a **NEEDS-YOU / PRD amendment + recommend DR-0003**; F22b dead access bar -> HOST-DEMO-04 under #26); 2026-08-07 (**F22a answered YES by founder - level-based access grants, recorded as DR-0003 `proposed`**; shareable classes = `read_only` / `use_host_ai` / `use_own_ai`; per-file grants deferred; five parameters still founder-owed; build blocked until DR-0003 accepted. **F23** hub access + share QR defect logged with **routing decided in advance by cause**)

---

## 1. Press release

### [HEADLINE TBD] - the host shell where a person lives day to day

**Subheading:** [customer + benefit TBD]

**Problem:** [customer words TBD - settings, pairing, and apps scattered; keys in plain files]

**Solution:** AirGPT is the standalone chat and control surface: settings, pairing, apps hub - a thin client of OpenVault for custody and Cortex for brains.

**Quote:** [pilot customer TBD]

**Call to action:** [TBD]

---

## 3. Out of scope

- A second key vault (custody stays in OpenVault)
- A second orchestrator (intents go to Cortex; AirGPT does not decide work shape)
- Inference serving (plane 1)
- Replacing DMS, Pointer, or FreeIDE as the product that proves a vertical

**F1 demo exception (founder 2026-08-03):** EPIC-D01 may use **Cortex API direct** for full AI on the RAG bench path. Honesty line: **Cortex-direct, not OpenVault-gated.** This does not amend the vault-first success assertion for the product trunk; it authorizes a true (not mock) demo path.

---

## 4. Success assertion

> **WHEN** a person opens AirGPT for chat or app control, **THE SYSTEM SHALL** resolve keys and model routes through OpenVault and send governed work to Cortex - with no path that bypasses those gates.

**Demo-path honesty (F1):** EPIC-D01 claims must say Cortex-direct, not OpenVault-gated. Vault-first gate is explicitly not required for this path.

---

## 5. Epic waves

### Vault-first product waves

**Not sliced yet.** Press release still TBD. EPIC-001+ reserved for OpenVault custody + Cortex handoff when Mode A runs. EPIC-D01 does not steal that numbering.

### Wave Demo-0 - RAG workbook cross-compare (AUTHORIZED)

**Status:** in flight (founder YES 2026-08-03). Prefer a **true** path on a keepable branch (`demo/rag-cross-compare` or equivalent). Not fake seed theater. AI Excel chart-governance (P3) **superseded by F15 Wave Demo-2** (DMS Excel-native; not in D01).

| Epic | Repo | Contract | Depends on | Visible |
|---|---|---|---|---|
| **EPIC-D01** [#6](https://github.com/jian-hong/AirGPT/issues/6) Demo-ready RAG workbook cross-compare | jian-hong/AirGPT | none | existing `tests/RAG/frtr_eval.py`, `rag/*`, Cortex API | **yes** |

**Repo:** `jian-hong/AirGPT`
**Contract impact:** none
**Depends on:** Cortex API reachable for LLM answer path (direct; not OpenVault-gated for this demo)
**Irreversibility tier:** DEMO (+ thin CAPABILITY: multi-variant score schema under `tests/RAG/results/`)
**Appetite:** <1 day (demo tomorrow)

**Acceptance (customer seat):**
> **WHEN** the founder ingests one real sanitized FRTR workbook, spot-checks that retrieval hits the right sheet/cells, and runs a few golden questions across RAG variants (baseline + SIRA-inspired + depth/adaptive as available), **THE SYSTEM SHALL** write retained multi-variant scores to `tests/RAG/results/` (JSON + Excel-openable xlsx) and leave those variants invocable for live click-through — with UI/docs stating Cortex-direct, not OpenVault-gated.

**Priority order (founder):** ingest one real workbook → verify retrieval correct → few FRTR golden questions → scores across variants. Strengthen RAG only with cheap wins. No mock.

**Code premise check (2026-08-03):**

| Claim | Verified |
|---|---|
| FRTR eval harness | `tests/RAG/frtr_eval.py` + `tests/RAG/results/frtr_gold.json` + sanitized xlsx |
| SiRA-like enrichment | `rag/sira.py` is **SiRA-inspired**, not full Meta SIRA |
| Offline depth bench | `rag/evaluate.py` |
| Adaptive depth | `rag/adaptive.py`, `tests/test_rag_adaptive.py` |
| Chat effort + thinking | `clipdrop.py` `model_tier` / `thinking`; RAG `depth` |
| RAG API surface | `/api/rag` in `clipdrop.py` |

#### EPIC-D01 - ticket batch for epic-agent (AUTHORIZED to file)

Slimmed for true ingest+score path. Ordered build sequence:

1. **RAG-BENCH-01 True ingest + retrieve + multi-variant scores** - WHEN one real sanitized FRTR workbook is ingested and a few golden questions are run across >=2 variants (baseline, sira-enrich; adaptive/depth if cheap), THE SYSTEM SHALL prove retrieval spot-check pass and write retained scores to `tests/RAG/results/` as JSON + xlsx.
2. **RAG-BENCH-02 Live variants click-through** - WHEN the founder selects a scored variant (UI or CLI), THE SYSTEM SHALL answer with that pipeline without wiping prior score rows.
3. **RAG-BENCH-03 Effort x thinking matrix (thin)** - WHEN time remains after 01-02, THE SYSTEM SHALL append a basic/high/max x thinking on/off sheet to the retained xlsx using existing knobs — defer cells if blocked, do not block demo on full matrix.
4. **RAG-BENCH-04 Minimal insights sheet (thin)** - WHEN scores exist, THE SYSTEM SHALL add a short insights/suggested-prompts sheet to the same xlsx — no AI chart-governance (P3).
5. **RAG-BENCH-05 Cortex-direct honesty** - WHEN the demo is shown, THE SYSTEM SHALL state Cortex-direct (not OpenVault-gated) in UI or demo README on the keepable branch.

#### EPIC-D01 - additive tickets (founder YES F2a / F5 / F6 / F10-F12)

6. **RAG-BENCH-06** [#13](https://github.com/jian-hong/AirGPT/issues/13) Sample messy multi-sheet fixtures - **F13 amend (2026-08-03):** primary demo pack is laptop-safe **~50 MB total / 4 distinct workbooks ~12 MB each** (not few-hundred-MB as demo-day requirement). WHEN that pack is ingested under the D01 harness with SiRA-inspired (`sira_max`) vs hybrid(+adaptive) variants, THE SYSTEM SHALL score toward **~99% retrieval-then-generate** without breaking sanitized warehouse/FRTR baselines; originals revealable via Docs (#20) + reveal UI (#14). Existing ~317MB `tests/RAG/messy/` = optional local stress only. ~2GB stays PARK P6; full Meta SIRA stays PARK P2.
7. **RAG-BENCH-07** [#14](https://github.com/jian-hong/AirGPT/issues/14) Reveal source folder - WHEN an answer cites an original source file, THE SYSTEM SHALL offer OS reveal / open-containing-folder for that path (demo UI or citation control). **F10 extend:** hover-card file icon (bottom-right) on ingested file cards calls existing `POST /api/rag/reveal-path` (API already present; UI is the remaining acceptance).
8. **RAG-BENCH-08** [#15](https://github.com/jian-hong/AirGPT/issues/15) Ontology then logic then answer - WHEN a workbook is ingested for demo Q&A, THE SYSTEM SHALL form ontology first from workbook semantics (columns/entities/relations), then show logics and answers on top of that ontology - not blind retrieve-only. Owns the read-path shape for D01; D02 consumes it for identify-row honesty. **F12 extend:** strengthen visible reasoning (logic chain quality / audit-grade why) on top of ontology — not a separate epic.
9. **RAG-BENCH-09** (epic-agent to file) Space Docs original retain (F11a) - WHEN a file is ingested into a RAG space, THE SYSTEM SHALL retain a byte-faithful copy under that space's local `Docs/` (or `blob/<id>/docs/`) so the founder can reveal/open the original for cross-check audit. Today `blob/.../sources` stores post-extraction `.txt` only (`rag/ingest.py`) — not original xlsx/binaries. Out of scope: encryption, ACL mesh, vault custody (F11b -> P9).
10. **RAG-BENCH-10** (epic-agent to file; F14) Continuous SQL ops after workbook locate - WHEN the founder asks a filter+aggregate KPI on an ingested FRTR workbook (acceptance example: "Find the average OnTimeSLA for all base rate above 1" on `frtr_00027_supply-chain-regional.xlsx`), THE SYSTEM SHALL locate the workbook, then run continuous SELECT-only SQL ops (filter `BaseRate > 1` → `AVG(OnTimeSLA)` on Carrier master), return a numeric average with sheet/SQL provenance, and refuse metadata-only / Summary-only theater. Do not stop at schema chunks; do not mix irrelevant web into workbook-bound KPI asks. Premise: `hybrid_sql_lane` + `frtr_sql_baseline.answer_sqlish` is keyword-heuristic and misses Carrier-master columns; playbook cite `docs/subagents_findings/2026-08-03_frtr-excel-rag-playbook.md`. **Not** an amend of #13 (pack/scoreboard) or #15 (readable reasoning) — #13 may **depend on** this for numeric KPI ~99%; #15 **consumes** SQL provenance when present. DMS shared regex/glossary/prompt standards = **P10** (cross-product), not this ticket.
11. **RAG-BENCH-11** [#25](https://github.com/jian-hong/AirGPT/issues/25) (F16) Settings post-create index depth / architecture / adaptive + rebuild - WHEN the founder opens Settings on an existing RAG space (e.g. FRTR Bench), THE SYSTEM SHALL show Index depth (basic/high/max/manual + adaptive/auto), Architecture (same selectable set as create, including hybrid / SiRA-inspired paths available to create), allow Save of those as space defaults (`depth_default` + `config.architecture` / adaptive mode), and WHEN they choose Rebuild whole pipeline after Save, THE SYSTEM SHALL re-run extract → chunk → enrich → embed → index under the newly saved config (not the create-time snapshot). Chat effort remains a separate query-time override. Premise: Settings already computes `depthOpts`/`archOpts` and `ragSaveSettings` already reads `#ragSetDepth`/`#ragSetArch`, but the selects are never rendered; Rebuild exists (`ragRebuildSpace` → `POST .../build`). **Not** amend #13/#21/#15.

### Deferred (not in Wave Demo-0 / Demo-1)

See AirGPT `PARKING_LOT.md` P1-P10. **P3 superseded by F15 / Wave Demo-2** (Excel-native path owned with DMS; AirGPT does not own chart orchestration). F2 ~2GB stays PARK P6. F4 NVIDIA catalog is OpenVault [#12](https://github.com/Netie-AI/OpenVault/issues/12) - not AirGPT vault. F11b secure/encrypted Docs custody **P9**. F14 DMS regex/glossary standards **P10**.

### Wave Demo-2 - Excel-native Copilot orchestration (AUTHORIZED to file; build later)

**Status:** founder authorized PRD→epic→tickets now (F15 2026-08-03); **NEEDS-YOU resolved 2026-08-03** (Pointer-primary + Copilot dependency YES); **implementation deferred** (leave build later). Do **not** start ticket-runners while D01/D02 WIP is hot unless founder overrides. Cross-product with DMS **EPIC-016** + Pointer paste.

**Pipeline (authoritative):** AirGPT RAG identify+draft insightful governed-tested prompt pack → DMS cross-check/strengthen/validate → Pointer paste into Excel Copilot on correct workbook → DMS extract resulting xlsx → AirGPT reveal. `user-excel` MCP = secondary/optional research only (not primary paste). F14/#21 SQL stays parallel.

| Epic | Repo | Contract | Depends on | Visible |
|---|---|---|---|---|
| **EPIC-D04** Identify workbook + structured Copilot prompt pack + handoff (AirGPT surface only) | jian-hong/AirGPT | none (demo) / additive if handoff receipt wire | DMS EPIC-016 capability; F14/#21 stays parallel in-RAG SQL | **yes** |
| **EPIC-016** (DMS PRD) Governed prompt-pack cross-check → Pointer→Excel Copilot run → extract resulting workbook | Netie-AI/dms (+ Cortex action gate if ledgered writes; Pointer paste) | none or additive | Space path usable; not AirGPT second orchestrator; Pointer paste lane | **yes** |

**Repo (AirGPT half):** `jian-hong/AirGPT`
**Contract impact:** none for surface handoff; additive only if a thin receipt/status field is required
**Depends on:** DMS owns governed prompt cross-check + Excel path orchestration; Pointer owns Copilot panel paste; AirGPT OOS "second orchestrator" stands
**Irreversibility:** BOUNDARY (who owns Excel drive / paste) + SURFACE (AirGPT identify+prompt) + DEMO
**Appetite:** tickets filed (#22-24 / DMS #29-32); epic-agent **amend bodies** for Pointer-primary + DMS cross-check; build after Demo-0 SQL (#21) or founder WIP override
**Honesty:** Excel Copilot (Pointer paste) path is **not** AirGPT in-process RAG. MCP is not the primary Copilot paste path. Distinct from F14 continuous SQL.

**Acceptance (customer seat, end-to-end with DMS + Pointer):**
> **WHEN** the founder asks (on `frtr_00027_supply-chain-regional.xlsx`) for OnTime=true average cost + separate xlsx export + chart/visualization for PPT, **THE SYSTEM SHALL** locate the workbook, emit a first-insightful structured Excel Copilot prompt pack, have DMS governed-cross-check/strengthen it, have Pointer paste the validated pack into Excel Copilot on the correct workbook, then return/open the resulting workbook (Cover / OnTime Export / Analysis / Presentation Chart) with avg on-time cost in the Excel Copilot ballpark (~USD 300 across ~184k OnTime rows) — not Summary-only refuse theater and not AirGPT inventing a second orchestrator loop.

**Code premise check (2026-08-03):**

| Claim | Verified |
|---|---|
| Cursor `user-excel` MCP | read/write/describe/format/screen_capture — **not** Excel Copilot panel paste/control; **secondary/optional only** |
| AirGPT RAG on same Q | Failed: no OnTime=true / empty Summary theater + web noise (F15) |
| Excel Copilot on same file | Succeeded (~6 steps; AVERAGEIF + FILTER; ~184k rows) |
| F14/#21 | In-process SELECT-only SQL after locate — **different path**; keep |
| P3 prior park | Chart-intent was Cortex/AirGPT surface — **superseded** by Excel-native DMS+Pointer path |
| PRD OOS | AirGPT must not become second orchestrator — intents/work-shape stay Cortex/DMS; paste = Pointer |

#### EPIC-D04 - ticket batch (filed; epic-agent amend bodies — do not implement yet)

1. **XLSX-ORCH-01** [#23](https://github.com/jian-hong/AirGPT/issues/23) Identify + prompt pack - WHEN founder asks multi-part filter/export/chart on an ingested FRTR workbook, AirGPT SHALL locate the correct workbook and emit a **first insightful, governed-tested, strong/correct** structured Excel Copilot prompt pack (ordered steps + formula/sheet intent), without running Copilot or Pointer itself. Pack is candidate input to DMS cross-check.
2. **XLSX-ORCH-02** [#24](https://github.com/jian-hong/AirGPT/issues/24) Handoff + resulting workbook surface - WHEN DMS Excel-native run completes (after Pointer→Copilot), AirGPT SHALL show handoff status and reveal/open the resulting workbook path (reuse reveal/#14 patterns) — no in-AirGPT Copilot panel driver.

Parent epic: [#22](https://github.com/jian-hong/AirGPT/issues/22) EPIC-D04.

#### DMS EPIC-016 - ticket sketch (filed #29-32; DMS epic-agent amends)

1. **XLSX-ORCH-10** [#30](https://github.com/Netie-AI/dms/issues/30) Governed cross-check + Pointer→Excel Copilot multi-step - WHEN handed AirGPT candidate prompt pack + `frtr_00027` path, DMS SHALL cross-check/strengthen/validate the pack (incl. schema/SQL sanity), then hand validated prompt to **Pointer** for paste into Excel Copilot on the correct workbook (MCP `user-excel` = secondary/fallback research only — **not** primary paste), producing Cover / OnTime Export / Analysis / Presentation Chart sheets.
2. **XLSX-ORCH-11** [#31](https://github.com/Netie-AI/dms/issues/31) Extract whole workbook - WHEN the Excel Copilot run completes, DMS SHALL return the resulting xlsx into the Space/Docs (byte-faithful) for audit and AirGPT reveal.
3. **XLSX-ORCH-12** [#32](https://github.com/Netie-AI/dms/issues/32) FRTR golden pack - WHEN the acceptance Q runs, THE SYSTEM SHALL match Excel Copilot ballpark (avg ~USD 300.27; ~184k OnTime / 200k total; region breakdown optional) with sheet provenance — not RAG Summary theater.

**Founder decisions (F15 NEEDS-YOU closed):** (1) **Pointer-primary** Copilot panel paste; (2) **Excel Copilot IS accepted path dependency** (YES).

**Not this wave:** amend #21; reopen EPIC-013 chart_spec (in-engine insights charts ≠ Excel Copilot); unpark EPIC-014 ask/preview MCP as substitute; promote MCP to primary Copilot paste.

### Wave Demo-1 - Governed amend-confirm ops (AUTHORIZED)

**Status:** authorized (founder YES 2026-08-03 F3/b). Branch preference: **`demo/rag-ops-confirm`** so D02 does not pollute D01 score artifacts on `demo/rag-cross-compare`.

| Epic | Repo | Contract | Depends on | Visible |
|---|---|---|---|---|
| **EPIC-D02** [#16](https://github.com/jian-hong/AirGPT/issues/16) Governed amend-confirm demo loop | jian-hong/AirGPT | none (demo) / Cortex action surface if real writes | EPIC-D01 read path + [#15](https://github.com/jian-hong/AirGPT/issues/15) | **yes** |

**Repo:** `jian-hong/AirGPT`
**Contract impact:** none (demo). If real Cortex writes: additive Cortex confirm gate first - do not invent a second write path.
**Depends on:** D01 read path proven; RAG-BENCH-08 ontology for honest "is it that one?"
**Irreversibility:** BOUNDARY (confirm gate) + SURFACE (AirGPT loop) + DEMO
**Appetite:** <2 days on demo branch
**Honesty:** Cortex-direct for demo (same F1 exception). Salary-increment style: identify row -> amend -> user confirm -> continue. Governed, not off-rails.

**Acceptance (customer seat):**
> **WHEN** the founder asks to increment a salary (or similar cell amend) on the demo branch, **THE SYSTEM SHALL** identify the candidate row and ask "is it that one?", apply the amend only after explicit user confirm, then continue the loop - refusing off-rails writes.

**Tickets:** [#17](https://github.com/jian-hong/AirGPT/issues/17) OPS-DEMO-01, [#18](https://github.com/jian-hong/AirGPT/issues/18) OPS-DEMO-02, [#19](https://github.com/jian-hong/AirGPT/issues/19) OPS-DEMO-03.

### Wave Demo-0 add-on - Host surface hardening (AUTHORIZED)

**Status:** authorized (founder YES 2026-08-03 F7a + F8a only). Branch: **`demo/rag-cross-compare`** — parent may implement immediately without waiting on epic-agent tickets.

| Epic | Repo | Contract | Depends on | Visible |
|---|---|---|---|---|
| **EPIC-D03** [#26](https://github.com/jian-hong/AirGPT/issues/26) Host surface hardening (F7a + F8a MVP + F21 tunnel reachability) | jian-hong/AirGPT | additive (establish headers + session bind) | existing `clipdrop.py` `ThreadingHTTPServer`, `hosting.py` health pings | **yes** |

**Filed 2026-08-07 (F21).** EPIC-D03 was founder-authorized 2026-08-03 but never existed as
a GitHub issue while its work was landing (`769c9c52` is HOST-DEMO-01). GitHub is the source
of truth; the epic is now [#26](https://github.com/jian-hong/AirGPT/issues/26). No new scope
was added by the filing itself. WIP unchanged: D01 + D02 stay the two primary lanes, D03
stays a thin add-on on the same branch.

**Repo:** `jian-hong/AirGPT`
**Contract impact:** additive — `X-AirGPT-Security-Version`, session nonce headers; no breaking wire change
**Depends on:** none (single-PC host mode; not F7b LB)
**Irreversibility:** BOUNDARY (F8a establish gate) + CAPABILITY (F7a in-process perf)
**Appetite:** <1 day on demo branch
**Honesty:** Cortex-direct demo unchanged. F7b true LB / multi-worker **P8**. F8c mTLS **P8**. F8b vault custody handshake stays **OpenVault** (P7).

**Acceptance (customer seat):**
> **WHEN** the founder runs host mode on one strong PC and opens AirGPT over tunnel or LAN, **THE SYSTEM SHALL** reach a working remote URL or say honestly and immediately why it cannot (F21), **SHALL** return `/api/info` and host health probes without blocking the UI (F7a caches/keepalive/throttled pings), and **SHALL** require an explicit establish handshake (session nonce + security version headers) before any `/api/ai/*` or chat API call is accepted.

**Acceptance amended 2026-08-07 (F21).** The reach clause is new. The original wording said
"opens AirGPT over tunnel or LAN" and was **not testable from the customer seat**, because
the tunnel could never come up on any network - see the F21 ledger row. An epic whose
acceptance cannot be reached is not a passing epic, it is an untested one.

**Code premise check (2026-08-03):**

| Claim | Verified |
|---|---|
| Single-process server | `clipdrop.py` `ThreadingHTTPServer` on `:8765` |
| Hot path exists | `/api/info` handler; SSE `: keepalive` in stream paths |
| Host health pings | `hosting.py` `_ping_openai` for Colibri/vLLM/Ollama |
| Local vs remote gate | `_is_local_host`, `_is_host_only_path` — no `/api/establish` yet |
| F7b LB | **Not present** — P8 only |
| F8c mTLS | **Not present** — P8 only |

#### EPIC-D03 - ticket batch for epic-agent (AUTHORIZED to file)

Thin pair; may land on `demo/rag-cross-compare` before tickets exist.

1. **HOST-DEMO-01 F7a in-process speed** - WHEN host mode is active on one PC, THE SYSTEM SHALL widen hot-path caches for `/api/info` and cortex probe, enable HTTP keepalive on long-lived connections, and throttle `hosting.py` backend health pings so the UI stays responsive — single-process only; no nginx/worker farm.
2. **HOST-DEMO-02 F8a establish handshake** - WHEN a client connects over tunnel or LAN (non-local `_is_local_host`), THE SYSTEM SHALL expose an explicit establish step (`/api/establish` or hardened `/api/probe`) returning session nonce + `X-AirGPT-Security-Version`, bind subsequent chat/API tokens to that handshake, audit-log mismatches, and reject `/api/ai/*` until establish completes.
3. **HOST-DEMO-03 F21 tunnel reachability (defect)** - WHEN the founder starts host mode on a network where at least one tunnel provider is reachable, THE SYSTEM SHALL publish that provider's real forwarding URL in `/api/info` `tunnel_url` within one sweep; WHEN none is reachable, SHALL report within a bounded time which providers were tried and why each failed - never a banner or console hostname, never silent churn. Root-cause class: first-match-wins over a pattern list with no non-tunnel-host exclusion (`_read_tunnel_url`). Class fix `_BANNER_LABELS` / `_is_banner_url` already in the tree; the ~48s-per-candidate probe budget (`_probe_tunnel_url` attempts=24 delay=2.0, `clipdrop.py:1577`) x 4 providers x 2 sweeps is **not** covered and is this ticket's remaining work.
4. **HOST-DEMO-04 F22b access-level bar is dead (defect, R-0011)** - WHEN the founder opens the access menu for a connected device, THE SYSTEM SHALL state what that level actually changes today (AI source and Hub labelling) and SHALL NOT present a level as granting API access it does not grant. `hub.py:13` `ACL_LEVELS` is persisted by `set_peer_acl` and read only by the `ai_source` label (`hub.py:306-314`); the gate at `clipdrop.py:2546`/`4026` is IP-only. **Honesty only - does not make `access_level` load-bearing** (that is F22a, PRD amendment + DR).

**WIP:** D01 + D02 remain primary (both human-inspectable). D03 is thin add-on on the same demo branch — do not open a fourth AirGPT epic.

---

## 6. Out-of-scope conflicts raised by F1

| Feedback piece | Conflict | Founder disposition 2026-08-03 |
|---|---|---|
| Full Meta SIRA + H100 / Rust bm25x | Plane 1 | Park (P2) |
| AI-governed Excel chart pipeline | Second orchestrator / Cortex | **Park (P3)** for tomorrow |
| 50GB ingest | Scale | Park (P1) |
| Model effort controls | OpenVault vs surface | Thin ticket RAG-BENCH-03; custody honesty = Cortex-direct |
| Cross-compare RAG agents | Outside vault-first trunk | **YES EPIC-D01** |
| Vault-first gate on demo path | Success assertion vs demo speed | **Exception:** Cortex API direct OK; record honesty |
| ~2GB messy raw multi-sheet demos (F2) | Scale / ingest ops | **Park (P6)**; sample-messy YES under D01 RAG-BENCH-06 |
| Confirm/amend/ops write loop (F3) | Not EPIC-D01; Cortex actions vs AirGPT surface | **YES EPIC-D02** on `demo/rag-ops-confirm` |
| NVIDIA/Mistral catalog + model pick (F4) | Plane 2 custody - OpenVault only | **YES OpenVault** catalog+probe; no AirGPT vault |
| Reveal source folder (F5) | Demo surface / citations | **YES** RAG-BENCH-07 under D01 |
| Ontology-first then logic/answer (F6) | Read-path capability | **YES** RAG-BENCH-08 under D01 (D02 consumes) |
| Load balancer + multi-worker host farm (F7) | Plane 1 / capital infra; `ThreadingHTTPServer` is single-process | **Founder YES (a) 2026-08-03:** F7a MVP under **EPIC-D03** on `demo/rag-cross-compare`. **F7b park P8.** |
| Strong secure establishment handshake on every chat/API (F8) | Vault-first assertion vs demo speed; remote OpenIDE capability tokens | **Founder YES (a) 2026-08-03:** F8a MVP under **EPIC-D03** (establish + security version headers). F8b **OpenVault/P7**. F8c mTLS **park P8**. |
| Clearer RAG demo: file select -> ingest -> answer (F9) | Demo docs vs UI gap | **Docs/guidance only** under EPIC-D01 (`tests/RAG/DEMO_RAG.md`). APIs exist (`/api/rag/spaces`, upload, build, answers); no new epic. |
| Hover-card reveal icon on ingested file cards (F10) | F5/#14 reveal surface vs new ticket | **YES extend #14** under EPIC-D01 — API live; UI icon is remaining acceptance |
| Secure backup / Docs folder per RAG space (F11) | Storage layout + "secure" custody vs audit need | **Split:** F11a YES thin original retain under D01 (RAG-BENCH-09). F11b PARK P9 (encryption/ACL/vault custody) |
| Strong reasoning on answers (F12) | Overlap with F6/#15 ontology->logic->answer | **YES extend #15** under EPIC-D01 — deepen reasoning quality; no new epic |
| Laptop-safe ~50MB / 4-workbook SIRA+hybrid bench toward ~99% retrieval + original reveal (F13) | F2a #13 was few-hundred-MB; 6GB RAM guidance caps raw text ~100–200MB; ~317MB already generated | **YES amend #13** under EPIC-D01 — primary demo pack **~50MB / 4×~12MB**; SiRA-inspired only (not P2); ~317MB optional stress; P6 2GB untouched; originals via #20/#14 |
| Continuous SQL after file locate + less metadata-chunk reliance; DMS regex/glossary/prompt standards (F14) | FRTR 00027 MAX RAG refused avg OnTimeSLA for BaseRate>1 — Summary-only evidence; `answer_sqlish` heuristics miss Carrier master; DMS regex is cross-product | **YES new RAG-BENCH-10** under EPIC-D01 (not amend #13/#15 as owner; #13 may depend; #15 consumes provenance). **Not PRD amend** for AirGPT SQL lane (inside D01 golden KPI). **PARK P10:** shared DMS↔AirGPT regex decision + glossary/standard prompts |
| Excel-native Copilot path for multi-part filter+export+chart (F15) | RAG alone fails sophisticated multi-step Excel work; AirGPT OOS second orchestrator; P3 was parked chart-governance; Cursor `user-excel` ≠ Copilot panel; must connect DMS + Pointer | **YES Wave Demo-2** — AirGPT **EPIC-D04** (#22-24) + DMS **EPIC-016** (#29-32) + Pointer paste. Pipeline: AirGPT pack → DMS cross-check → Pointer→Excel Copilot → DMS extract → AirGPT reveal. **Founder YES 2026-08-03:** Pointer-primary paste; Copilot path dependency accepted; MCP secondary only. **Not** F14/#21. **P3 superseded**. **NEEDS-YOU closed.** |
| Skills stop being a user-facing concept; tools live inside the Cortex engine (F17) | Removes a shipped surface **and** a wire field (`skill` / `skill_pack`); tool selection is Cortex's per NETIE.md section 3 | **NEEDS-YOU 2026-08-06.** No open epic. Surface removal is an afternoon; the boundary statement is not. If the field is deleted rather than made engine-selected, that is **breaking -> decision record, not an epic**. Recommend a DR fixing the boundary: tools are engine-internal, agents are the user-facing reusable unit |
| Suggested agents are filler; must be real and runnable (F18) | Content ask needs an amendment; the **dead `schedule_hint`** underneath it is a shipped lie (NETIE.md rule 6) | **NEEDS-YOU 2026-08-06.** Two halves. Making the "daily / weekly" chip honest - wire it to the **existing** Cortex routines scheduler (`cortex_client.py:613-647`) or stop claiming recurrence - **widens nothing** and should go first. Real, workflow-tied suggestions depend on F19 |
| Cortex must create reusable AGENTS: scheduler, email connector, orchestrator, downloadable local Python, online backend (F19) | Does not serve this PRD's success assertion; collides with NETIE.md section 6 in three places | **NEEDS-YOU 2026-08-06.** **Recommend a new PRD (Tier 3, founder-authored), not an amendment.** Scheduler already exists in **Cortex**; connector credentials are **OpenVault**; decomposing orchestrator is the **third-orchestrator** NETIE.md declines; sandbox VM is **plane 0/1**; downloadable Python is a code-signing decision. AirGPT owns surface only |
| Tool-call surfacing grouped and expandable like Claude Code (F20) | No open epic owns the agent run stream; #15 owns the RAG reasoning chain, a different surface | **NEEDS-YOU 2026-08-06.** Cheapest of the four: pure SURFACE, in-AirGPT, no contract change. **Not** an amend of #15. Diff stats need `fs_write`/`fs_patch` to return line deltas first |
| Remote access over tunnel is unreliable to unusable (F21) | None. Remote reach is a shipped capability and it is named inside EPIC-D03's own acceptance clause | **belongs_to OPEN EPIC-D03 [#26](https://github.com/jian-hong/AirGPT/issues/26).** Not a PRD amendment - nothing widens, no contract changes, the tunnel worker and `/api/info tunnel_url` already ship. Epic filed 2026-08-07 (authorized 2026-08-03, never filed). New ticket sketch **HOST-DEMO-03**. **Not** amend HOST-DEMO-01 (perf) or -02 (establish). The fix belongs in the current wave: D03 is the only epic whose acceptance the defect blocks |
| Per-device access grants - a bar that grants a class of access to a connected device (F22) | Changes the threat model of a gate deliberately shipped closed (S0 host-only). `_HOST_ONLY_PREFIXES` includes `/api/rag`, so a phone that connects still gets 403 on the product. Custody of any capability token is OpenVault (plane 2) | **Split.** **F22a NEEDS-YOU 2026-08-07 - PRD amendment, founder's call.** Maps to no open epic; D03's authorized scope is F8a establish only, and its own honesty line already defers capability tokens ("F8b OpenVault/P7"). **Recommend DR-0003 in `D:\AirGPT\docs\decisions\` before any build** - crosses a repo boundary, expensive to reverse, will be re-litigated every session. Dependency: the capability-token design, not the guest chat token (`clipdrop.py:780-785` already says so). **F22b YES** - the access bar already exists and grants nothing (R-0011); making it honest widens nothing -> **HOST-DEMO-04** under [#26](https://github.com/jian-hong/AirGPT/issues/26). **RESOLVED 2026-08-07: founder YES, level-based, recorded as DR-0003 (status `proposed`).** Shareable classes = the three he named (`read_only` / `use_host_ai` / `use_own_ai`); 16 of the 17 host-only prefixes stay shut to every shareable level; per-file grants deferred (DR-0003 decision 3); five parameters still founder-owed; **build blocked until DR-0003 is accepted** |
| Hub access control and share QR are broken today (F23) | A defect in the surface F22a replaces - must not be folded into the capability that replaces it | **Conditional routing decided in advance 2026-08-07**, before the parent-session investigation lands: ACL-bar cause -> amend **HOST-DEMO-04**; no-passcode-QR cause -> new **HOST-DEMO-05**; tunnel-URL-lifecycle cause -> **HOST-DEMO-03** (F21); expired-token-not-surfaced cause -> amend **HOST-DEMO-04**; **join-succeeds-then-403 is not a defect** -> DR-0003, and must not be "fixed" by opening the gate locally. Not a PRD amendment under any cause |
| Change index depth / architecture / adaptive on existing RAG + Rebuild under new config (F16) | Settings shows Rebuild but not depth/arch controls; create already has knobs; chat has effort but index side cannot rework after pipeline | **YES RAG-BENCH-11 [#25](https://github.com/jian-hong/AirGPT/issues/25)** under EPIC-D01. **Not** PRD amendment (create + space `depth_default`/`architecture` + rebuild already in product; D01 already claims depth/adaptive variants). **Not** amend #13 (pack), #21 (SQL lane), #15 (reasoning). Adaptive/auto = **space default** used by Save→Rebuild (and default answers); chat effort stays query-time override. Demo-variant APIs remain related but not a substitute for Settings controls |

---

## 7. Feedback ledger

Append only. This table is the PRD's memory - it is how feedback given weeks ago lands in the right epic instead of becoming a duplicate.

| # | Date | Raised in | Feedback | Routed to | Outcome |
|---|------|-----------|----------|-----------|---------|
| F1 | 2026-08-03 | Cursor session (founder ask) | Demo-ready RAG cross-comparison bench: multi-workbook FRTR-style ingest + golden accuracy across RAG variants (incl. Facebook SIRA-type); chat bar effort (high/max/basic) + thinking on/off with retained scores; post-bench insights / suggested prompts / xlsx export + graphs by test/field/data type; AI-governed Excel chart-intent pipeline. Ambition cites ~50GB and full Meta SIRA. | EPIC-D01 / AirGPT#6 | **Founder YES 2026-08-03.** Wave Demo-0 authorized. Amendments: Cortex-direct (not OpenVault); P3 parked; true ingest+score; retained scores + live variants. Tickets: #7 RAG-BENCH-01, #8 RAG-BENCH-02, #9 RAG-BENCH-03, #10 RAG-BENCH-04, #11 RAG-BENCH-05. |
| F2 | 2026-08-03 | Cursor session (founder follow-up) | Few demos ready for ~2GB messy multi-sheet uncleaned raw workbooks; retrieve insights; total/average sales; calculate salary increment. | Split: read demos vs scale | **Founder YES (a) 2026-08-03.** Sample messy multi-sheet at **few hundred MB** (not 2GB) under D01 / RAG-BENCH-06. **~2GB stays PARK P6.** Salary write half -> F3/EPIC-D02. |
| F3 | 2026-08-03 | Cursor session (founder follow-up) | Must loop/check-back/navigate like an app with operations (not read-only): ask "is it that one?", amend value, ask user to confirm, then continue. Governed - not off-rails, not too weak. Explicitly for writes/amendments (salary increment), distinct from DMS exclusion-loop bug and from D01 read path. | EPIC-D02 | **Founder YES (b) 2026-08-03.** Wave Demo-1 **EPIC-D02** authorized on `demo/rag-ops-confirm` (do not pollute D01 scores). Cortex-direct honesty. Cross-ack Cortex PRD-001 F1: actions = only write path if real writes. Tickets: OPS-DEMO-01..03. |
| F4 | 2026-08-03 | Cursor session (founder follow-up) | Improve check for other models e.g. Mistral, NVIDIA; OpenVault error "Looks like a nvidia key, but that provider is not in the catalog yet"; freenvidia-key / NVIDIA_API_KEY=nvapi…; want test/check and select best model via docs. | OpenVault PRD-001 (plane 2) | **Founder YES (c) 2026-08-03.** OpenVault: add **nvidia** to PROVIDER_CATALOG + freenvidia/nvapi probe; evaluate NVIDIA models for retrieval+reasoning Excel/RAG fit. No AirGPT vault. Serves: OV F1 YES. AirGPT P7 stays parked until OV catalogs nvidia AND vault-first consume is authorized. |
| F5 | 2026-08-03 | Cursor session (founder YES extras) | Link to open file explorer on the original source files (OS reveal / open containing folder) from the demo UI or answer citations. | EPIC-D01 | **Founder YES.** Ticket RAG-BENCH-07 under D01. |
| F6 | 2026-08-03 | Cursor session (founder YES extras) | Form ontology first from workbook semantics (columns/entities/relations), then show logics and answers on top of that ontology - not blind retrieve-only. | EPIC-D01 | **Founder YES.** Ticket RAG-BENCH-08 under D01 (clear ownership). D02 identify-row consumes ontology; do not duplicate under D02. |
| F7 | 2026-08-03 | Cursor session (founder follow-up) | Make backend faster/stronger with load balancer; **host mode especially** (`clipdrop.py` `ThreadingHTTPServer` on `:8765`, `hosting.py` Colibri/vLLM health). | EPIC-D03 / park | **Founder YES (a) 2026-08-03.** **F7a MVP:** in-process speed on one strong PC — cache `/api/info`, HTTP keepalive, throttle host pings — **EPIC-D03** on `demo/rag-cross-compare` (implement immediately OK). **F7b park:** true LB / multi-worker — **P8**. |
| F8 | 2026-08-03 | Cursor session (founder follow-up) | Every chat and API request needs a **really strong secure establishment handshake** and improvement (beyond current passcode + `_is_local_host` + host-only prefixes). | EPIC-D03 / OpenVault / park | **Founder YES (a) 2026-08-03.** **F8a MVP:** explicit establish (`/api/establish` or hardened `/api/probe`), session nonce + `X-AirGPT-Security-Version` headers, bind chat token, audit mismatch — **EPIC-D03** on `demo/rag-cross-compare` (implement immediately OK). **F8b OpenVault:** custody handshake stays OV (`openvault_bridge.handshake`); vault-first consume **P7**. **F8c park:** mTLS mesh — **P8**. |
| F9 | 2026-08-03 | Cursor session (founder follow-up) | Clearer RAG demo process: **file select -> ingest -> answer** (founder lost in CLI runbook). | EPIC-D01 docs | **Guidance only.** Built path: create/import space -> `POST .../upload` or `.../import` -> `.../build` -> `POST /api/rag/answers`. Extend `tests/RAG/DEMO_RAG.md` with a 3-step founder walkthrough; UI file-picker is optional thin surface — not blocking demo. |
| F10 | 2026-08-03 | Cursor session (founder) | All ingested files in RAG: hover card has a file icon bottom-right; press opens File Explorer on the original stored file (auditable cross-check). | EPIC-D01 / #14 | **YES — extend #14 (RAG-BENCH-07), not a new ticket.** Premise check: `POST /api/rag/reveal-path` + `rag/reveal.py` already open Explorer `/select,`; STATUS Next already queued thin UI button. Acceptance add: hover icon on ingested file cards (not only citation row). Epic-agent: amend #14 body; do not open RAG-BENCH-10 for UI-only. |
| F11 | 2026-08-03 | Cursor session (founder) | Securely store as a backup in the RAG Space like a Docs folder — goal: cross-reference check if the answer is correct (auditable). | EPIC-D01 / park | **Split.** **F11a YES** thin under D01: new ticket **RAG-BENCH-09** — retain byte-faithful originals under space-local `Docs/` (or `blob/<id>/docs/`); reveal may target that path. Premise: today `blob/.../sources` is post-extraction `.txt` only (`rag/ingest.py` ~370-384), not original binaries. **F11b PARK P9:** encryption, ACL mesh, vault-grade custody of Docs backups — unlock when founder accepts vault-first custody OR DR that demo plaintext Docs is enough forever. |
| F12 | 2026-08-03 | Cursor session (founder) | Next: provide strong reasoning (on answers). | EPIC-D01 / #15 | **YES — extend #15 (RAG-BENCH-08), not separate / not park.** F6 already owns ontology -> logic -> answer; STATUS reports ontology+logic steps live. Extend acceptance: founder-visible strong reasoning chain (why this entity/row/number) sufficient for audit cross-check with F10/F11a — not a new CoT product epic. If #15 closes weak, epic-agent files a follow-on under D01 only after completeness check. |
| F13 | 2026-08-03 | Cursor session (prior chat 66233508 + founder follow-up) | Prior session generated ~hundreds-MB–~1GB messy fixtures; RAM guidance on 6 GB laptop: realistic raw text corpus ~100–200 MB (safe). NEW: (1) demo under SiRA-inspired path again (`rag/sira.py` / `sira_max`; not full Meta SIRA P2); (2) benchmark/compare variants aiming best approach to **~99% retrieval then generate**; (3) perfect use-case pack **~50 MB total** — **4 workbooks ~12 MB each**; (4) chunk+ingest+demo and **retrieve original file** (Docs/ reveal — #20/#14). | EPIC-D01 / #13 (+ consume #20/#14) | **belongs_to OPEN EPIC-D01.** Not reopen. Not PRD amendment (scale-*down* inside F2a envelope; SiRA-inspired already in D01; 99% is sharper demo bar not new product). **Not park** — P2 (full Meta SIRA) and P6 (true 2GB) untouched. **Epic-agent:** amend #13 from few-hundred-MB primary to laptop-safe **~50MB / 4×~12MB workbook** demo pack + SIRA vs hybrid(+adaptive) cross-compare toward ~99% retrieval; treat existing ~317MB `tests/RAG/messy/` as optional local stress only (not demo-day requirement). Wire verify: Docs originals via #20 + reveal #14. Do **not** file a second epic; new ticket only if epic-agent judges #13 overloaded (sketch: RAG-BENCH-10). |
| F14 | 2026-08-03 | Cursor session (founder FRTR MAX RAG fail) | Q: "Find the average OnTimeSLA for all base rate above 1". System refused ("cannot be computed from the provided evidence"); correctly found `frtr_00027_supply-chain-regional.xlsx` but used Summary-only OnTimeRate/AvgCost chunks — missed Carrier master (`BaseRate`, `OnTimeSLA`, ~143+ rows); mixed irrelevant web conversion-rate sources. Wants: after workbook locate, continuous SQL-style ops (filter BaseRate>1 → AVG OnTimeSLA); chunks too metadata-heavy for numeric KPI; ticket soon; connect DMS for strong regex + glossary/standard prompts (AirGPT RAG ↔ DMS). | EPIC-D01 / new RAG-BENCH-10; DMS cross-product → P10 | **belongs_to OPEN EPIC-D01.** Not reopen. **Not amend #13 as owner** (#13 = pack/scoreboard; may **depend on** RAG-BENCH-10 for numeric KPI toward ~99%). **Not amend #15 as owner** (#15 = readable reasoning; **consumes** SQL/sheet provenance when present). **Not PRD amendment** for continuous SQL (inside D01 golden FRTR KPI + playbook SQL-per-workbook). **Epic-agent:** file **RAG-BENCH-10** under #6 — accept: frtr_00027 Q returns numeric avg + sheet/SQL provenance, not missing-evidence; continuous filter→aggregate after file locate; reduce metadata-only reliance; suppress off-topic web on workbook-bound KPI. Premise: `rag/answer.py` `_try_hybrid_sql_lane` + `tests/RAG/frtr_sql_baseline.answer_sqlish` is keyword-heuristic (unit-cost etc.), not continuous NL→SQL over Carrier master. Cite playbook + excel-rag API crosswalk. **PARK P10:** shared DMS regex decision + glossary/standard prompts — AirGPT may ship local schema/SQL glossary for FRTR without waiting on DMS. |
| F15 | 2026-08-03 | Cursor session (founder FRTR Excel Copilot win vs RAG fail) | Same `frtr_00027_supply-chain-regional.xlsx`. Q: OnTime=true avg cost + export separate xlsx + chart/viz for PPT. AirGPT MAX RAG refused (no OnTime=true / empty Summary / web noise). Excel Copilot succeeded (~USD 300.27 avg; 184k/200k OnTime; Cover/OnTime Export/Analysis/Presentation Chart; AVERAGEIF+FILTER). Product ask: sophisticated multi-part Qs need stronger path than RAG alone — identify workbook + structure prompts → open Excel → paste into Excel Copilot panel (MCP and/or panel control) → Excel does the rest → extract resulting workbook; cross-excel orchestration is most important; connect `D:\DMS`; **PRD→epic→tickets now, build later**. | Wave Demo-2 EPIC-D04 (AirGPT) + DMS EPIC-016; P3 superseded | **PRD amendment authorized by founder (file epic/tickets; leave build later).** **Not** F14/#21 (in-process continuous SQL after locate — keep parallel). **Not** ticket under EPIC-D01. **Not** reopen P3 as AirGPT-owned AI chart-intent — **supersede P3** into DMS-owned Excel-native orchestration; AirGPT = identify + prompt pack + handoff/reveal only (OOS second orchestrator stands). **Not** EPIC-013 chart_spec (in-engine insights) or EPIC-014 ask/preview MCP reopen. **Epic-agent (AirGPT):** file EPIC-D04 + XLSX-ORCH-01/02 under AirGPT; label post-demo / blocked on DMS EPIC-016; do not start runners yet. **Epic-agent (DMS):** file EPIC-016 + XLSX-ORCH-10..12; Serves: AirGPT PRD-001 F15. Tickets filed: AirGPT #22-24; DMS #29-32. **NEEDS-YOU RESOLVED 2026-08-03 founder:** (1) **Pointer-primary** paste into Excel Copilot panel (preferred over MCP paste; `user-excel` MCP = secondary/optional research only). (2) **Excel Copilot IS accepted path dependency (YES).** Pipeline: AirGPT RAG identify+draft insightful pack → DMS governed cross-check/strengthen/validate → Pointer paste on correct workbook → DMS extract → AirGPT reveal. F14/#21 SQL parallel. Epic-agent: amend #22-24 + DMS #29-32 bodies (Pointer-primary + DMS cross-check ownership); do not start runners yet. P10 stays parked (prompt glossary may later feed packs). |
| F16 | 2026-08-03 | Cursor session (founder FRTR Bench Settings) | On existing RAG (FRTR Bench, Settings, Private, LLM ON): sees Rebuild / Export / Archive / Evidence policy but wants to change **index depth**, **architecture**, and **adaptive/auto** after create; select new settings then **Rebuild whole pipeline** so extract→chunk→enrich→embed→index runs under the new config. Context: rechunk/rebuild because current chunks weak; not hybrid SQL + SiRA; chat already has effort — index side needs depth ranking + choose + manual rework after pipeline. Applies to every RAG, not one-off. | EPIC-D01 / [#25](https://github.com/jian-hong/AirGPT/issues/25) RAG-BENCH-11 | **belongs_to OPEN EPIC-D01. YES — filed RAG-BENCH-11 as [#25](https://github.com/jian-hong/AirGPT/issues/25) (not amend #13/#21/#15).** Not reopen. **Not PRD amendment** (create already carries depth/arch into space config; D01 acceptance already includes depth/adaptive variants; Settings gap is SURFACE). **Not park.** Honesty: `depthOpts`/`archOpts` computed in Settings tab (~9988–9989) but **never rendered**; Name/Share/Evidence/Export/Rebuild/Archive only; `ragSaveSettings` already expects `#ragSetDepth`/`#ragSetArch` and POSTs `depth_default`+config; `ragRebuildSpace` exists. Adaptive/auto = **space default** (Save→Rebuild + default answers); chat effort stays **query-time override**. Demo-variant (`hybrid_max`/`sira_max`/`adaptive`) related but not a substitute for Settings. Do not fold into #13 pack, #21 SQL correctness, or #15 reasoning. |
| F17 | 2026-08-06 | Claude Code session (founder) | "i dont want skills to exist, skills are tools that can be used by our normal llm engine Cortex". Remove the user-facing Skill card + Use button from the Snippets/Agents panel; the capability stays as tool-calling inside the engine. | none - **PRD amendment** | **NEEDS-YOU - awaiting founder.** Maps to NO open epic (D01 is the RAG bench, D02 ops-confirm, D04 Excel handoff). Premise verified: `snippetCardHtml` (index.html:6950-6965) renders kicker "Skill" plus a Use button from `GET /api/skills`; `useSkillSnippet` arms `pendingSkill`, which rides the next send as the `skill` field (index.html:12999) and as `skill_pack` on `/api/agents/<id>/run` (7501); `agent_runtime._load_skill()` injects the markdown into the prompt. So "skills" today are a gallery **plus** an authoring surface (Settings "Rules and Skills", create/import/scope/delete) **plus** a wire field - not just cards. **Two halves, different tiers:** removing the gallery is SURFACE (an afternoon); asserting "tools are engine-internal, agents are the user-facing reusable unit" is BOUNDARY and is what constrains F18/F19. **Contract impact:** if the client stops sending `skill`/`skill_pack` and the engine selects instead, that is additive; if the field is deleted, it is **breaking - and a breaking change is a decision record, not an epic**. **Repo split:** AirGPT owns the surface removal only; tool selection is Cortex's by NETIE.md section 3. **Recommend a DR** - this boundary crosses repos and will be re-litigated every session otherwise. |
| F18 | 2026-08-06 | Claude Code session (founder) | Agents panel copy is fine but the suggested agents under it are toy examples ("Daily insights on does music give people chills", "Daily dance tutorial", "Morning news brief daily", "Weekly memory digest Mondays 8am"). "inside should be something working and something useful" - suggested agents must be real, runnable, tied to actual workflows. | none - **PRD amendment** for the content ask; **the recurrence claim is a live defect** | **NEEDS-YOU - awaiting founder, with one part that needs no amendment.** Premise verified: `HABIT_AGENT_ACTIONS` (index.html:4365) and `cortexSuggestionChips()` (6853-6859) hardcode the starters; `suggestedAgentsFromTrend()` reads localStorage taste, so the mechanism is real and only the seed content is toy. **The defect (R-0011 / NETIE.md rule 6, a silent fallback is a lie):** clicking "Morning news brief, daily" routes through `ensureCortexAgent` (index.html:7533-7539), which sets `kind:'scheduler'` and writes `schedule_hint` - **and `schedule_hint` is read by nothing in the estate** (single hit, index.html:7539). Nothing ever fires. Meanwhile the real Cortex routines scheduler is already wired at `cortex_client.py:613-647` and is not called by this path. Two paths for one user intent, one real and one dead - NETIE.md rule 4 says merge them, do not special-case. **Making that chip honest (wire it to `/api/cortex/routines`, or stop claiming recurrence) widens nothing and is the only item in F17-F20 that needs no amendment** - it makes a shipped surface stop lying. It still has no open epic to hang on. |
| F19 | 2026-08-06 | Claude Code session (founder) | "cortex it is not just create functions it is creating agents ... agentic working and can be reused and help in real workflows like a scheduler like a real world email connector orchestrator, then real world in your pc a small downloadable python function, with backend that can run and useful with website online also". Six asks: (1) reusable persisted agents (2) scheduler (3) real-world connectors, email named (4) decomposing orchestrator (5) downloadable local Python artifact (6) backend that runs it, online too. Manus research supplied: sandbox VM per task, orchestrator + sub-agents, action/observation loop, filesystem as memory, todo.md recitation, action masking over tool removal, KV-cache hit rate as the production metric. | none - **PRD amendment; recommend a new PRD, not an amendment to this one** | **NEEDS-YOU - awaiting founder.** Does not serve PRD-001's success assertion (vault-first key/route resolution). Premise check, item by item: **(1) already exists** - `agent_store.py` SQLite `agents` table + `/api/agents` CRUD + pinning; agents are persisted objects today, not one-shot functions. The gap is that they are thin. **(2) already exists, and it is Cortex's** - `cortex_client.py:613-647` proxies Cortex `/api/routines` draft/create/pause/resume/run/delete with `next_run_at`, `schedule_text` and a governor; AirGPT drives it from the Routines page. Do not build a second one (see F18). **(3) does not exist** - `email_resend.py` is outbound Resend for waitlist/security alerts only; `mcp_wanted` is a UI hint string with no Python behind it. A user-inbox connector needs OAuth credentials, and **custody is OpenVault (plane 2)** - AirGPT must not hold Gmail tokens. **(4) collides with NETIE.md section 6** - "a third orchestrator" is on the do-not-build list and AirGPT "is not a second orchestrator"; decomposition/delegation is Cortex `dag_runner`. `subagent_dispatch` in `agent_tools.py:722` is already a thin local version and is the wrong direction. **(5) does not exist** - `app_scaffold` writes `apps/<slug>/` into AirGPT's own hub with a registered port; `apps_hub.py` has no download/export/zip path. Shipping executable Python to a user's PC is a code-signing and supply-chain decision, not a feature. **(6) sandbox VM is plane 0/1** - NETIE.md declines it; renting is a packaging decision, building is not AirGPT's. **Repo split if authorized:** engine-side agent/orchestration -> Cortex; connector credentials -> OpenVault; sandbox -> neither, rent it; AirGPT owns surface only. |
| F20 | 2026-08-06 | Claude Code session (founder) | Tool-call surfacing must match Claude Code: collapsed, grouped summary rows per turn segment ("Ran a command, searched code, browsed the web, used a tool", "Read frtr_eval.py, used 3 tools", "Edited frtr_eval.py, ran 2 commands, searched code  +25 -4"), distinct tool kinds, counts, +added/-removed diff stats, expandable. | none - **PRD amendment** | **NEEDS-YOU - awaiting founder.** Maps to NO open epic. **Not** #15/RAG-BENCH-08: that is the RAG answer reasoning chain (`cot-body`/`cot-step`, index.html:12649); this is the agent run stream (index.html:7519). Folding it into #15 would be scope-smuggling of the kind F13/F14/F16 rows explicitly refused. Premise verified: the SSE loop already emits `type:'tool'` with `j.name` and `j.result`, and renders one flat line per event with no grouping, no counts, no diff stats, no expand. Cheapest of F17-F20: pure SURFACE, in-AirGPT, **no contract change, no new capability**. Diff stats (+N -M) need `fs_write`/`fs_patch` to return line deltas - `agent_tools.py` does not today. |
| F21 | 2026-08-07 | Claude Code session (founder, live server) | **DEFECT.** Remote access over tunnel is unreliable to unusable. Verified live against the running server (PID 45120, `0.0.0.0:8765`), not from a screenshot: `/api/info` returned `tunnel_url: null`, `tunnel_healthy: false`, `tunnel_status: "localhost.run unreachable"`, `tunnel_error: "https://admin.localhost.run did not pass /api/probe"`, `lan_url: http://172.20.10.2:8765` (iPhone hotspot), `network_profile: "Unknown"`. Founder additionally reports localtunnel (`loca.lt`) "totally down, cannot use". | **OPEN EPIC-D03 [#26](https://github.com/jian-hong/AirGPT/issues/26)** - new ticket sketch HOST-DEMO-03 | **belongs_to OPEN EPIC-D03. Not a PRD amendment, not a reopen.** Remote reach is a shipped capability and D03's own acceptance already reads "opens AirGPT over tunnel or LAN" - that clause was never testable from the customer seat, so this is a defect in the epic in flight, and **the fix belongs in the current wave.** **Decomposition gap named:** EPIC-D03 was founder-authorized 2026-08-03 and never filed as a GitHub issue while its work landed (`769c9c52` = HOST-DEMO-01 F7a). Filed 2026-08-07 as [#26](https://github.com/jian-hong/AirGPT/issues/26); no scope added by the filing. **Root cause (code-verified):** `_read_tunnel_url` returned on the **first** line matching **any** pattern; localhost.run prints `https://admin.localhost.run` in its banner before the real `*.lhr.life` URL, so the console link always won, `_set_tunnel` probed and rejected it, `_kill_tunnel_procs()` killed the ssh session before the real URL was emitted - localhost.run could **never** succeed on any network on any attempt. Root-cause **CLASS** (R-0004): first-match-wins over a pattern list with no non-tunnel-host exclusion; `tunnel_serveo` carries the same shape. **Class fix already in the working tree:** `_BANNER_LABELS` + `_is_banner_url` (`clipdrop.py:1678-1686`) reject banner/console hostnames as a class and keep reading. **Not covered, remains HOST-DEMO-03 work:** `_probe_tunnel_url(attempts=24, delay=2.0)` (`clipdrop.py:1577`) burns ~48s per doomed candidate and `tunnel_worker` (`clipdrop.py:1820`) sweeps 4 providers x 2 attempts, so total failure takes minutes of "trying <provider> (retry 2)" churn - **R-0011**, motion in the UI while the product is unreachable. **cloudflared is not missing** (`bin/cloudflared.exe`, 54MB, 2026-08-02); it failed to emit a `trycloudflare.com` URL in its window, consistent with the quick-tunnel rate limit and/or hotspot blocking - environmental, but the product must say so. **R-0005 check:** the fix must not get so conservative it rejects a working tunnel - re-run on a network where one works. **Open question, not settled:** loca.lt availability is one report; do not hardcode a provider removal on it. |
| F22 | 2026-08-07 | Claude Code session (founder) | **FEATURE REQUEST.** Verbatim: "AirGPT the interface cannot use in laptop (Host), and on top of there should be a bar grant what kind of access." Read as: the product is usable only on the host laptop, and the founder wants a bar on the connected-devices surface that grants a connected device a **class** of access (chat-only / read knowledge / full agent) instead of the current binary of host-everything vs remote-nothing. | **Split.** F22a: **none - PRD amendment, NEEDS-YOU.** F22b: **OPEN EPIC-D03 [#26](https://github.com/jian-hong/AirGPT/issues/26)** - ticket sketch HOST-DEMO-04 | **NEEDS-YOU 2026-08-07 for F22a - founder's call.** **Premise correction (verified, flag back to the parent session):** the bar is **not missing**. `hub.py:13` defines `ACL_LEVELS = ("read_only", "read_write", "use_host_ai", "use_own_ai", "limited")`; the Hub renders a per-peer "Edit access" menu (`index.html:6633` `hubPeerMenu`) that POSTs `/api/hub/peers/<ip>/acl` (`index.html:6610`); `hub.py:245` `set_peer_acl` persists it. **It grants nothing.** The gate is `if _is_host_only_path(path) and not _is_local_host(ip): 403 "host only"` at `clipdrop.py:2546` (GET) and `clipdrop.py:4026` (POST) - IP-only, never consults `access_level`. The sole consumer is a display label (`hub.py:306-314` -> `ai_source`). So the founder's ask is not "add a bar", it is **"make the bar that already exists mean something"** - which is a security-boundary change, not a surface one. Parent-session premise on the block itself confirmed: `_HOST_ONLY_PREFIXES` (`clipdrop.py:786-804`) blocks 17 surfaces including `/api/rag`, so a phone that connects over the tunnel still gets 403 on the actual product, and the comment at `clipdrop.py:780-785` already names the dependency - "remote OpenIDE would need a distinct capability token (a later phase), not the guest chat token". **Why F22a is an amendment and not a ticket:** it maps to no open epic (D01 = RAG bench, D02 = ops-confirm writes, D03 = F7a perf + F8a establish, D04 = Excel handoff); D03's authorized scope is the establish handshake and its own honesty line defers custody to **F8b OpenVault / P7**; and it changes the **threat model** of a gate deliberately shipped closed, which no epic may absorb without sign-off. **Recommend DR-0003** in `D:\AirGPT\docs\decisions\` before any build - it crosses a repo boundary (token custody is OpenVault, plane 2 - AirGPT must not become a second key vault, NETIE.md section 3), it is expensive to reverse, and an agent will re-derive it every session otherwise. Same shape as F17, where a boundary claim was routed to DR-0002 rather than an epic. **Named dependency:** the capability-token design. **R-0005 cuts both ways and must be stated in the DR:** the gate refusing the founder's own phone **is** a control refusing legitimate work; and a grant bar that opens `/api/fs/`, `/api/terminal/` or `/api/agents/` to a device on a phone hotspot is the failure in the other direction. The DR must name which of the 17 prefixes each class may reach, and the default must stay closed. **F22b YES, no amendment needed:** the access bar presenting itself as granting access while granting nothing is **R-0011**, the same shape as the dead `schedule_hint` F18 fixed. Making it honest widens nothing -> **HOST-DEMO-04** under [#26](https://github.com/jian-hong/AirGPT/issues/26). Honesty only; it must **not** make `access_level` load-bearing - that is F22a. **NEEDS-YOU RESOLVED 2026-08-07 - founder answered YES with a design.** Access becomes **level-based**; shareable classes are the three he named ("read / use host / use api (own compute)" = `read_only` / `use_host_ai` / `use_own_ai`), plus per-file granularity, durable project-folder share links, a handshake on every entry, a host-side approval queue with a minimise-to-bottom-right unresolved indicator, and - ranked most important by him - an authentication code shown by the host and typed by the client. Recorded as **DR-0003** `docs/decisions/0003-level-based-access-grants-replace-the-binary-host-only-gate.md`, status **proposed** (the PR is the RFC). **Finding that changes the shape of the ask:** the auth code he ranked most important **already exists and is the weakest part** - `auth.py:289-314` mints `secrets.token_hex(3).upper()` (24 bits), `JOIN_CODE_TTL` is 48h (`auth.py:254`), and `redeem_join_code` (`auth.py:317-336`) **never removes the code**, so one code mints unlimited guest tokens for two days. The gate currently masks that by refusing guests everything worth having; opening the gate removes the mask. **Deferred by DR-0003 decision 3:** per-file grants - no per-file ACL exists in the data model, and it is the manifest-enforced-read problem arriving in AirGPT. **Fence decided:** 16 of the 17 `_HOST_ONLY_PREFIXES` stay shut to every shareable level; only `/api/rag` read paths open, plus `/api/ai/*` for the two compute levels; positive allowlist, unknown prefix = 403. **Five founder-owed parameters remain** (shareable set, per-file staging, link lifetime, absent-host rule, code TTL and binding) - **build blocked until DR-0003 is accepted.** |
| F23 | 2026-08-07 | Claude Code session (founder, inside the F22a answer) | **DEFECT.** Verbatim, mid-sentence: "now the access and share qr in hub is not working". Two halves of the Hub - the access control and the share QR - both reported broken today. Separate from F22a: F22a is the future capability, this is the existing surface failing. A parallel parent-session investigation is root-causing both halves in code with adversarial verification; this row records the **routing rule decided before the evidence arrives**, so the answer is not fitted to the finding. | **Conditional - see rules.** Default landing: **OPEN EPIC-D03 [#26](https://github.com/jian-hong/AirGPT/issues/26)** | **Routing decided in advance, by cause (2026-08-07).** **(A) Access half - the ACL bar does not persist, does not render, or errors on save:** same surface and same class as the already-sketched **HOST-DEMO-04** (the bar grants nothing). **Amend HOST-DEMO-04**, do not open a second ticket - one surface, one owner. **(B) QR carries no credential because no passcode is set:** `auth.py:158-168` `issue_qr_token` returns `None` when `pass_hash` is unset, and `clipdrop.py:1961-1967` `_join_url` returns the bare base URL when `needs_auth` is false - so in the default no-passcode state the QR is a link, not a credential. **New ticket HOST-DEMO-05 under [#26](https://github.com/jian-hong/AirGPT/issues/26)** - same R-0011 class as HOST-DEMO-04 but a different code path, so it gets its own ticket rather than an amend. **(C) QR encodes a tunnel URL that is stale, invalid, or never came up (incl. `_qr_join_cache.clear()` racing a tunnel change at `clipdrop.py:1637,1766`):** the cause is tunnel URL lifecycle, not authentication - **route to F21 / HOST-DEMO-03**, and extend its acceptance to "the QR encodes a URL that resolves". **(D) QR token simply expired (`QR_TOKEN_TTL = 600`, one-time, popped on redeem at `auth.py:171-179`) and the surface does not refresh or does not say so:** not a broken credential, a surface lying about state - **amend HOST-DEMO-04** (honesty), R-0011. **(E) The join succeeds and the phone is then 403ed by the host-only gate:** **not a defect.** That is F22a working exactly as designed, and it routes to **DR-0003**, not to a ticket. This is the rule most likely to be violated: the tempting fix is to open the gate locally to make the symptom go away, which is DR-0003 Considered Option B and is refused there. **If two or more causes hold at once**, file per cause rather than one omnibus ticket - the causes live in three different subsystems (hub ACL, auth token issue, tunnel URL lifecycle) and merging them produces a ticket no single agent run can close. **Not a PRD amendment under any cause** - every branch above is a defect in a shipped surface or a decision already captured in DR-0003. |

---

## 8. Review

Silent read before any vault-first slice. F1 demo must not silently become the product trunk success assertion.

**Demo claims:** Cortex-direct. **Not** OpenVault-gated. **Not** full Meta SIRA. **Not** AirGPT-owned AI Excel chart governance (P3 **superseded** by F15 Excel-native DMS path). **Write-confirm ops = EPIC-D02 on `demo/rag-ops-confirm` only.** **Not** NVIDIA catalog in AirGPT (OpenVault F1 YES - OV owns). **Not** ~2GB messy (P6). **F13:** demo-facing messy pack = **~50MB / 4×~12MB workbooks** under #13 (SiRA-inspired + hybrid cross-compare toward ~99% retrieval); ~317MB stress optional/local only. **Not** load balancer / multi-worker host farm (F7b **P8**). **F7a+F8a MVP = EPIC-D03** on `demo/rag-cross-compare`. **Not** mTLS mesh (F8c **P8**). **RAG walkthrough (F9) = `tests/RAG/DEMO_RAG.md` only.** **F10 = extend #14 hover reveal UI.** **F11a = space Docs original retain (RAG-BENCH-09); F11b secure Docs custody = P9.** **F12 = extend #15 strong reasoning (not a new epic).** **F14:** continuous SQL after workbook locate = **RAG-BENCH-10** under D01; shared DMS regex/glossary/prompt standards = **P10** (not AirGPT-owned). **F15:** Excel-native Copilot/orchestration = **Wave Demo-2 EPIC-D04** (#22-24 identify+prompt+reveal) + **DMS EPIC-016** (#29-32 cross-check+Pointer→Copilot+extract); **Pointer-primary** paste; Copilot dependency YES; MCP secondary; **NEEDS-YOU closed**; build later; **not** #21; AirGPT remains not a second orchestrator. **F16:** Settings post-create depth/arch/adaptive + Rebuild under new config = **RAG-BENCH-11 [#25](https://github.com/jian-hong/AirGPT/issues/25)** under D01 (render dead `depthOpts`/`archOpts` + Save→Rebuild; not amend #13/#21/#15).

**F17-F20 (2026-08-06) - all four NEEDS-YOU. No epic filed, no ticket filed.**

The reason none of them route is the finding, not the obstacle: **this PRD's product trunk
was never sliced.** Section 5 still reads "Not sliced yet. Press release still TBD." Every
epic beneath it is a demo wave (D01, D02, D03, D04). F17-F20 are all trunk work - the
AirGPT agent surface - so there is no trunk for them to land in. Routing them into a demo
epic would leave the success assertion no longer describing the epics under it.

Three decisions only the founder can make:

1. **The boundary F17 and F19 both rest on.** Tools are engine-internal and selected by
   Cortex; agents are the user-facing reusable unit. Stating this dissolves the apparent
   contradiction between "no skills" (F17) and "reusable agents a user picks and
   schedules" (F19). It meets the Tier 5 threshold - it crosses a repo boundary and an
   agent will re-derive it every session otherwise. **Recommend a DR before any build.**
2. **Whether F19 is a new PRD.** Recommended: yes. It does not serve this PRD's vault-first
   success assertion, and three of its six asks are already refused by NETIE.md section 6.
3. **WIP.** D01 and D02 are both open and both human-inspectable - that is already the
   limit of two. Nothing in F17-F20 starts before one of them closes, absent an override.

**One item needs no amendment and should be separated from the rest.** The "Morning news
brief, daily" chip creates an agent with `kind:'scheduler'` and a `schedule_hint` that
**nothing in the estate reads**, while the real Cortex routines scheduler sits wired and
uncalled at `cortex_client.py:613-647`. A shipped surface promising recurrence that never
fires is NETIE.md rule 6 (a silent fallback is a lie), and two paths for one intent is
rule 4 (merge them; do not special-case). Making it honest is a defect fix, not scope.

---

### RESOLVED 2026-08-06 (same day) - founder decided in session

All three answered. Recorded as **DR-0002** in the AirGPT repo,
`docs/decisions/0002-tools-are-engine-selected-agents-are-the-user-unit.md`, status
`accepted`. F17-F20 are **no longer NEEDS-YOU**.

1. **Boundary: ACCEPTED as recommended.** Tools are engine-internal and Cortex-selected;
   agents are the user-facing reusable unit. Founder added the decisive refinement: the
   gallery goes because it *"use up too many space"* and should *"become like something
   auto wire for user instead of let them press"*, **but** explicit selection survives as a
   slash command (`/anthropic-skills:lazy-senior-dev`). Auto by default, explicit always
   available and always wins.
   **Contract impact revised to none.** `skill` / `skill_pack` is **kept** and becomes
   engine-populated rather than client-populated - additive, not breaking. The breaking
   variant (delete the field) is declined.
2. **F19: orchestrator DECLINED outright.** Founder: *"no need the orchestrator, the
   orchestrate still depends on the central orchestrator."* Confirms NETIE.md section 6;
   AirGPT never decomposes or delegates. The remainder of F19 (connectors, downloadable
   local artifact, online backend) still wants **its own PRD** - not decided here.
3. **WIP: unchanged, and now moot for this batch.** Founder is running D01 and D02 in a
   separate agent. Nothing in F17-F20 is being built in parallel.

**F18 shipped the same day** and needed no amendment, exactly as the paragraph above
predicted: AirGPT `7b794f67` wires the daily/weekly chip to the real Cortex routines
scheduler and refuses visibly when Cortex is down. Verified live - routine `rt-dd286103`,
`interval_seconds: 300`, forced run `status: completed`, `next_run_at` advanced.

**F20 was re-scoped by the founder and split.** It is not surface-only. Founder: *"need
loop tool calling and measure if quality of output is perfect and loop until enough
connectors enough tools and good answer"*, delegating the call. Analysis in DR-0002
section 6: `agent_runtime.py:542` loops `while step < max_steps and tokens_used <
token_budget` - it stops on exhaustion, never because the answer became good, so grouping
the readout while the loop cannot distinguish a good answer from a spent budget is
polishing the gauge instead of the engine.
- **F20a** grouped tool-call rows - AirGPT surface, no contract change, blocked on
  `fs_write`/`fs_patch` returning line deltas.
- **F20b** quality-terminated agent loop - **Cortex's, not AirGPT's**, per decision 2.

**New founding constraint recorded as DR-0002 decision 5.** The assistant hand-wrote a
pomodoro timer; the founder rejected the premise: *"the pomodoro is not an app u do for me
it should be generate by the agent, the agent need to be very useful and can do anything
not u create and run."* The deliverable is the **capability to generate**, never the
generated artifact. `pomodoro.html` is reclassified as a **fixture and acceptance target** -
`app_scaffold` must reproduce it from a one-line ask, then the hand-written file is deleted.
Machinery already exists and has been exercised: `apps/` holds five agent-scaffolded apps
(`counter-smoke`, `hello-ship-demo`, `todo-demo`, `vdml-sheet-demo`, `pw-smoke-app`).

**Capability gaps surfaced while deciding** (none previously ledgered): no image or pixel
generation exists anywhere in the estate, so the "describe the clock shape, become pixels"
idea has nothing behind it; Gemini is wired for **text only** (`gemini-2.0-flash`,
`gemini-2.5-flash`); `app_scaffold` has no download/export path, so "a small downloadable
python function" does not exist and is a code-signing decision before it is a feature.

---

### F21-F22 (2026-08-07) - remote reach, and the bar that grants nothing

**F21 routed into an open epic. F22 split - half routed, half is the founder's call.**

The finding underneath F21 is not the regex. It is that **EPIC-D03 was founder-authorized
on 2026-08-03 and never existed on GitHub**, while its work landed anyway (`769c9c52`).
The PRD said "AUTHORIZED to file" and nobody filed. That is a decomposition failure of the
same kind the routing rule exists to catch, and it is why a defect blocking D03's own
acceptance had nowhere to be filed for four days. Epic now filed as
[#26](https://github.com/jian-hong/AirGPT/issues/26).

D03's acceptance also failed the Tier 3 test that a success assertion must be testable from
the customer's seat. It read "opens AirGPT over tunnel or LAN" while the tunnel could
**never** come up on any network. An epic whose acceptance cannot be reached is not passing,
it is untested. Acceptance amended.

**F22 is the more expensive one, and it is not the feature it looks like.** The founder
asked for "a bar grant what kind of access". That bar already ships: five `ACL_LEVELS`, a
per-peer Edit-access menu, a POST endpoint, a database column. It changes a **label**. The
request gate is IP-only and never reads it. So the ask decomposes into a shipped lie
(F22b, R-0011, a ticket) and a threat-model change (F22a, the founder's call).

F22a must not be absorbed into D03. D03's authorized scope is the F8a establish handshake,
and its own honesty line already defers custody to **F8b OpenVault / P7**. Granting a remote
device a class of capability is a different decision from proving who a device is, and
`clipdrop.py:780-785` has been saying so since before the founder asked - "a distinct
capability token (a later phase), not the guest chat token."

**Recommend DR-0003 before any build.** Three of the four Tier 5 thresholds hold: it crosses
a repo boundary (token custody is OpenVault, plane 2), it is expensive to reverse, and an
agent will re-derive it every session otherwise. The DR must name, for each access class,
which of the 17 `_HOST_ONLY_PREFIXES` it may reach, and must keep the default closed. It
must also carry both directions of R-0005 explicitly: the gate refusing the founder's own
phone **is** a control refusing legitimate work, and a bar that hands `/api/terminal/` to a
device on a hotspot is the same rule failing the other way.

**WIP unchanged.** D01 (#6) and D02 (#16) remain the two primary human-inspectable lanes.
D03 (#26) is a thin add-on on the same branch, not a third. Nothing under F22a starts before
the founder answers.

---

### RESOLVED 2026-08-07 (same day) - founder answered F22a in session

**F22a is YES, and it is level-based.** Recorded as **DR-0003**,
`docs/decisions/0003-level-based-access-grants-replace-the-binary-host-only-gate.md`,
status `proposed` - the pull request is the RFC (DOCUMENT_SYSTEM Tier 5). F22a is no longer
NEEDS-YOU. **It is also not yet buildable**, and the distinction matters: the founder
answered the question that was asked, and the answer contains five further parameters only
he can set. They are listed in the DR as FOUNDER OWES.

**The finding that reframes his own priority.** He ranked one control above everything else
in his message - *"most importantly need give authentication code from host then client need
to correctly fill in for access"*. That control already exists, and it is the weakest thing
in the design:

- `auth.py:289-314` mints the code as `secrets.token_hex(3).upper()` - **24 bits**.
- `JOIN_CODE_TTL` (`auth.py:254`) is **48 hours**.
- `redeem_join_code` (`auth.py:317-336`) **never removes the code**. One code mints
  unlimited guest tokens for two days.

Today that is nearly harmless, because the host-only gate refuses the guest everything worth
having. **Opening the gate removes the mask**, and a 24-bit multi-use two-day code becomes
the front door to whatever the levels grant. So the first work under this decision is not
new capability, it is hardening a primitive that already shipped.

**The clause that costs the most is not the one that sounds biggest.** Per-file access -
*"give them their level of access to each files"* - is one line in his message and is the
only item that requires an object the data model does not have. RAG sources carry no owner
and no grant table; the gate is a path-prefix check that never sees a file id. Filtering
citations by reader is the manifest-enforced-read problem from NETIE.md section 3 arriving
in AirGPT. DR-0003 decision 3 stages it out of the first slice and asks the founder to
accept that.

**What the record refuses, stated rather than buried.** He asked for durable collaboration
links into a machine that also serves `/api/terminal/`, `/api/fs/` and `/api/agents/`. The
fence is DR-0003 decision 2: **16 of the 17 host-only prefixes stay shut to every shareable
level**, only `/api/rag` read paths open, and the allowlist is positive so that a prefix
with no class entry resolves to 403. The predictable way this design fails is a future
prefix added to `_HOST_ONLY_PREFIXES` and not to the class map - silent, and it hands a
public durable link something nobody granted it. That is why DR-0003's Confirmation requires
the test to enumerate `_HOST_ONLY_PREFIXES` at runtime rather than list paths by hand.

**F23 is a defect and is carried separately.** *"now the access and share qr in hub is not
working"* arrived in the same sentence as the design, and it is the surface F22a replaces
failing today. Its routing was decided **before** the investigation reported, so the answer
is not fitted to the finding - see the F23 ledger row for the rule per cause. The rule most
likely to be broken: a join that succeeds and is then 403ed by the host-only gate is **not a
defect**, it is F22a working as designed, and opening the gate to make that symptom go away
is DR-0003 Considered Option B, which the record refuses.

**WIP recommendation, unchanged and now more pointed.** D01 (#6) and D02 (#16) are the two
primary lanes and both are still open. F22a is a security boundary being deliberately
loosened; it is the last thing that should be built while attention is elsewhere. **Finish
D01 and D02 first.** DR-0003 costs nothing to hold in `proposed` while that happens, and
review time before a threat-model change is the cheapest review in the estate.
