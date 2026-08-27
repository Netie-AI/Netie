# WP-001 - An operating system for AI that a business can be run on

**ID:** WP-001
**Thesis:** custody + governance + applications belong to one company
**Audience:** investors, design partners, technical buyers
**Status:** draft for founder review
**Date:** 2026-08-27
**Companion:** `NETIE.md` (constitution). If this paper and that file disagree, `NETIE.md` wins until a pull request amends it.

This paper answers four questions:

1. Why the world needs Netie.
2. What each product is, separately.
3. What Vault + Cortex + the apps do together that existing tech cannot.
4. How Cortex-Crew, Netie Control, skills, and the agent factory fit without becoming a second brain.

---

## 1. Press-release thesis

Intelligence is bought. Accountability is the product.

Companies with real intention - finance, logistics, operations, legal, support - do not need a smarter chatbot. They need output they can put in front of an auditor: every answer carrying its evidence, every write going through a gate, every refusal recorded instead of guessed.

That is a different market from "tokens per second" and a different market from "an agent framework on GitHub." The first is a capital fight. The second is already free. The gap is the layer in between: who held the key, which model was allowed to see the row, whether the write happened, and whether the system is allowed to say "I do not know."

Netie sells that layer, starting with one buyer-visible product (DMS), not with a cloud, a swarm, or a serving engine.

---

## 2. Why existing tech cannot do this

| What people buy today | What it actually is | What it cannot do |
|---|---|---|
| vLLM, SGLang, Ollama, "edge MoE serving" | Plane 1: tokens out of silicon | No memory of the customer. No idea who was allowed to see the row. |
| OpenRouter / LiteLLM | A model menu with a bill | Routing without a leave-machine gate is just spend. |
| LangGraph, Deep Agents, CrewAI | A graph that calls tools | Orchestration with no manifest, no ledger, no abstain. |
| Claude Code / Cursor / Grok Bot | Excellent single-player agents | A private thread. No auditor. No shared live session. No company ACL. |
| Palantir Foundry / AIP | Ontology + ops for the fortune-500 | Correct ambition, wrong buyer, wrong price, wrong complexity for an SME warehouse. |
| ChatGPT over a spreadsheet | Fluency | Confidently wrong, no Space boundary, no SQL, no rows. |
| AWS / Azure | A cloud for big software | The opposite of "share this internal tool like a Google Doc." |

The expensive mistake is to look at that table and try to become all of it. Netie is the company that makes plane-1 tokens *accountable* and plane-4 products *auditable*. It is not the company that writes a kernel, a serving runtime, or a generic agent framework.

---

## 3. The five planes - one picture

```
  0  SILICON          GPU, laptop, datacentre          NOT OURS. Rent or use the customer's.
  1  INFERENCE        vLLM, Ollama, Anthropic, Groq    NOT OURS. Buy tokens. Host, do not write.
  2  CUSTODY          keys, route, leave-machine,      OURS. OpenVault
                      deploy
  3  GOVERNANCE       what work, what evidence,        OURS. Cortex
                      what refusal, what ledger
  4  APPLICATIONS     what a human (or a crew) sees    OURS. DMS, AirGPT, Pointer,
                                                       Space, FreeIDE, Constructor,
                                                       Cortex-Crew
```

Two corrections this table exists to make, because both keep coming back:

**Cortex is not on plane 1.** There is no batching, no KV-cache manager, no CUDA path, no MoE serving engine in Cortex. "Give me an LLM and I will generate throughput" is a plane-1 company. Netie declined that on purpose. If we ever want local inference, the move is: host vLLM, put OpenVault in front of it. Packaging, not a PhD.

**Cortex-Crew is not a second Cortex.** Crew is a plane-4 operator app that *hosts* Cortex the same way DMS hosts Cortex. It staffs agents, shows the board, loads skills, and keeps the factory running. It does not decide what is true, what may be read, or whether a write happened. Those stay in Cortex.

One decision layer. Many surfaces. That is the whole topology.

---

## 4. What each product is (and is not)

The second sentence is the load-bearing one. Scope creep in this estate always looks like one product growing another product's organ.

### OpenVault - plane 2 - custody and routing

