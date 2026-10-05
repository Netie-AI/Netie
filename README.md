# Netie

Netie builds the layer that makes AI accountable enough to run a business on: every answer
carries its evidence, every write goes through a gate, and the system refuses rather than
guesses. We do not sell intelligence. We sell output you can put in front of an auditor.

This repo is the constitution (`NETIE.md`), the portable contracts product repos import
(`netie/`, `scripts/`), and the ecosystem lane that takes permissive open-source projects
and ships them under the Netie brand with our gate on top (`ecosystem/`).

## The estate

| Product | Plane | Job |
|---|---|---|
| OpenVault (FreeRoute, FreeBuild) | 2 | Keys, routing within budget, "may this leave the machine?" |
| Cortex | 3 | Governed execution: evidence, manifest-enforced reads, ledger, abstain over guess |
| DMS / Spaces | 4 | ChatGPT for a company's spreadsheets and databases, every answer attributable |
| AirGPT, Pointer, FreeIDE | 4 | Chat shell, desktop control, coding surface |
| Cortex-Crew, Constructor, Netie Control | 4 | Operator factory, canvas, fleet board |

Every request takes one path: app -> Cortex -> OpenVault -> run -> Cortex -> app. A step
that skips a box is a bug. Planes 0 and 1 (silicon, inference serving) are bought, not built.

## Adopt, do not distill

Reimplementing open-source projects was too slow, so DR-0002 (proposed) switches the lane:

- Permissive upstreams (MIT, Apache-2.0) are forked and rebranded with LICENSE and NOTICE
  untouched. A fork is a pinned upstream commit plus a patch series, never a vendored tree.
- Libraries are depended on. Copyleft, source-available, branding-locked and noncommercial
  projects (n8n, Dify, Open WebUI, NadirClaw, Routerly) are hosted unmodified or blocked.
- A fork keeps no vault and no orchestrator of its own: keys come from OpenVault, tools run
  through Cortex.

The full list, licenses, stages and reasons: `ecosystem/ECOSYSTEM.md` (generated).
Stage 1 means an overlay exists. It does not mean the fork is renamed, gated or sellable.

## Run it

```
make ci                                                   # the one gate, same as GitHub docs-ci
python3 scripts/ecosystem.py validate                     # catalog + license-class gate
python3 scripts/ecosystem.py clone freeide /tmp/freeide   # pinned upstream base
python3 scripts/ecosystem.py apply freeide /tmp/freeide   # replay the Netie overlay
python3 scripts/ecosystem.py drift                        # network: has any upstream license changed?
```

Product repos use the contracts with `uv add git+https://github.com/Netie-AI/Netie.git`
(Cortex is the exception, see `scripts/netie_init.py`).

## Read next

| You want | Read |
|---|---|
| What we are and what we refuse to build | `NETIE.md` |
| Rules for agents working in this repo | `CLAUDE.md` (`AGENTS.md` points to it) |
| What is true right now | `STATUS.md` |
| How far each product is from its analogue | `TAS/ESTATE-GAP.md` |
| Why adopt-and-rebrand | `docs/decisions/DR-0002-adopt-and-rebrand-permissive-upstreams.md` |
| How work becomes tickets | `Internal/Agents/AGENT_SYSTEM.md` |
