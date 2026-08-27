# DR-0001 - One decision layer; Crew is an app

**Status:** proposed
**Date:** 2026-08-27
**Decision-makers:** founder (accept on merge)
**Repo:** Netie-AI/Netie (estate-wide topology)

---

## Context and Problem Statement

The estate started with Netie as documents (PRD, TAS) and Cortex as the single reasoning/governance engine. As more surfaces appeared - AirGPT, Pointer, Constructor, Netie Control, a planned Cortex-Crew, a serving-engine instinct, a JEPA planner, a mouse-driven Cursor bypass - it started to feel like there were several "decision layers."

That feeling is the same failure `NETIE.md` section 2 was written to prevent: believing we are on a plane we are not on, or growing a second organ in a product that should stay thin.

A 2026-08-27 founder dump also proposed (a) building or wrapping a vLLM/SGLang/MoE serving engine inside Cortex, (b) copying OpenWork + Deep Agents + Grok Bot reconstructed into Crew "10x better," (c) OpenVault intercepting verification messages and passwords, (d) Pointer as a billing bypass into Cursor/Claude Code, (e) merging or duplicating Control and Crew, (f) spawning department agents 24/7 at huge concurrency.

We need one recorded decision so the next session does not re-litigate the topology.

---

## Considered Options

1. **Many brains.** Cortex + Crew + Control + Constructor each grow a DAG runner / agent loop. Fast locally, then undebuggable, then two ledgers.
2. **Crew replaces Cortex.** Make the operator app the engine. DMS, Pointer, AirGPT would have to retarget. Throws away the contract, the manifest, and the one thing that is actually hard.
3. **Do nothing.** Leave Control as a 12-file repo, Crew unnamed, serving-engine talk alive. The constitution already forbids most of this, but unnamed products keep getting proposed as new planes.
4. **One Cortex, Crew as plane-4 operator app, Control folded in, references distilled not copied.** Name it, bound it, refuse the malware-shaped and copyright-shaped ideas in writing.

---

## Decision Outcome

Option 4.

1. **Cortex remains the only plane-3 engine.** No second `dag_runner`. Crew, Control, AirGPT, Pointer, Constructor, FreeIDE are plane 4 or views of plane 4.
2. **Cortex-Crew is the operator factory** (internal first). It hosts Cortex the way DMS hosts Cortex. Netie Control is its board view; the Control *product name* is retired when Crew exists.
3. **AirGPT stays the customer shell.** Multiplayer sessions, when they exist, are Crew underneath and AirGPT in front - not a merge that shows customers the estate board.
4. **Do not write a serving engine.** Host vLLM behind OpenVault if we ever need plane 1. Prefix-cache lives there, not in Cortex.
5. **Do not copy the three trees.** Depend on Deep Agents (MIT). Study OpenWork. Reimplement a licensed-seat router in original code. Do not vendor `grok-bot-0.18-reconstructed`.
6. **OpenVault does not intercept 2FA, SMS, email, or passwords from other apps.** Consented custody only: the human puts the secret in, grants the call, the ledger records it.
7. **Licensed-seat routing is allowed; billing-bypass UI-driving is not.** Crew may dispatch into a Cursor or Claude Code session the operator already pays for, through that product's own login. Pointer is computer-use for the *customer's* desktop under Cortex gates, not a way to steal a meter.
8. **Tickets stay in GitHub Issues.** Plane.so stays rejected. Netie-KB stays the distillation record, not the board.
9. **Concurrency stays the WIP law.** Two epics in flight. Roles are skills. No million-agent standing army.
10. **JEPA / gen-cFSM stay parked** until DMS has a real user (same unlock as PRD-001 EPIC-006).

This decision amends `NETIE.md` section 3 (new is/is-not entries) and section 6 (new refuse rows). `TAS/TAS-CREW.md` and `WP-001` carry the explanation. They do not override this file.

---

## Consequences

Positive:

- Cold sessions can answer "is Crew a second Cortex?" with a file, not a vibe.
- Control vs Crew stops being a product-strategy meeting.
- Legal/safety lines (no reconstructed Grok Bot, no credential interception) are explicit.

Negative:

- Founder must still *create* the Crew repo; this DR does not invent code.
- People who wanted a serving-engine company will feel declined. That is the point.
- Deep Agents as a dependency means Crew inherits LangGraph. That is acceptable *under* Cortex gates and forbidden *as* a second spine.

---

## Confirmation

Until Crew exists, confirmation is documentary:

- `NETIE.md` section 3 lists Cortex-Crew as plane 4 and Control as a view, not a product.
- `NETIE.md` section 6 lists serving-engine, third orchestrator, credential interception, and vendoring Grok Bot reconstructed as declined.
- `TAS/TAS-CREW.md` says PLANNED and "no dag_runner."

When Crew exists, confirmation must resolve to a real test, e.g. `tests/contract/test_crew_cannot_bypass_tool_runner.py` - Crew invoking a denied tool is refused by Cortex, not by a Crew-side allowlist. Track that test name here when the file is real. A decision that names a non-existent enforcer is a wish; this line is therefore **pending a repo**, not green.
