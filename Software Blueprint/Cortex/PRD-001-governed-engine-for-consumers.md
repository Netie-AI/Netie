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
```

AirGPT and Pointer consume manifest enforcement from the same engine work; they do not own DMS epics.

---

## Feedback ledger

| # | Date | Raised in | Feedback | Routed to | Outcome |
|---|------|-----------|----------|-----------|---------|