**Is:** the single place keys live; the single decision on which model or route serves a call within budget (FreeRoute, previously OmniRoute / OpenFree); the single gate that answers "may this leave the machine, and may this be deployed?" (FreeBuild, previously OpenShip).

**Is not:** an agent loop, a password sniffer, a 2FA interceptor, or a second Cortex.

**FreeRoute philosophy:** pick the cheapest route that is *allowed*, not the cheapest route that exists. Budget, data-residency, and leave-machine beat raw token price. A free endpoint that exfiltrates a customer sheet is not free.

**FreeBuild philosophy:** deploy small software the way a Google Doc is shared - a gated publish, not an AWS account. This is the honest mapping of "a cloud for small software." It is a later destination of OpenVault, not a new company.

**Credential rule, stated so it cannot be misread:** agents get secrets the human *put in the vault* and *granted for this call*. OpenVault does not intercept SMS, email, authenticator codes, or passwords from other apps. That would be malware. The product is consented custody with a ledger, least privilege, and a human approval when the secret is high-risk.

### Cortex - plane 3 - reasoning and governance

**Is:** the governed execution engine. It takes a question or a goal, decides the shape of the work (often a DAG), assembles context, runs it, and returns an answer or action that *carries its own evidence* - the SQL, the rows, the signed manifest, the ledger entry - or an honest abstention.

**Is not:** a model server, a vertical product, a key vault, a UI, or a generic agent framework.

**The moat is not orchestration.** LangGraph orchestrates better and costs nothing. The moat is four things underneath the graph:

1. Manifest-enforced reads - a session declares what it may touch; a query that cannot be proven to stay inside is refused.
2. Hash-chained ledger - silent edits are detectable.
3. Actions as the only write path - agents and humans use the same gate.
4. Abstain over guess - measured on how often it is confidently wrong, floor at zero.

JEPA, gen-cFSM, "world models that predict consequences" - these are research names for a future planner that would *propose* a DAG Cortex then *governs*. Measured 2026-08-02: JEPA is a name, not an artefact. They stay parked until DMS has a real user. Building a world-model before the Space ACL holds is how eight workstreams die at 80 percent.

### DMS / Spaces - plane 4 - the first thing that gets sold

**Is:** ChatGPT for a company's spreadsheets and databases, every answer attributable, every Space an access-scoped sandbox.

**Is not:** the engine, Palantir, or a general app builder.

Ontology (object types, link types, action types) exists in Cortex and is load-bearing. "Palantir for SMEs" is the *later* shape of DMS after a paying client and after the F-gates hold. It is not the pitch this year.

### AirGPT - plane 4 - the customer host shell

**Is:** the standalone chat and control surface a human lives in: settings, pairing, apps hub, phone-PC sync. The place a client can expect the features.

**Is not:** a second key vault, a second orchestrator, or the internal operator board.

When "every feature inside" is the requirement, AirGPT is the shell and Cortex is the brain. New capability lands in Cortex first, then appears in AirGPT.

### Pointer - plane 4 - hands and eyes

**Is:** computer control. See the screen, click, type, verify. A coworker, not a macro. Holds no keys, trusts nothing on screen, fail-closed. Sends intents to Cortex and executes what comes back.

**Is not:** a second orchestrator, and not a way to steal someone else's metered API.

**Licensed-seat routing vs. stealing tokens.** Using Cursor, Claude Code, or Codex *seats you already pay for*, through their own login and their own client, is a cost choice: one subscription instead of a second metered API. Driving another vendor's UI in order to dodge their billing is not a Netie feature. Pointer exists so *the customer's* desktop can be operated under Cortex gates. Crew may *dispatch work* into a licensed Cursor/Claude Code session the operator owns. It may not harvest cookies, scrape 2FA, or impersonate a billing bypass.

### Netie Space - plane 4 - the Windows front door

**Is:** file/PDF preview plus file-named chats. A finished desktop product.

**Is not:** "DMS Spaces." Those are ACL sandboxes over warehouse data. Same word, different thing. Rename before a third person joins.

### FreeIDE - plane 4 - the coding surface

**Is:** a standalone coding app that activates the coding slice of the engine. Lives with OpenVault.

