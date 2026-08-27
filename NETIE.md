# Netie

**The one file that does not change.** Everything else in this estate is downstream of
what is written here. If a repo doc contradicts this file, this file wins and the repo
doc is wrong.

Version 1.0 - 2026-08-01. Amend by pull request with a stated reason, never in passing.

---

## 1. What Netie is, in one line

> Netie builds the layer that makes AI **accountable enough to run a business on**:
> every answer carries its evidence, every write goes through a gate, and the system
> refuses rather than guesses.

We are not competing on intelligence. Intelligence is bought. We compete on **whether
you can put the output in front of an auditor.**

---

## 2. The five planes - and which two are ours

This is the most important section in this document, because the most expensive mistake
available to us is believing we are on a plane we are not on.

| # | Plane | What lives there | Ours? |
|---|-------|------------------|-------|
| 0 | **Silicon** | GPUs, CPUs, RAM, datacentre, laptop | **No.** We rent or use what the customer has. |
| 1 | **Inference serving** | vLLM, Ollama, llama.cpp, TensorRT-LLM, Anthropic/OpenAI endpoints. Batching, KV cache, quantization, tokens-per-second. | **No.** We *buy* tokens here. We do not build here. |
| 2 | **Custody and routing** | Where the keys live. Which model answers this call. What is allowed to leave the machine. What may be deployed. | **Yes - OpenVault.** |
| 3 | **Reasoning and governance** | What work to do, in what shape, using what evidence, under what audit, with what refusal. | **Yes - Cortex.** |
| 4 | **Applications** | What a human sees and clicks. | **Yes - DMS/Spaces, AirGPT, Pointer, FreeIDE.** |

### The correction this table exists to make

Cortex is **not** on plane 1. There is no serving runtime in Cortex: no batching, no KV
cache management, no CUDA path, no quantization. Cortex reaches plane 1 through a client
library and a configurable base URL. It calls a model; it does not run one.

So the sentence "give me an LLM or raw compute and I will manage the infra and generate
throughput" describes a **plane 1 company**, and Netie is not one. That is a deliberate
decline, not a gap:

- Plane 1 is a capital fight (GPU access), a kernel-engineering fight (someone else's
  PhD), and a commodity fight (vLLM is free, excellent, and improving weekly).
- Plane 1 has no memory of the customer. It cannot tell you *why* an answer was given,
  who was allowed to see the rows behind it, or whether a human approved the write.
- Plane 2 and 3 are where the accountability lives, and accountability is the thing an
  SME finance director will actually pay for.

**If we ever want plane 1, the correct move is to host vLLM and put OpenVault in front of
it - not to write a serving engine.** That is a packaging decision, not an engineering
programme.

---

## 3. What each product is

Each product gets one sentence for what it is, and one for what it is **not**. The second
sentence is the load-bearing one, because scope creep in this estate has always taken the
form of one product quietly growing a second product's organ.

### OpenVault - custody and routing (plane 2)

**Is:** the single place keys live, the single decision on which model or route serves a
call within budget (FreeRoute), and the single gate that answers "may this leave the
machine, and may this be deployed?"

**Is not:** an agent loop, a password sniffer, or a 2FA interceptor. It never decides
*what work to do*. It answers where, with what key, and whether-allowed. Secrets enter
because a human put them in and granted the call.

**Non-negotiable:** there is exactly one key vault in this company. Any `env.local`
anywhere else is a cache synced from OpenVault, never a second source of truth.

### Cortex - reasoning and governance (plane 3)

**Is:** the governed execution plane. It takes a question or a goal, decides the shape of
the work, assembles the context, runs it, and produces an answer or an action **that
carries its own evidence** - the SQL that ran, the rows behind the number, the manifest
that authorised the read, the ledger entry for the write.

**Is not:** a model server, a vertical product, a key vault, or a UI.

**The differentiator, stated honestly:** orchestration is not the moat. LangGraph
orchestrates better than us and costs nothing. The moat is the four things underneath it:

1. **Manifest-enforced reads** - a session declares what it may touch, and a query that
   cannot be proven to stay inside that declaration is refused rather than run.
