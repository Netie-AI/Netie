# PRD-001 - Local assistant, vault-first

**Product:** AirGPT
**Owner:** founder
**Status:** draft - not yet sliced
**Repos in scope:** `jian-hong/AirGPT`
**Created:** 2026-08-03

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

---

## 4. Success assertion

> **WHEN** a person opens AirGPT for chat or app control, **THE SYSTEM SHALL** resolve keys and model routes through OpenVault and send governed work to Cortex - with no path that bypasses those gates.

---

## Feedback ledger

| # | Date | Raised in | Feedback | Routed to | Outcome |
|---|------|-----------|----------|-----------|---------|