**Is not:** the deploy console (FreeBuild) and not Cortex.

### Constructor - plane 4 - the consumer canvas

**Is:** a ChatGPT-style box that compiles a canvas graph (connector -> ontology -> insight -> foundry -> app), with ghost-mode dry-runs.

**Is not:** n8n, and not a clone of Cortex `activeflow`. Thin skin on Cortex. If it grows a second DAG runner it is deleted.

### Cortex-Crew - plane 4 - the operator factory (internal, then multiplayer)

**Is:** the software that *hosts* Cortex for the people (and later, the teams) who run the estate. Live sessions. Role agents. Skills directory. Ticket board. 24/7 runners against tickets that already carry their prompt. The thing you look at to see who is doing what, and the thing that spawns the next agent into a hole that is not being filled.

**Is not:** a second Cortex, a second Vault, a serving engine, or a rewrite of Claude Code.

Netie Control (12 files, one commit, deliberately thin) is the *board view* of Crew: estate gate, ledger, manifest, refusal, cards. It is not a sibling product. Fold it in. Two operator UIs is the third-orchestrator bug in costume.

### Netie-KB - meta - the immune system

**Is:** the distillation record. Rules, workflows, findings, attacks. Skills that survive contact with a customer get promoted here so every agent can load them.

**Is not:** the ticket system. Tickets live in GitHub Issues. Mixing them destroyed the thing the KB is good at - that experiment already failed on paper.

---

## 5. The unique combination

Vault without Cortex is a keychain with a router. Cortex without Vault is a brain that cannot be told which key, which model, or whether the tokens may leave the room. Pointer without both is a macro that can click the wrong thing with no record.

Together:

```
  Human or Crew
      |
      v
  APP  (DMS / AirGPT / Pointer / FreeIDE / Crew)
      |
      v
  CORTEX     decides the shape of the work, assembles evidence, plans
      |
      v
  OPENVAULT  resolves the key, picks the allowed route, answers leave-machine
      |
      v
  RUN        inference, query, click, or action
      |
      v
  CORTEX     checks the result against evidence, refuses if unsupported, ledgers
      |
      v
  APP        shows an answer with sources, or an honest abstention
```

That loop is the product. A competitor can copy a chat UI in a week. They cannot copy "the write did not happen unless it passed an action type and landed in the ledger" without becoming us.

Pointer is the proof that governance survives contact with a real desktop. DMS is the proof that governance survives contact with a real warehouse. Crew is the proof that governance survives contact with a swarm of our own agents. None of those proofs is a new plane.

---

## 6. Cortex and Cortex-Crew - the relationship that was getting blurred

Originally Netie only wrote PRDs and technical documents. Then Cortex became the one orchestration / decision layer. Then more "decision layers" started appearing: Crew, Control, Constructor, a serving engine, a JEPA planner, a goal-mode, a mouse-driver into Cursor.

That feeling is correct and the fix is not "add a coordinator of coordinators." The fix is to name the layers and stop.

| Layer | Who | Job |
|---|---|---|
| Constitution | `NETIE.md` + this paper | What we will not build |
| Document factory | PRD Agent -> Epic Agent -> Ticket Runner | How work is sliced and verified |
| Decision engine | **Cortex** (exactly one) | What is true, what is allowed, what is refused |
| Custody | **OpenVault** (exactly one) | Keys, route, leave-machine, deploy |
| Operator factory | **Cortex-Crew** (exactly one) | Who is running, which skill, which ticket, live board |
| Customer shells | AirGPT, DMS, Pointer, Space, FreeIDE, Constructor | What a buyer sees |

Crew *executes* the document factory against Cortex. It does not replace Cortex's `dag_runner`. If Crew grows its own ungoverned graph, Crew is wrong.

### Distill, do not copy

Three public repos are the right *references*. None of them is the product.