2. **Hash-chained ledger** - an append-only record that makes a silent edit detectable.
3. **Actions as the only write path** - agents and humans use the same gate; there is no
   agent bypass.
4. **Abstain over guess** - the system is built to say "I do not know" and is measured on
   how often it is confidently wrong, with the floor set at zero.

Nobody in the open-source agent-framework space is building 1-4 together. That is the
whole thesis. Every hour spent making Cortex a better generic orchestrator is an hour
spent competing with free software; every hour spent on 1-4 is an hour on the moat.

### DMS / Spaces - the first product (plane 4)

**Is:** ChatGPT for a company's spreadsheets and databases, where every answer is
attributable and every Space is an access-scoped sandbox over selected sources.

**Is not:** the engine. It is the proof that the engine works, and the first thing that
gets sold.

### Pointer - computer control (plane 4)

**Is:** a client that lets the engine act on a real desktop - see the screen, click,
type, verify - as a coworker rather than a macro.

**Is not:** a second orchestrator, and not a way to drive another vendor's UI to dodge
their meter. It sends intents to Cortex and executes what comes back, fail-closed.

### AirGPT - the host shell (plane 4)

**Is:** the standalone chat and control surface: settings, pairing, the apps hub, the
place a human lives day to day. The customer-facing shell.

**Is not:** a second key vault, a second orchestrator, or the internal operator board.
It is a thin client of OpenVault for custody and of Cortex for brains.

### Cortex-Crew - the operator factory (plane 4)

**Is:** the internal (later multiplayer) app that hosts Cortex for the people who run
the estate: live sessions, role skills, ticket runners, the board that shows who is
doing what. Netie Control is this board's view, not a sibling product.

**Is not:** a second Cortex. It has no `dag_runner`, no ledger, no leave-machine gate.
It staffs work; Cortex decides what is true and what is allowed. See
`docs/decisions/DR-0001-one-decision-layer.md`.

### Constructor - the consumer canvas (plane 4)

**Is:** a ChatGPT-style box that compiles a canvas graph on Cortex (connector ->
ontology -> insight -> foundry -> app), with ghost-mode dry-runs.

**Is not:** n8n, and not a clone of Cortex `activeflow`. If it grows a second graph
runtime it is deleted.

### FreeIDE - the coding surface (plane 4)

**Is:** a standalone coding app that activates the coding slice of the engine.

**Is not:** the deploy console. That is OpenVault.

> **Naming note (2026-08-01):** OpenVault's code has renamed OpenIDE to **FreeIDE**,
> OpenShip to **FreeBuild**, and OpenFree to **FreeRoute**. Cortex and AirGPT still say
> "OpenIDE" in their copies of the roles contract. The code is right; the docs lag. Use
> the Free* names from here.

---

## 4. The safe path

Every request in this estate follows one shape. Any code path that skips a box is a bug,
not a shortcut.

```
  App (DMS / AirGPT / Pointer / FreeIDE / Crew / Constructor)
      |
      v
  CORTEX  - decides the shape of the work, assembles context, plans
      |
      v
  OPENVAULT  - resolves keys, picks the route within budget,
      |          answers "may this leave the machine?"
      v
  RUN  - inference, query, or action
      |
      v
  CORTEX  - checks the result against its evidence, refuses if it cannot
      |      be supported, writes the ledger entry
      v
  App receives an answer that carries its sources, or an honest abstention
```

**Retrieval or deployment that does not pass OpenVault is unsafe.**
**A write that does not pass an action type and land in the ledger did not happen.**

---

## 5. Methodology - how we decide things

These are not aspirations. They are the rules that have already caught real defects in
this estate, and they are the reason the codebase is worth continuing.

1. **A gate asserts the artifact the customer receives.** Testing the SQL a system
   generated is necessary and insufficient. Test the sentence the customer reads and the
   rows they see. We have certified a broken feature as working by asserting on an
   intermediate artifact; it will happen again if this rule slips.
2. **A skipped test is a failing test.** Suites fail loudly with the cause named. Never
   skip on a missing service, a lock, or a timeout.
