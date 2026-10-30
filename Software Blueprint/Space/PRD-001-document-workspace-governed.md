# PRD-001 - Document workspace (governed)

**Product:** Space (desktop)
**Owner:** founder
**Status:** draft - not yet sliced
**Repos in scope:** `Netie-AI/Space`
**Created:** 2026-08-03

**Naming collision:** "Space" here is the Windows Quick Look / preview desktop app (`NetieSpace.exe`). DMS "Spaces" are ACL-scoped sandboxes over warehouse data - a different product. Do not conflate them in tickets or epics.

---

## 1. Press release

### [HEADLINE TBD] - preview and work on a file without leaving the desktop

**Subheading:** [customer + benefit TBD]

**Problem:** [customer words TBD - opening files for preview and light edit breaks flow]

**Solution:** Space turns the Space key into Quick Look-style preview with PDF/video/image tools, OCR, and optional chat over the file - synced to OpenVault for keys.

**Quote:** [pilot customer TBD]

**Call to action:** [TBD]

---

## 3. Out of scope

- DMS Spaces (governed warehouse sandboxes - see [PRD-001 (DMS)](../DMS/PRD-001-governed-answers-over-your-own-data.md))
- A second orchestrator or key vault
- macOS or Linux builds (current ship target is Windows net8.0 WPF)
- Governed multi-tenant document ACLs (that is DMS engine territory)

---

## 4. Success assertion

> **WHEN** a person selects a supported file in Explorer or on the Desktop and presses Space, **THE SYSTEM SHALL** open an accurate preview within one interaction - and **WHEN** AI chat is invoked, **THE SYSTEM SHALL** resolve keys through OpenVault, not a local secret file.

---

## Feedback ledger

| # | Date | Raised in | Feedback | Routed to | Outcome |
|---|------|-----------|----------|-----------|---------|
