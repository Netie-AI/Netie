# Netie

Netie builds the layer that makes AI accountable enough to run a business on: every answer carries its evidence, every write goes through a gate, and the system refuses rather than guesses.

This repository (`Netie-AI/Netie`) is the constitution and the portable contracts. Product applications live in their own repositories. This repo does not vendor those applications or other people's trees.

If a document in this repo disagrees with `NETIE.md`, `NETIE.md` wins.

## Planes

| Plane | What | Netie? |
|---|---|---|
| 0 Silicon | GPUs, CPUs, machines | No. Rent or use what the customer has. |
| 1 Inference | vLLM, Ollama, hosted model APIs | No. Buy tokens. Do not write a serving engine. |
| 2 Custody and routing | Keys, which model, may this leave the machine | Yes. OpenVault. |
| 3 Reasoning and governance | Shape of the work, evidence, audit, refusal | Yes. Cortex. |
| 4 Applications | What a human sees | Yes. DMS, AirGPT, Pointer, FreeIDE, Crew, Constructor. |

## Safe path

```
App (DMS / AirGPT / Pointer / FreeIDE / Crew / Constructor)
    |
    v
Cortex        decides the work, assembles context, plans
    |
    v
OpenVault     keys, route, leave-machine and deploy gate
    |
    v
Run           inference, query, or action
    |
    v
Cortex        evidence check, ledger, or an honest abstain
    |
    v
App           answer with sources, or a refusal
```

## Products

Each product has one job. The second sentence is the boundary.

| Product | Is | Is not |
|---|---|---|
| OpenVault | The only key vault, FreeRoute, and the leave-machine gate | An agent loop or a model server |
| Cortex | Governed execution with manifest, ledger, actions, and abstain | A model server, a vault, or a UI |
| DMS / Spaces | Answers over a company's own data, scoped per Space | The engine |
| AirGPT | The customer chat and apps shell | A second vault or orchestrator |
| Pointer | Desktop see / click / type, fail-closed, intents to Cortex | A second orchestrator or a billing bypass |
| Cortex-Crew | Operator factory (planned) | A second Cortex. Control is this board's view |
| Constructor | A canvas that compiles to Cortex IR | n8n, or a second graph runtime |
| FreeIDE | Coding surface on the engine | The deploy console |

Sibling remotes and what is actually measured: `TAS/ESTATE-GAP.md` and `docs/ACCESS.md`. Scores there are analogue distance, not a launch claim.

## This package

```
uv add git+https://github.com/Netie-AI/Netie.git
```

Then, for example:

```
from netie.crew import bind_deep_agent, crew_harness_profile, TokenBudget
from netie.cortex import run_question
from netie.dms import answer_or_abstain
```

The import list is `netie/__init__.py`. Optional extra: `crew` pulls `deepagents` (MIT) as a dependency. Do not vendor that tree.

Do not `uv add` this package into Cortex. Cortex already owns the Python package name `netie`. Use `docs/patches/cortex-netie-path.patch`.

## Upstream software

Classify the license before any reuse:

- **A. Compatible open source.** Depend, or port with copyright, license, and attribution kept. Record the upstream.
- **B. Restricted or unclear.** Do not copy. Use an allowed interface or reimplement.
- **C. Proprietary or no license.** Do not copy source, assets, or trademarks.
- **D. Incompatible with that repo's distribution.** Do not merge it.

Netie does not remove upstream attribution or call upstream code a Netie original. `TAS/ESTATE-GAP.md` is the capability matrix. Do not add a second one.

Already refused, with the reason in `NETIE.md` and `DR-0001`: vendoring Grok Bot reconstructed, license-stripping OmniRoute / OpenWork `ee/` / Deep Agents / xyflow / Guacamole / UACC, a serving engine, a second orchestrator, and credential interception.

## Develop

```
make ci
```

Same command as GitHub `docs-ci`: compile `scripts` and `netie`, then required docs, laptop-ASCII, and `scripts/test_*.py`.

Agent instructions: `AGENTS.md` then `CLAUDE.md`.

## Layout

| Path | Role |
|---|---|
| `NETIE.md` | Constitution |
| `CLAUDE.md` | Agent law for this repo |
| `STATUS.md` | What is true now (60-line cap) |
| `netie/` | Import surface |
| `scripts/` | Contract implementations and tests |
| `TAS/` | Per-product technical notes and the estate gap |
| `docs/decisions/` | Decision records |
| `docs/patches/` | Patches for sibling repos (push is a separate grant) |
| `Software Blueprint/` | PRDs |
| `Internal/` | How the estate files work |

## License

Original code in this repository is MIT (`pyproject.toml`). Third-party components keep their own licenses. This repo does not ship vendored upstream trees.

## Contributing

Read `AGENTS.md`. Tickets are GitHub Issues. At most two epics in flight. A feature request is routed through the PRD before it is built (`Internal/Prompts/ONESHOT_NEW_REPO.md`).
