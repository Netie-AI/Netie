# WP-001 - Accountable AI for business

**Audience:** investors, design partners, technical buyers
**Owner:** founder
**Created:** 2026-08-03
**Source:** [NETIE.md](../NETIE.md) section 1

---

## Why the world needs this

General AI is cheap and getting cheaper. Intelligence is not the bottleneck for a finance director or operations lead - **auditability is**. They need to put an answer in front of an auditor and defend it: which rows, which query, who was allowed to see them, and whether a write was approved.

Today's assistants optimize for fluency. They will answer confidently from a spreadsheet they half-read. There is no reliable way to tell a correct answer from a fluent one.

## Why existing tech cannot do it alone

| Layer | What it gives you | What it cannot give you |
|---|---|---|
| Plane 1 (inference) | tokens per second | memory of the customer, row-level authorization, tamper-evident writes |
| Generic orchestrators (LangGraph, etc.) | workflow graphs | manifest-enforced reads, one ledger, actions as the only write path, measured abstention |
| A chat UI on top of RAG | fast demos | proof that a session stayed inside what was granted |

Nobody in the open-source agent space is building manifest enforcement, a hash-chained ledger, governed actions, and abstain-over-guess **together**. That combination is the thesis.

## What Netie builds

Netie owns planes 2-4:

- **OpenVault (plane 2)** - one vault, one route, one leave-machine gate
- **Cortex (plane 3)** - governed execution; evidence rides with every answer
- **Applications (plane 4)** - DMS/Spaces, AirGPT, Pointer, FreeIDE prove the stack

The safe path is fixed: App -> Cortex -> OpenVault -> Run -> Cortex (evidence check) -> App. Retrieval or deployment that skips OpenVault is unsafe. A write that does not pass an action type and land in the ledger did not happen.

## What we refuse to claim

We do not compete on intelligence. We compete on whether you can run the business on the output. Every external claim must trace to a passing gate - not a demo branch, not a hand-written regex path, not a press-release quote from a customer who does not exist yet.
