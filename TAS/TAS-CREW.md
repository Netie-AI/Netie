# TAS-CREW - Cortex-Crew technical architecture

**Plane:** 4 (application - operator factory) · **Repo:** not created · **PLANNED**
**Measured:** 2026-08-27 against public references and the Netie constitution, not against a Crew codebase. There is no `Netie-AI/Cortex-Crew` (or `cortex-crew`) visible to this estate token. Treat every section below as planned unless a later TAS revision is measured against code.

Companion: `White Paper - Why/WP-001-accountable-ai-operating-system.md`, `docs/decisions/DR-0001-one-decision-layer.md`.

---

## 1. What it is

The operator factory: a plane-4 app that *hosts* Cortex for the people who run the estate. It staffs role-agents, projects GitHub Issues onto a live board, loads skills from Netie-KB, keeps ticket runners alive, and (later) offers shared live sessions a team can drop into.

**It is not a second Cortex.** It has no `dag_runner`, no manifest enforcer, no ledger, no leave-machine gate. Those stay in Cortex and OpenVault. Crew sends work in and renders what comes back.

**It is not Netie Control as a sibling product.** Control (reported: 12 files, 1 commit, deliberately thin - estate gate, ledger/manifest/refusal views, board) is the board *view* of Crew. Fold it in on day one. Do not stand up a fourth shell.

**It is not AirGPT.** AirGPT is the customer host shell. Crew is internal first; multiplayer customer sessions are a later AirGPT surface over Crew, not a merge of the two apps.

**First artefact (in Netie, until the Crew repo exists):** wrap (empty wrap and extra unwrapped names refuse), HITL on known writes (`export_pptx` needs `operator_confirm=True`), cap-2 parallel (hard refuse above 2), verify, budget, ledger (refuses skill_body on append), OV gate (`skill` kind refused until a registry row exists), parent-run graph (default child kind is `service`, not `skill`), factory (PRD slice refuses without out-of-scope; WIP 2 epics; close updates the epic task list; `index()` drops prompts), ticket runner (Cortex refusal on the board, ticket stays open, prompt never goes to a child), session view (ids only, no transcript), checkpoint/summarise (ids and counts only; resume cannot recover a prompt), `seat_router.py`. Child jobs that still carry `skill_body` / transcript are refused and do not spend budget. Tools Cortex or OpenVault refuse do not run. This is not Deep Agents and not a second `dag_runner`.

---

## 2. Entry points (planned)

| Surface | Role |
|---|---|
| Crew board (absorb Control) | Factory tickets/epics + run/ledger/refusal cards; no prompts; no dag_runner |
| Session view | one live run: ids, todos, permissions, hand-off id; no transcript |
| Skill browser | Netie-KB promotions + `skills/` directory; pick, demote, improve |
| Runner | pull open GitHub tickets, execute embedded prompts, emit DONE/BLOCKED/NEEDS-YOU/FAILED |
| Seat router | dispatch a ticket into a licensed Cursor or Claude Code session the operator already pays for |

No CLI required for v0. HTTP only if Cortex already exposes the contract Crew needs; do not add a parallel API surface "because Crew wants JSON."

---

## 3. Trust boundaries (planned - fail closed)

| Boundary | Enforced by | Bypass that would make Crew wrong |
|---|---|---|
| What work to do | GitHub Issue with epic parent + embedded prompt | a free-form chat that implements unrouted requests |
| What may be read/written | Cortex manifest + action registry + ledger | Crew calling DuckDB, the filesystem, or the network directly |
| Which key / which model | OpenVault FreeRoute + leave-machine | Crew reading `env.local` or a Grok Bot reconstructed secrets bridge |
| Licensed-seat use | operator's own Cursor / Claude Code login | Pointer-clicking a vendor UI to dodge a meter; cookie/2FA harvest |
| Verification | a different run than the implementer (R-0003) | the runner marking its own ticket done |
| Concurrency | WIP: 2 epics, ticket batching by shared mental model | "spawn millions of agents 24/7" |

If a tool cannot go through Cortex `tool_runner`, Crew does not get that tool.

---

## 4. What we depend on, and what we do not copy

