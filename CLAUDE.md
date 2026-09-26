# CLAUDE.md - Netie constitution repo

Read this before any edit. This file does not amend `NETIE.md`. A change to a product boundary is a pull request against `NETIE.md` with a stated reason.

## Rank

1. `NETIE.md` (constitution)
2. `docs/decisions/DR-0001-one-decision-layer.md` (one decision layer)
3. this file
4. `TAS/ESTATE-GAP.md` (measured analogue gaps, not a wish list)

## What this repo is

`Netie-AI/Netie` is the constitution plus portable contracts in `netie/` and `scripts/`. Product applications live in their own repositories. This checkout is not a monorepo of those apps and not a place to drop upstream trees.

`.gitignore` already ignores `OmniRoute/`, `llm-router/`, and `deepagents/`. Leave them ignored.

## Before coding

Read, in order:

1. `NETIE.md`
2. this file
3. `STATUS.md` (60-line cap)
4. `TAS/ESTATE-GAP.md` when the change touches an analogue
5. `docs/ACCESS.md` when the change needs another remote

Then read the module you will edit and its `scripts/test_*.py`.

## Upstream classification

Classify every external project before reading its source into this tree or a product patch.

| Class | License situation | Allowed move |
|---|---|---|
| A | Permissive license that allows the intended use, modification, and redistribution | Depend on it, or port a named behavior in original code. Keep copyright, `LICENSE`, and required attribution. Record the upstream URL and the license in the commit or in `TAS/ESTATE-GAP.md`. |
| B | Source-available, restricted, unclear, or non-compete (example: OpenWork `ee/` is FSL) | Do not copy the tree. Public docs and the allowed interface only. Reimplement behind a Netie contract, or skip. |
| C | Proprietary or no license (example: `b-nnett/grok-bot-0.18-reconstructed` has no SPDX license) | Do not copy source, assets, or trademarks. A study note is not a clone target. |
| D | Incompatible with how that Netie repo is distributed | Do not merge the code. An optional adapter is allowed only when the license allows that adapter. |

`Distill` means: name the capability, keep the smallest legal implementation, put it behind a Netie interface, test it, and credit upstream. It does not mean removing copyright, removing a license, or calling upstream code a Netie original.

## Refuses already recorded

Do not re-open these without a new decision record:

- Vendoring Grok Bot reconstructed. Seat routing stays original code in `scripts/seat_router.py`.
- Vendoring or license-stripping OmniRoute, OpenWork `ee/`, the Deep Agents tree, xyflow, Guacamole, UACC, Palantir, AnythingLLM, Perplexity Computer, n8n, or Activepieces.
- A serving engine inside Cortex. Plane 1 is rented. OpenVault may sit in front of a hosted runtime. It does not become that runtime.
- A second `dag_runner`. Crew, Control, AirGPT, Pointer, and Constructor are plane 4. Cortex is the only plane-3 engine.
- Control as a sibling product. It is the Crew board view.
- Constructor is not n8n and not a second graph runtime. It compiles a canvas to Cortex IR.
- Credential, 2FA, SMS, or password interception. OpenVault is consented custody.
- Pointer or Crew as a billing bypass into another vendor's meter.
- A standing army of agents. WIP law is two epics. `DR-0001` item 9.
- New product names that are not in `NETIE.md` (OpenWiki, Studio, a second gateway). A new product starts as a PRD, not as a cloned repo.

Deep Agents is an allowed dependency (`deepagents` extra, MIT), under Cortex `tool_runner` and `crew_harness_profile`. Depending is not vendoring.

## Product boundaries

| Name | Plane | Is | Is not |
|---|---|---|---|
| OpenVault | 2 | Keys, FreeRoute, leave-machine and deploy gate | An agent loop or a model server |
| Cortex | 3 | Governed execution: manifest, ledger, actions, abstain | A model server or a UI |
| DMS / Spaces | 4 | Evidence-backed answers over granted sources | The engine |
| AirGPT | 4 | Customer shell | A second vault or orchestrator |
| Pointer | 4 | Desktop client. Intents go to Cortex | A second orchestrator |
| Cortex-Crew | 4 | Operator factory. Not created yet | A second Cortex |
| Control | 4 view | Board projection of Crew | Guacamole, Kubernetes, or a decision layer |
| Constructor | 4 | Canvas compiled to Cortex IR | n8n, Activepieces, or `dag_runner` |
| FreeIDE | 4 | Coding surface | The deploy console (that is OpenVault) |

Safe path: app -> Cortex -> OpenVault -> run -> Cortex -> app. A path that skips a box is a bug.

## Contracts in this repo

Product repos import `netie.*` after `uv add git+https://github.com/Netie-AI/Netie.git`, except Cortex, which already owns the package name `netie`. Cortex gets `docs/patches/cortex-netie-path.patch` instead. Callers are listed in `netie/__init__.py` and `scripts/netie_init.py`.

Do not `uv add` this package into Cortex.

## Verify

```
make ci
```

That is `python3 -m compileall -q scripts netie` and `python3 scripts/check_docs.py` (required files, laptop-ASCII, every `scripts/test_*.py`).

Laptop-ASCII in corpus text: `-`, `->`, straight quotes. No em dash, en dash, or curly quotes.

## Completion

A change is done when `make ci` passes, the doc you touched still matches the code, secrets are absent, and any upstream use still has its license and copyright. Do not claim a latency, a score, or production readiness that a test did not measure.
