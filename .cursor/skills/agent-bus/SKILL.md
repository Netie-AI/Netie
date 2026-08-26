---
name: agent-bus
description: Pass work between the orchestrator and builder or researcher subagents using docs/agent-bus files plus the Task tool.
---

# Agent bus

Use this when the user wants more than one agent, a builder, a researcher, or a place to leave a message for the next run.

## Two channels

1. Live: Cursor `Task` subagents. Orchestrator writes a tight prompt. Builder or researcher returns files and a short result.
2. Durable: `docs/agent-bus/`. Survives a new chat. Next Grok run should read INDEX.md first.

| File | Who writes | What it is |
|---|---|---|
| `docs/agent-bus/INDEX.md` | Orchestrator | What is in flight |
| `docs/agent-bus/to-builder.md` | Orchestrator | Build this. Paths, constraints, done-when. |
| `docs/agent-bus/from-builder.md` | Builder | What shipped, what blocked, exact paths |
| `docs/agent-bus/to-researcher.md` | Orchestrator | Look this up. Do not send mail. |
| `docs/agent-bus/from-researcher.md` | Researcher | Facts with URLs. No invented emails. |

Overwrite the `to-*` file for a new job. Append a dated note on `from-*` so history stays.

## How to staff

- Builder: websites, slides, proposal HTML, scoped code. `subagent_type=generalPurpose` unless a computerUse login is required.
- Researcher: live site facts, mailto, Coming Soon check. No Gmail send.
- Orchestrator: mail, Stripe-once, hire upload, keep-list jobs, STATUS.

Do not spawn a subagent to watch email. Execute, then write the bus, then stop.