| Need | Closest | Action |
|---|---|---|
| Harness (subagents, summarise, skills, HITL, checkpoints) | `langchain-ai/deepagents` 0.7.9 (MIT, on LangGraph) | **Depend.** Wrap every tool with Cortex gates. Their default is "trust the LLM"; Talon README says it is not a production security boundary. Ours is the opposite. `create_deep_agent(tools=require_wrapped(names, wrap_deepagents_tools(gate, names)))`. Empty wrap refuses. Extra unwrapped names refuse. Known writes need `operator_confirm=True`. Checkpoints and summarise are ids/counts only (`scripts/crew_checkpoint.py`); they do not persist a transcript. |
| Shared session UX, capability MCP into Cursor/Claude Code, org policy | `different-ai/openwork` (OpenCode-powered Cowork-class app) | **Study.** Reuse the *ideas* (session, search_capabilities / execute_capability, Den-like policy). Do not vendor the desktop; AirGPT + Pointer already exist. |
| Route into licensed Cursor / Claude Code / Codex seats | Pattern only | **Reimplement original.** `scripts/seat_router.py` queues a ticket into a seat the operator already pays for. It does not click a vendor UI. Grok Bot / pointer-drive names refuse as `billing-bypass product`. Do not vendor `b-nnett/grok-bot-0.18-reconstructed`. |
| Tickets | GitHub Issues + Projects | Already chosen. Crew projects them. Not Plane.so, not Jira, not Netie-KB. |
| Board / ledger views | `Netie-AI/netie-control` (thin, internal) | Merge the UI into Crew. Retire the product name. |
| Computer use on the *customer's* desktop | Pointer | Keep. Crew may *ask Cortex* to use Pointer. Crew is not a second clicker. |
| Learning / skills | Netie-KB | Findings -> rules/skills. Tickets never live here. |

---

## 5. Factory mapping (already specified, Crew only runs it)

Canonical prompts live in `Internal/Agents/AGENT_SYSTEM.md`. Crew does not author new agent types without a constitution change.

```
  PRD Agent     slice PRD -> epics (irreversibility order)
  Epic Agent    epics -> tickets; completeness re-derived from code
  Ticket Runner one (or a batched) ticket; different run verifies
  Skill miner   customer scolding / defects -> KB finding -> skill or prompt patch
```

Department functions (presales, sales, security, frontend, devops, feedback) are **skill files** loaded when a ticket's role field matches, not always-on processes.

Status line, every hand-off:

```
DONE      <id>  <what became true>  <verified-by>
BLOCKED   <id>  waiting on <owner/repo#N> in <repo>  <one line why>
NEEDS-YOU <id>  <the decision only you can make>
FAILED    <id>  <what broke>  <what was tried>
```

---

## 6. Data stores (planned)

| Store | Where | Rule |
|---|---|---|
| Tickets / epics | GitHub | source of truth |
| Board projection | local cache, rebuildable | never a second backlog |
| Skills | Netie-KB + `skills/` in Crew | generated copies of KB promotions |
| Session transcripts | Crew disk, hashed; optional Cortex ledger append for writes | no silent local-only writes that matter |
| Seat credentials | OpenVault only | Crew holds a handle, not a key |

---

## 7. Shipped vs scaffold

**Shipped:** no Crew product repo. Netie `scripts/crew_*.py` is the portable wrap/verify/budget/ledger/gate the Crew repo must import, not a runtime to pretend is Crew.

**Scaffold that must not be mistaken for shipped:** Netie Control's 12 files, Constructor's 11 files, any Grok Bot agent list sitting in another product. Those are inputs to a migration (prompt-packs -> tickets), not a runtime to transplant.

---

## 8. Verify (when a repo exists)

Until then, this TAS is unverifiable as a *product* and must be reported as such. The wrap tests in `scripts/test_*.py` are the contract.

```
NEEDS-YOU TAS-CREW  create Netie-AI/Cortex-Crew (or fold Control and rename)
                    then stamp with netie_init.py and replace this document
                    with measurements against code
```

When it exists: ruff/mypy/pytest as for any Python surface; plus the Netie wrap tests copied in; plus Deep Agents tools only via `require_wrapped` + `wrap_deepagents_tools`.

---

## 9. Honest summary

Crew is the right *name* for the factory the founder is already running by hand across Cursor and Claude Code. The failure mode is treating that pain as evidence that we need a second engine, a copied desktop, or a serving stack. The TAS is: one thin operator app, Deep Agents as a library, OpenWork as a UX reference, original seat-router, Control folded in, Cortex still the only brain.
