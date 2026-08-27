# PRD-002 - Operator factory that hosts Cortex (Cortex-Crew)

**Product:** Cortex-Crew (plane 4)
**Owner:** founder
**Status:** draft - not yet sliced. Blocked behind PRD-001 wave 1.
**Repos in scope:** planned `Netie-AI/Cortex-Crew` (or Control folded in). OpenVault already has `POST /api/crew/gate` on PR #44.
**Created:** 2026-08-27

---

## 1. Press release

### See every agent, load every skill, never skip the gate

**Netie Crew is the board the operator lives on: live sessions, role skills from Netie-KB, ticket runners that pull GitHub Issues, and a licensed-seat dispatch into Cursor or Claude Code you already pay for - all of it calling Cortex for brains and OpenVault for keys.**

Today the founder runs that factory by hand across two IDEs. Threads collide. Context windows fill. Skills learned in one chat die in another. Crew makes the factory visible and gated instead of tribal.

It is not a second Cortex. It does not copy OpenWork's desktop, Deep Agents' name, or Grok Bot's reconstruction. It *depends* on Deep Agents (MIT) under Cortex `tool_runner`, *studies* OpenWork's session UX, and *reimplements* a seat router in original code.

> "I dropped into the same live run as the ops lead, redirected it, and the ledger still showed who approved the write." - *internal operator, not a customer yet*

---

## 2. FAQ

### External

**Is this ChatGPT Teams / Claude Cowork?**
No. Cowork-class session UX is the later shape. The product is a gated operator board over *our* engine.

**Can it spawn infinite subagents?**
It can fan out ticket runners. WIP stays two epics. Every tool hits Cortex. Infinite idle department bots are out of scope.

### Internal

**Q: OpenVault PR #44 says Crew is a Cortex git worktree. This PRD says plane-4 app. Which?**
DR-0001 in Netie says plane-4 app; Control is the board view. OpenVault #44 could not see `Netie-AI/Cortex` and treated crew as a Cortex branch. **Founder call on merge of DR-0001.** Until then this PRD assumes the constitution: Crew is an app, Cortex stays the only `dag_runner`.

**Q: Deep Agents security model is "trust the LLM."**
Yes. That is why every tool is wrapped. If the wrap is missing, Crew is wrong.

---

## 3. Out of scope

- Vendoring `b-nnett/grok-bot-0.18-reconstructed`
- OpenWork `ee/` Den (FSL-1.1-MIT, no competing commercial control plane for two years)
- A second ledger or vault
- Customer-facing AirGPT merge
- Starting before PRD-001 Space boundary holds

---

## 4. Success assertion

> **WHEN** an operator opens Crew, pulls one GitHub ticket with an embedded prompt, and the runner calls a tool Cortex would refuse, **THE SYSTEM SHALL** show the Cortex refusal on the board and leave the ticket open. A Deep Agents subagent completing the same ticket without that wrap is a failing test, not a feature.

---

## 5. Licensed bootstrap (when the repo exists)

```bash
uv init && uv add deepagents
python D:\Netie\scripts\netie_init.py .
# wrap every tool with Cortex tool_runner; OpenVault crew_gate for leave-machine
```

Do not `git clone` OpenWork or Grok Bot into the tree.

---

## 6. Feedback ledger

| # | Date | Raised in | Feedback | Routed to | Outcome |
|---|------|-----------|----------|-----------|---------|
| F1 | 2026-08-27 | founder dump | copy OpenWork+DeepAgents+Grok Bot 10x | out of scope / this PRD | distill, do not copy |
