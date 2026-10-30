---
name: agent-bus
description: How cloud agents, laptop Cursor, and Claude Code share work. STATUS.md is the bus. Do not add a second bus.
---

# Agent bus

Netie already forbids a sixth file type. The bus is:

| Layer | File | Who writes |
|---|---|---|
| Now / next | `STATUS.md` | Every agent, every session |
| Skill catalog | `.cursor/AGENTS.md` + `.cursor/skills/*/SKILL.md` | Distill after a method works |
| Job log | `docs/side-hustle/truelancer.md` | Hustle lane only |

## How agents see each other

1. Push `STATUS.md` to GitHub. Other cloud runs pull the same repo.
2. Do not open `docs/agent-bus/` on this branch for a parallel channel. If the sales branch already has one, do not copy its live Stripe/queue notes here.
3. Spawn a subagent only for a bounded job (browser login, research). The parent writes the result into `STATUS.md`.

## Claude Code on D:\Netie

Same git remote. Same `.cursor/skills`. After distill, commit here so Cursor cloud picks it up.
