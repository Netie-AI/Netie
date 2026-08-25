# PRD-001 - Governed engine for consumers

**Product:** Cortex
**Owner:** founder
**Status:** draft - not yet sliced
**Repos in scope:** `Netie-AI/Cortex`
**Created:** 2026-08-03

**Companion:** [PRD-001 (DMS) - Governed answers over your own data](../DMS/PRD-001-governed-answers-over-your-own-data.md). DMS is the first consumer that proves this engine; AirGPT and Pointer inherit the same manifest enforcement and ledger spine.

---

## 1. Press release

### [HEADLINE TBD] - an engine that refuses rather than guesses

**Subheading:** [customer + benefit TBD - for teams building on governed data]

**Problem:** [customer words TBD - orchestrators answer fluently; auditors cannot trace rows, SQL, or who was allowed to see them]

**Solution:** Cortex is the governed execution plane: manifest-enforced reads, hash-chained ledger, actions as the only write path, abstain over guess. Consumers speak HTTP; they never import the engine.

**Quote:** [pilot customer TBD]

**Call to action:** [TBD]

---

## 3. Out of scope

- Inference serving (plane 1) - Cortex calls models; it does not run them
- A vertical product UI (that is DMS, AirGPT, Pointer, FreeIDE)
- A second key vault (OpenVault owns custody)
- A third orchestrator
- WASM/microVM isolation (host `tool_runner` is the path; WASM modules are 0-byte scaffolds today)

---

## 4. Success assertion

> **WHEN** a consumer submits governed work through the published contract, **THE SYSTEM SHALL** return an answer with evidence (rows, SQL, manifest authorization) or an honest abstention - and **WHEN** a query cannot be proven inside the granted manifest, **THE SYSTEM SHALL** refuse rather than run.

Measured on engine gates and contract tests, then on the consumer envelope (DMS: `POST /v1/chat/ask`).

---

## Cross-product acknowledgement

```
Serves: PRD-001 (DMS) EPIC-001, EPIC-002, EPIC-004, EPIC-005a, EPIC-006
Ack: AirGPT F15 / DMS EPIC-016 Excel-native Copilot path — Cortex owns action/ledger gate only if exports become governed writes; do not invent a second orchestrator in AirGPT
```

AirGPT and Pointer consume manifest enforcement from the same engine work; they do not own DMS epics.

---

## Feedback ledger

| # | Date | Raised in | Feedback | Routed to | Outcome |
|---|------|-----------|----------|-----------|---------|
| F1 | 2026-08-03 | AirGPT PRD intake (founder via Cursor) | AirGPT demo wants governed write loop: identify row ("is it that one?"), amend (e.g. salary increment), confirm, then continue - not read-only RAG. | AirGPT EPIC-D02 (AUTHORIZED) | **Founder YES on AirGPT D02 2026-08-03.** Cortex ack: actions remain the only write path. AirGPT D02 may ship a **demo stub** on `demo/rag-ops-confirm` with Cortex-direct honesty. If D02 does **real** writes, file a Cortex confirm/refuse-gate ticket and block AirGPT adoption on it - do not let AirGPT invent a second write path. Serves: AirGPT PRD-001 F3. |
| F2 | 2026-08-03 | AirGPT PRD intake (founder via Cursor) | Excel-native Copilot orchestration for multi-part filter+export+chart (frtr_00027); DMS owns drive; AirGPT surfaces only. | DMS EPIC-016 / AirGPT EPIC-D04 | **Ack only.** If Excel exports become governed writes, file Cortex action/confirm ticket and block consumer adoption — do not let AirGPT/DMS invent a second write path. Serves: AirGPT PRD-001 F15 / DMS F25. |
| F3 | 2026-08-20 | Founder via Cursor (Netie Control lock) | Operator surface is a plane-4 app (Netie Control). Cortex stays engine-only: no UI organ. Customer writes still only through Cortex action types. Control GET-probes health. | none - **ack** | **Ack.** Serves Control PRD-001. No Cortex epic. |

