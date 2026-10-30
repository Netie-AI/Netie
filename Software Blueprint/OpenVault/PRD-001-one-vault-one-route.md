# PRD-001 - One vault, one route

**Product:** OpenVault
**Owner:** founder
**Status:** draft - not yet sliced
**Repos in scope:** `Netie-AI/OpenVault`
**Created:** 2026-08-03

---

## 1. Press release

### [HEADLINE TBD] - one place for keys, routes, and leave-machine decisions

**Subheading:** [customer + benefit TBD]

**Problem:** [customer words TBD - keys scattered across env files, no single gate on what may leave the machine]

**Solution:** OpenVault holds keys, picks the route within budget (FreeRoute), and answers whether a call may leave the machine or be deployed.

**Quote:** [pilot customer TBD]

**Call to action:** [TBD]

---

## 3. Out of scope

- An agent loop or second orchestrator (OpenVault decides where and whether-allowed, not what work to do)
- A second key vault anywhere in the estate (`env.local` elsewhere is a cache synced from OpenVault, never a source of truth)
- Inference serving (plane 1) - OpenVault routes to it, does not run models
- Production multi-tenant hosting before a paying client demands it in writing

---

## 4. Success assertion

> **WHEN** an application needs a model key or a leave-machine decision, **THE SYSTEM SHALL** resolve it only through OpenVault - and **WHEN** the vault denies egress, **THE SYSTEM SHALL** refuse without a silent fallback.

---

## Feedback ledger

| # | Date | Raised in | Feedback | Routed to | Outcome |
|---|------|-----------|----------|-----------|---------|