| Need | Closest public repo | What we take | What we do not take |
|---|---|---|---|
| Shared live session, skills/MCP reused across Cursor and Claude Code, team control plane | [different-ai/openwork](https://github.com/different-ai/openwork) (Claude Cowork-class desktop; OpenCode underneath) | Session UX, capability search/execute, "one MCP into the tools you already use," org policy | The whole desktop. We already have AirGPT + Pointer. |
| Long-horizon harness: subagents, filesystem, summarisation, skills, HITL, checkpoints | [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) (MIT; sits on LangGraph) | Depend as a library when Crew needs a harness. Wrap every tool with Cortex `tool_runner` + ledger | A fork advertised as "10x better." Their security model is "trust the LLM." Ours is the opposite. |
| Route work into licensed Cursor / Claude Code / Codex seats you already pay for | Pattern only. `b-nnett/grok-bot-0.18-reconstructed` is an unofficial reconstruction of Anysphere's Grok Bot | The *idea*: inference router across seats you own, local usage tracking, optional local sandbox | **Do not vendor, copy, or "reconstruct" that tree into Crew.** It is a copyright and provenance problem. Reimplement the capability list in original code. |

"Copy everything and make it 10x more efficient" is how you spend a year competing with MIT-licensed software and a reconstructed proprietary app. The 10x is the gate: Crew's tools fail closed, every spawn is a ticket, every ticket names its epic, every epic names its PRD, every write hits the ledger.

### Control vs Crew vs AirGPT

They felt similar because they *are* similar until you name the audience.

- **AirGPT** - customer. Chat, apps hub, pairing.
- **Crew** - operator (internal now; multiplayer team later). Sessions, roles, skills, 24/7 runners.
- **Control** - a view. Cards, ledger, refusals, "who is idle." Fold into Crew as the board. Do not ship a fourth shell.

Plane.so was tried as the board and judged useless for this estate. GitHub Issues remain the ticket system. Crew *projects* issues onto a live board. It does not become a second Jira.

---

## 7. The factory that staffs the company

This is the part that sounds like "spawn a million agents." The version that works is smaller and meaner.

```
  Founder writes NETIE.md, WP, PRD, TAS     (strategy; agents do not author this)
      |
      v
  PRD Agent     slices one PRD into epics by irreversibility
                (foundation -> boundary -> capability -> surface -> demo)
      |
      v
  Epic Agent    turns one epic into tickets; after each batch re-derives
                completeness from the code, not from checkboxes
      |
      v
  Ticket Runner executes the embedded prompt; a DIFFERENT run verifies
      |
      v
  Feedback      distill -> Netie-KB rule or skill -> every agent can load it
```

**Roles are skills, not processes.** Sales, presales, security, frontend, devops, customer-feedback are *skill files* plus a ticket, not 50 idle bots. Crew loads the skill when the ticket's role field matches. A standing army of department agents is how you get eight workstreams at 80 percent and none at 100.

**WIP law, unchanged:** at most two epics in flight, at least one human-inspectable. Parallelism is for tickets inside an epic that do not share a mental model, not for "millions of agents until we are the top ecosystem."

**The verification chain the founder asked for already exists on paper:**

- Ticket Agent (runner) does the work.
- A different run verifies the customer-visible assertion.
- Epic Agent measures whether the epic's acceptance still holds.
- PRD Agent measures how much of the PRD is true, and whether new work would have consequences the PRD did not budget.

Clear communication across layers is allowed. Silent scope-widening is not. Information is visible; *acting* on information that changes a PRD stops for the founder.

**Customer scolding becomes a skill.** Outreach that gets roasted is not a vibe to remember in one agent's context. It is a finding in Netie-KB, then either a tighter system prompt, a tone skill, or a refusal ("do not send this class of message"). One layer, every agent can load, wrong skills get demoted by evidence.

**Grok Bot agents move as prompt-packs and tickets, not as a transplanted runtime.** The 24/7 loop is: Crew ticket runner, OpenVault-resolved keys, prefer the Cursor seat for code (Grok 4.6 high, not fast, for hard fan-out; Composer for routine), Claude Code seat where that login is the right tool. Official sessions. Not a mouse pasting into a chat to dodge a meter.

**Context-window and "new chat" decisions belong in the harness** (Deep Agents already summarises and offloads tool output to disk). Crew must notice a full window, compact, or hand off - not blindly open a new chat and lose the thread. That is a Crew feature, not a Cortex feature.

---

## 8. Three later destinations - not three new companies

These are real markets. They map onto products we already named. They are not year-one builds.

### A cloud for small software (Pete Koomen)

Purpose-built tools for one team, as easy to share as a Doc, without AWS complexity.

**Maps to:** FreeBuild (OpenVault deploy gate) + AirGPT apps hub + Constructor for the canvas + Cortex for the governed runtime.

**Does not map to:** writing Azure. Auth, permissions, and "nontechnical people sharing arbitrary code" are exactly why FreeBuild is a *gate*, not a public `npm publish`.

### Multiplayer AI (Aaron Epstein)

Shared live agent sessions a team can drop into, redirect, and hand off.

**Maps to:** Cortex-Crew sessions (OpenWork's good idea) surfaced later in AirGPT so a customer team, not just Netie operators, can crowd around one run.

**Does not map to:** a thousand private Cursor chats with a read-only link. That is the problem statement, not the architecture.

### Self-maintaining APIs (Harsha Gaddipati)

When Stripe (or anyone) ships a breaking change, an agent opens the PR in the customer's repo.

**Maps to:** a vertical *pack* on Cortex, run by Crew, after DMS has a user. Dependabot-shaped, ledgered, human-approved merges.

**Does not map to:** a new startup, and not a reason to delay the Space ACL.

Prefix-caching and "orchestrate APIs efficiently" are plane-1 concerns. If we host vLLM later, prefix-cache lives in that host. Cortex already has `/api/goals`. Goal-mode is "Crew runs the factory." It is not a new engine.

---

## 9. How this is sold

**Who buys:** SME operators who already run on Excel and cannot afford to be confidently wrong. First beachhead: Malaysian logistics / distribution warehouses (PRD-001). Not "every knowledge worker."

**What they buy first:** DMS. One Space, one warehouse, answers with rows and SQL, abstention when the data cannot support it. They do not buy Cortex, Crew, JEPA, or a cloud.

**Presales motion, two minutes:**

1. Load *their* sheet, not our demo.
2. Ask a question inside a Space that is allowed to see it - show the rows.
3. Ask a question that requires a table outside the Space - show the refusal.
4. Show the ledger entry. Stop talking.

If step 3 cannot be demoed, we do not have a product. As of 2026-08-02 it cannot: Space ACL is decorative. That is why PRD-001 exists, and why this paper does not author a second first-product.

**Later SKUs, in order, only after a user exists:**

1. Pointer on the ops desktop (computer-use under the same gates).
2. AirGPT as the daily shell.
3. Crew sessions for the customer's own team (multiplayer).
4. FreeBuild for the small tools Constructor generated (small-software cloud).
5. API-update pack (self-maintaining APIs).

**Who talks to whom in a deal:** one human closer, backed by Crew skills (presales research, security questionnaire, implementation). Not a swarm on the customer's Slack.

---

## 10. What we refuse (so the argument can end)

| Not building | Because |
|---|---|
| An inference / MoE serving engine | Plane 1. Host vLLM, do not write it. |
| A second Cortex under any name | Crew, Control, AirGPT, Pointer, Constructor do not get a `dag_runner`. |
| A generic agent framework | Depend on Deep Agents / LangGraph. Compete on the gate. |
| Vendoring Grok Bot reconstructed | Copyright. Reimplement the seat-router idea. |
| Credential / 2FA interception | Malware. Vault is consented custody. |
| UI-driving a vendor to dodge their meter | Licensed-seat routing only, through their login. |
| Palantir-parity marketing | After a paying client and hardened F-gates. |
| Million idle department agents | Roles are skills. WIP is two epics. |
| WASM as the isolation story | Zero production callers today. Containers if a customer needs untrusted code. |
| Blockchain, tokens, PQC | No customer has asked in writing. |

---

## 11. Internal FAQ - does the founder's latest map hold?

**Q: Decision engine first, not inference. Then a Claude/Grok-class coordinator. Then JEPA to predict consequences. Then Crew copying three repos. Then Vault as login interceptor plus OpenRouter plus OpenShip. Then DMS as Palantir. Then a small-software cloud, multiplayer AI, and API agents. Then a central chat that drives Cursor with the mouse. Then Control as the visual board. Then a skills layer. Then 24/7.**

**A:** The spine is right. The organs were growing into each other. Collapsed:

- Decision engine = Cortex. Keep. Do not put serving inside it.
- Coordinator = Cortex's existing DAG/goal path + Crew as the *staffing* UI. Do not add LangGraph as a second spine; Deep Agents may sit *under* Crew's runners, gated by Cortex.
- JEPA / gen-cFSM = parked. Name, not artefact. Unlock after one real user.
- Crew = plane-4 operator app. Distill OpenWork (sessions) + Deep Agents (harness) + the *idea* of a licensed-seat router. Do not copy the three trees.
- Vault = keys, FreeRoute, leave-machine, FreeBuild. Not an interceptor.
- DMS = first sale. Ontology later.
- Cloud / multiplayer / API-agents = later destinations of FreeBuild, Crew, and a Cortex pack.
- Central chat driving Cursor = Crew dispatch into a licensed session, or Pointer for *customer* desktops. Not a billing bypass.
- Control = Crew's board. Merge.
- Skills = Netie-KB. Keep.
- 24/7 = ticket runner with a concurrency cap, not a million agents.

**Q: Can Crew and Control be one app?**
Yes. They should. AirGPT stays separate because it is the customer shell.

**Q: Can we sell Cortex as an API that "clients can expect every feature inside"?**
They can expect every *governed* feature. AirGPT is the client. Cortex is the API. "Every feature" that skips the manifest is a bug.

**Q: Is the quality good enough to sell?**
Not proven. Corpus `wrong=0` on 376 with only 47 human-verified items bounds the error rate at 6.4 percent, not under 1 percent. The last five live defects were all missed by the corpus. PRD-001 buys a number we can defend. This paper does not.

---

## 12. Build order

Appetite is two weeks. A slice that misses is cancelled, not extended. This is the only plan that does not reopen the eight-workstreams failure.

### Now - one buyer-visible slice (already specified)

PRD-001 wave 1, in DMS + Cortex:

1. Eval gate can fail (Cortex).
2. Space boundary actually holds (DMS) - the demo a stranger can see.

Nothing in this paper, including Crew, jumps that queue.

### Next - operator factory, thin

3. Constitution amendment: name Crew as plane 4, fold Control, add Constructor (this PR).
4. Cortex-Crew v0 in its own repo, stamped with `netie_init.py`: GitHub Issues projected on a board, PRD/Epic/Ticket agents as Crew roles, Deep Agents as an optional harness *behind* Cortex `tool_runner`.
5. Skills directory: Netie-KB findings promote into `skills/` Crew can load. One outreach-tone skill as the proof.
6. Licensed-seat router (original code): Cursor session and Claude Code login the operator already has, usage logged, OpenVault holds the tokens. Pointer is not the primary path into those UIs.

### Later - only with a user

7. JEPA / gen-cFSM as a *proposer* of DAGs, Cortex still governs.
8. Hosted vLLM behind OpenVault (packaging).
9. Multiplayer sessions in AirGPT (Crew underneath).
10. FreeBuild as the small-software share path.
11. API-update pack.
12. Ontology / lineage marketing after F-gates and a paying client.
13. Department skill pack (sales, security, frontend, devops, feedback) loaded on demand.

### Explicitly not a ticket this year

Writing SGLang. Copying Grok Bot. Intercepting 2FA. A third orchestrator. Plane.so. A million agents.

---

## 13. How to read this estate from a cold start

| You want | Read |
|---|---|
| What the company is | `NETIE.md` |
| Why the combination exists | this file |
| How work is sliced | `Internal/Agents/AGENT_SYSTEM.md` |
| What DMS will ship | `Software Blueprint/DMS/PRD-001-*.md` |
| How Cortex is actually built | `TAS/TAS-CORTEX.md` |
| How Crew is supposed to be built | `TAS/TAS-CREW.md` (planned; no repo yet) |
| How close each product is to its analogue | `TAS/ESTATE-GAP.md` (measured 2026-08-27) |
| What was decided about Crew vs Cortex | `docs/decisions/DR-0001-*.md` |