| F4 | 2026-08-22 | Founder override via UX Agent | Constructor must BUILD now as its own repo and public link. Do not keep it as a parked Cortex/RUMA Flows vertical. n8n banned. Activepieces clone at D:\\Cortex\\activeflow\\activepieces stays un-wired in Cortex. | **out of Cortex PRD** | **Ack. Cortex does not own constructor.** No Cortex ticket. No Space-grant mint. New unused Cortex branches only if Cortex work appears; this ask is not Cortex. |
| F5 | 2026-08-22 | Founder Constructor workspace (PRD Agent) | Chats die in chat; Constructor lacks Cortex connectivity; far from ontology/Palantir-as-a-service; check-measure-improve; scale PRD+epic+ticket; run chat-to-workflows; object kinetics/motion; LEARN via subagents. | **split** | **F4 still holds: Cortex does not own Constructor UI.** Additive Cortex compile of constructor-graph.json -> AgenticDSLProgram is in-engine (new file, not a second orchestrator). Palantir AIP = PARKING_LOT P1, not build-now. O1-O3 PASS in STATUS.md; plan-doc "nothing built" is STALE. Chat-to-workflow = existing distill_ingest.py + captures/workflows, not a new product. Kinetics = (b) object_type transitions via registered action_types on DAG edges (dag_runner TOOL_CALL already exists); not canvas animation. Scale agents = FLEET parallel seat, not a swarm. Constructor has no Software Blueprint PRD - Constructor surface epics await founder PRD. Serves: proposed Constructor PRD. |
| F6 | 2026-08-22 | Ticket Runner handoff of UNROUTED Constructor chat asks (PRD Agent, customer-seat) | chat-to-workflow | **none - PRD amendment.** Maps to no open Constructor epic (repo has 0 issues / 0 PRs). Does not map to landing#9 (static first path, no chat). | **STOP. Do not ticket.** Live https://netie-ai.github.io/constructor/ has Export JSON / Reset / 4 node kinds / port wiring / inspect JSON. No chat box, no prompt-to-DAG. `hls_compiler.py` `HLSCompiler.synthesize` is in-engine intent->AgenticDSL, not a Constructor surface. `scripts/distill_ingest.py` is operator skill distill (P19), not a buyer chat-to-workflow. Constructor export JSON (`app.js` KINDS ingest/hypothesize/improve/audit + edges) is not AgenticDSL (`dsl_parser.py` NodeType TOOL_CALL/INFER_*/EMIT + entry_node_id). F5's "compile constructor-graph.json" claim is a false premise: no such compiler file in Cortex. Not a third orchestrator. Not n8n. Serves: proposed Constructor PRD. |
| F7 | 2026-08-22 | Ticket Runner handoff of UNROUTED Constructor chat asks (PRD Agent, customer-seat) | ontology connectivity | **none - PRD amendment** for Constructor wiring. Engine ontology O1-O5 already PASS in Cortex `STATUS.md` (`packs/dms/ontology/object_types.yaml`). | **STOP. Do not ticket Constructor. Do not start Cortex P1.** Buyer on Pages cannot attach a node to an object_type/link_type. Constructor `app.js` stores localStorage `netie.constructor.v0` only. Cortex does not own Constructor UI (F4). Connecting the live canvas to the engine registry is a new product clause, not an O1 defect. AirGPT RAG-BENCH-08 workbook ontology is a different product. |
| F8 | 2026-08-22 | Ticket Runner handoff of UNROUTED Constructor chat asks (PRD Agent, customer-seat) | object kinetics | **none - PRD amendment** | **STOP. Do not ticket.** Live Pages lets a stranger drag nodes (`app.js` pointermove) and redraw SVG wires. That is canvas drag, not Palantir object-type lifecycle and not `dag_runner.py` TOOL_CALL transitions. F5 option (b) remains an engine reading only; it is not visible on the Pages URL. |
| F9 | 2026-08-22 | Ticket Runner handoff of UNROUTED Constructor chat asks (PRD Agent, customer-seat) | Palantir-as-a-service | **none - PARKING_LOT P1.** Condition: 1+ paying clients, F1-F7 production-hardened. P17 hosted-API is a related park, not a Constructor epic. | **STOP. Do not ticket. Do not start Cortex P1.** Live first path is a static DAG sketch on GitHub Pages, not AIP. NETIE.md section 3 does not name Constructor. Landing copy on https://netie.ai/ still claims Prompt-to-Agent / Autonomy Sliders / Ghost Mode / CoT Debugger; none of those exist on the Pages URL. Do not invent a host. |
| F10 | 2026-08-22 | Founder Constructor workspace (PRD Agent) | LAW: everything must be powered by Cortex. Overrides last-week "no live Pages HTTP". Constructor is the P17 "first external-consumer ask". | **amendment accepted for :8010 consumer path only** | **P17 full hosted-API + self-host packaging stays parked.** O4+O5+POST /run are enough. Cortex serves Constructor at existing :8010 (not a new host). github.io stays 200 brochure, 0 fetch, no keys. F4 refined: Cortex does not own the Constructor repo; it does compile+run+serve the consumer. F6 false premise stands: `constructor_graph.py` still missing; POST /run wants AgenticDSL not constructor-graph.json (`dag_run.py`). Do not add github.io to CORS (`app.py` localhost:3000/:8765 only). Do not bake `dms-demo-viewer-key` into Pages. P1/O6 still parked. Finding `2026-08-22_constructor-ontology-connectivity-gap.md` golden rule "do not wire" is superseded by this law. |
| F11 | 2026-08-23 | DMS PRD-001 intake F40 (PRD Agent) | A manifest refusal (`PathNotAllowed` / `StatementNotAllowed` / `SqlNotAnalyzable`) leaves `/v1/contract/ask` as `SESSION`: `CortexOS/api/contract_routes.py:118` `_is_abstain_signal` does not know `refused` and `:148` `_FLAT_BADGE.get(badge_raw, Badge.SESSION)` defaults an unknown badge to a confident one. DMS renders it `L2_VALIDATED`, `abstained=false`. Repro `D:\DMS\scripts\repro_refused_badge.py` exit 0. | Cortex **EPIC-001** (#11, riding alongside) | **Ack + engine ticket.** Fix the class (unknown badge -> ABSTAIN) and the word (`refused` is an abstain signal). Contract impact none (`Badge.ABSTAIN` is on the wire). This epic's acceptance says the stranger "receives a refusal when the question reaches outside that Space"; today a green badge. Serves: PRD-001 (DMS) EPIC-017 (Netie-AI/dms#33) F40. Epic-agent files; the DMS envelope test depends on it. |
| F12 | 2026-08-25 | AirGPT PRD-001 intake F49 (PRD Agent) | Founder: the layer connecting agents across Claude Code, Grok Bot and Cursor lanes should become a Cortex crew agent. Code home `CortexOS/crew` (estate service on :8020) exists; no PRD clause covers it. | none - **PRD amendment, NEEDS-YOU** | **Do not build.** This PRD is the governed engine for consumers; crew is operator-lane orchestration of the founder's own agent estate. Options for the founder: amend this PRD with a crew-agent clause, or keep it as Internal/Agents fleet work (`FLEET.md`, founder-authored) with a Cortex ticket only after that. R-0015 binds any design: attach and distill only - a crew agent never launches or drives Grok Bot or Cursor (founder desktop apps). The mystery full-suite pytest in D:\AirGPT is attributed, not established: `CortexOS/crew/*.py` names neither pytest nor AirGPT. Serves: AirGPT PRD-001 F49. |