3. **The adversary is never the verifier.** Whoever found the bug does not confirm the
   fix. A different agent, against a live stack.
4. **Fix the root-cause class, not the symptom.** If two lists can disagree, merge them.
   Do not special-case the one caller that exposed the disagreement.
5. **A control that refuses legitimate work is a failure, not a win.** After any
   hardening, re-run the full corpus and prove nothing valid became refused.
6. **A silent fallback is a lie.** Any degradation - demo mode, a cached key, a smaller
   model - appears in the output, not only in a log line.
7. **Zero errors in n trials bounds the error rate at 3/n.** Do not say "zero wrong"
   without stating n. Below n=300 we cannot claim under one percent.
8. **Never hand-author a generated artifact.** OpenAPI specs, indexes, agent rule files
   and doc tables are outputs. Edit the source and regenerate.
9. **Verify a gate can fail before trusting it green.** A checker that reports success
   while analysing nothing is worse than no checker, because it buys false confidence.
10. **Laptop-ASCII in all corpus text and CLI output.** No em dash, no curly quotes, no
    arrow glyphs. Use `-`, `->`, `'`, `"`, `...`.

---

## 6. What we deliberately do not build

Writing this down is the point of the document. Every item here was considered and
declined, and each will be proposed again by someone who has not read this.

| Not building | Because |
|---|---|
| An inference server | Plane 1. vLLM is free and better. Host it, do not write it. |
| A third orchestrator | We have `dag_runner`. Adding one in AirGPT, Pointer, or Crew splits the governance spine. |
| A second Cortex under any name | Crew is an app. Control is a view. Constructor is a skin. |
| A second key vault | Custody has exactly one home. |
| Credential / 2FA interception | Malware. Vault is consented custody, not a sniffer. |
| Vendoring Grok Bot reconstructed | Copyright. Reimplement a licensed-seat router in original code. |
| A general-purpose agent framework | LangGraph / Deep Agents exist. Our value is the gate, not the graph. |
| A vertical we cannot sell this year | Verticals are packs on the engine, added when a customer pays for one. |
| Blockchain, tokens, PQC crypto | No customer has asked. Revisit when a regulated client demands it in writing. |

---

## 7. How to read this estate

| You want to know | Read |
|---|---|
| What the company is and what each product does | **this file** |
| Why custody + governance + apps belong together | `White Paper - Why/WP-001-accountable-ai-operating-system.md` |
| How we work: file rules, CI, tickets, roles | `Internal/Workflow/OPERATING_MODEL.md` |
| How PRD -> epic -> ticket runs | `Internal/Agents/AGENT_SYSTEM.md` |
| What is true in a repo right now | that repo's `STATUS.md` |
| The laws of a repo (invariants, boundaries) | that repo's `CLAUDE.md` |
| What exists in a repo and where | that repo's `docs/ACTIVE.md` |
| What was postponed and on what condition | that repo's `PARKING_LOT.md` |

Repositories:

| Repo | Plane | Path | Remote |
|---|---|---|---|
| Cortex | 3 | `D:\Cortex` | `Netie-AI/Cortex` |
| OpenVault | 2 | `D:\OpenVault` | `Netie-AI/OpenVault` |
| DMS | 4 | `D:\DMS` | `Netie-AI/dms` |
| Space | 4 | `D:\Space` | `Netie-AI/Space` |
| AirGPT | 4 | `D:\AirGPT` | `jian-hong/AirGPT` |
| Pointer | 4 | `D:\Pointer` | `Netie-AI/Pointer` |
| Constructor | 4 | `D:\constructor` | `Netie-AI/constructor` |
| Cortex-Crew | 4 | not created | planned; Control folds in; `TAS/TAS-CREW.md` |
| Netie-KB | meta | `D:\Netie-KB` | `Netie-AI/Netie-KB` |
| Netie (this) | meta | `D:\Netie` | `Netie-AI/Netie` |

Two things to correct when convenient: **AirGPT is the only repo not under the `Netie-AI`
org**, and Pointer moved from `jian-hong/NetieClicks` on 2026-08-02 (old remote kept
locally as `old-netieclicks`, not deleted).
