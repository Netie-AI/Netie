# TAS-ESTATE-GAP - measured distance to named analogues

**Measured:** 2026-08-27. Scores are 0-10 against the analogue's *buyer-visible job*, not against a vibe.
**This cloud environment contains only `Netie-AI/Netie`.** Cortex, DMS, AirGPT, Pointer, Space, Control, Netie-KB were `repository not found` to this token. Those rows are TAS-dated or UNVERIFIABLE, not live HEAD.

**License law (non-negotiable):** we depend, port with attribution, or reimplement. We do not vendor a tree, strip the license, or slap a Netie logo on someone else's product. `b-nnett/grok-bot-0.18-reconstructed` has **no SPDX license** and reconstructs Anysphere's Grok Bot. It is a study note, not a clone target.

Score key: 0 = no artefact. 3 = real code, cannot sell. 6 = stranger can use the analogue's core job. 8 = analogue-class. 10 = analogue plus our gate.

---

## 0. How Cortex works today (JEPA and gen-cFSM are not in the path)

From `TAS/TAS-CORTEX.md` (measured 2026-08-02 by building the app, not by reading a slide):

```
  question
      |
      v
  race_router.auto_route     cosine >= 0.80 against a family centroid
                             AND a stored winner with >= 3 runs
                             else probe top 3, score predicates-over-judge
      |
      +-- workflow_recognizer.recognize  (template pick)
      |
      v
  COLD_START_ORDER = minimal | sequential | dag
      |
      +-- DMS answers today: keyword cascade (~240 lines of regex)
      |   C7 generated-SQL is OFF (17 confidently wrong vs floor 0)
      |
      v
  dag_runner / tool_runner / answer envelope
```

**JEPA** is a sha256 feature-hash into 64 buckets (`action_value.py`). Not a joint-embedding world model. Not on the request path as a consequence predictor.

**gen-cFSM** has no HTTP entry. `auto_route` never passes it as a candidate.

**OSR** (`osr.route`) is classify-only on `POST /api/engine/osr`.

So Cortex today is: a FastAPI engine with a live auto-router, a DAG runner, a tool allowlist that is bypassed on some paths, a keyword warehouse Q&A, and four governance organs (manifest, ledger, actions, abstain) of which several are decorative on the product path. It is not a serving engine and not Claude.

---

## 1. Scorecard

| Product | Closest analogue | License | Score | Why that number | Move |
|---|---|---|---|---|---|
| **Cortex** vs Claude / Claude Code | `langchain-ai/deepagents` (harness) + our gates | MIT | **2 / 10** as a coding agent. **4 / 10** as governed Q&A | Tool loop and `dag_runner` exist. One invocable write action (`export_pptx`). Web tools can skip `tool_runner`. RBAC absent on the modules that execute. Keyword cascade, not a Claude-class prompt+tool runtime. Internal prompts live in `AGENT_SYSTEM.md`, not in a shipped harness. | Depend Deep Agents *under* `tool_runner`. Do not fork Claude. Do not claim stronger. |
| **OpenVault FreeRoute** vs OmniRoute | `diegosouzapw/OmniRoute` MIT (`2acbfc6`) | MIT | **4 / 10** as a gateway. **6 / 10** as a vault+gate | Live OmniRoute `ROUTING_STRATEGY_VALUES`: **19** user-facing (+ internal `quota-share`). FreeRoute still **8** (priority, weighted, fill-first, round-robin, p2c, random, least-used, cost-optimized). Missing: context-relay, reset-aware, reset-window, headroom, strict-random, auto, lkgp, context-optimized, cache-optimized, fusion, pipeline. `combo.ts` still not extractable. OpenVault **main CI green** (merge #43, 2026-08-25). | Keep porting *algorithms* into Python. Do not vendor OmniRoute. |
| **FreeRoute** vs NVIDIA LLM Router | `NVIDIA-AI-Blueprints/llm-router` HEAD `07b0fb6` | Apache-2.0 | **2 / 10** | README: **deprecated** for NVIDIA NeMo Switchyard. v1 was BERT+Triton proxy; v2 experimental is Qwen 1.7B or CLIP+NN, classify-only. FreeRoute still classifies *cost/quota/health* and picks a key. Different job. | Optional later: host Switchyard *behind* OpenVault leave-machine. Do not rewrite Triton. Do not vendor the blueprint. |
| **OpenVault FreeBuild** vs Vercel | `ship/hosts/cloudflare_pages.py` vs Vercel | n/a (Vercel closed) | **2 / 10** | `docs/SHIPPING_MODEL.md` is honest: user CPU builds, user cloud hosts, OpenVault is the button. Cloudflare Pages adapter is real (wrangler). STATUS: four hosts declared, **no live box has run it (HT1)**. Engine hosting step still simulated unless a remote FreeBuild is configured. This will never *be* Vercel; it is a control plane for the user's own account. | Finish HT1 on one real Pages deploy. Then Netlify/Coolify. Not ECS first. |
| **DMS** vs "ChatGPT for the warehouse" | AnythingLLM / evidence-QA, later Palantir | mixed | **3 / 10** | TAS-DMS 2026-08-02: 166 passed, Space ACL decorative, no auth, two warehouses, 2 of 5 sheet classes ingest. Cannot demo two customers in one room. Do not clone Palantir. Do not clone AnythingLLM over the envelope. | PRD-001 wave 1. No second repo. |
| **Cortex-Crew** vs Deep Agents | `langchain-ai/deepagents` 0.7.9 | MIT | **0 / 10** as a product. **2 / 10** as a portable wrap | No `Netie-AI/Cortex-Crew` remote. Netie `scripts/crew_*.py` now: wrap, cap-2, parent-run graph, verify, budget, ledger, OV gate. Deep Agents `create_deep_agent(tools=[...])` is the depend path. Talon README: not a production security boundary. | Create repo. `uv add deepagents`. Wrap every tool. |
| **Cortex-Crew** vs OpenWork | `different-ai/openwork` | MIT core; `ee/` is FSL-1.1-MIT (no competing Den for 2 years) | **0 / 10** | Session UX + capability MCP are the take. Do not vendor the desktop (AirGPT+Pointer exist). Do not ship `ee/` as a competing control plane. | Study; reimplement session board in Crew. |
| **Cortex-Crew** vs Grok Bot reconstructed | `b-nnett/grok-bot-0.18-reconstructed` | **none** | **0 / 10** and **do not clone** | Seat-router *idea* only (Cursor / Claude Code / Codex logins you already pay for). | Original code. |
| **AirGPT** vs ChatGPT | Open WebUI / LibreChat | MIT | **UNVERIFIABLE** HEAD. Corpus exists | Repo 404. Portable table-chunk corpus in `scripts/airgpt_chunk.py` (repeated headers, ragged rows, labels). Chunker in `rag/ingest.py` still unread. | Add AirGPT remote. Run corpus against `rag/`. |
| **Netie Control** vs Apache Guacamole | `apache/guacamole-client` | Apache-2.0 | **1 / 10** | Guacamole is a remote-desktop gateway. Control is a 12-file operator board. Wrong analogue for RDP; right *feeling* is "watch the session." Closer licensed boards: GitHub Projects (already chosen for tickets) + Langfuse (OSS traces). | Fold Control into Crew. Do not clone Guacamole. |
| **Pointer** vs Perplexity Computer / UACC | `uacc` on PyPI; `e2b-dev/open-computer-use` Apache-2.0 | MIT / Apache | **UNVERIFIABLE** HEAD. Fail-closed click spec exists | Tray still not cloned. `scripts/pointer_click.py` refuses unlabeled / no Cortex intent and does not touch `os.environ`. | Measure Pointer HEAD. MCP-wrap UACC behind `tool_runner` if the 68 tools are the gap. |
| **Netie Space** vs Peek / macOS Preview | Windows: PowerToys Peek. macOS: Quick Look + `altic-dev/PeekX` (MIT) | mixed | **6 / 10** as a preview app. **2 / 10** as governed | TAS-SPACE: most finished *product* in the estate (installer, PDF/OCR/video/chat). Leave-machine ungated. No tests. Name collision with DMS Spaces. Do not clone PeekX (macOS extension) into a C# WinExe. | Add CI + leave-machine gate. Rename one "Space". |
| **Constructor** vs React Flow | `xyflow/xyflow` (`@xyflow/react`) | MIT | **2 / 10** as a node editor. **4 / 10** as a Cortex IR compiler | Live clone: 11 files, custom canvas. This VM: `node --test tests/compiler.test.cjs` **3 passed**. Default branch **pages.yml green**; **no unit-test workflow** on HEAD. Push 403. See `TAS/TAS-CONSTRUCTOR.md`. | Land the test branch when write access exists. `npm i @xyflow/react` only if the canvas must feel like React Flow. |

---

## 2. What is already copied (honest, from OpenVault's own DRs)

OpenVault `docs/decisions/DR-0003-openship-app-plan.md` already ran the "steal OmniRoute" experiment and recorded the result. Do not re-run it as a logo swap.

| Taken | How | Still ours |
|---|---|---|
| OmniRoute Electron process-tree kill, preload whitelist *shape*, CSP/single-instance ideas | Port / rewrite to `apps/shell` | Different channels, uv+npm spawn, no `login:*` |
| OmniRoute `proxy.ts` + authz pipeline *shape* | Port to `apps/web/src/server/authz/` | Loopback+CSRF policy, our LOCAL_ONLY prefixes |
| 8 of 18 routing strategies + circuit breaker | Port to `openvault/route/*.py` | Python, Redis-or-memory, no `combo.ts` |
| FreeBuild UI primitives + stack-detection *tables* | Port | Not FreeBuild's proprietary `oblien` deploy executor |
| Gellix / cdn.oblien.com fonts | **Explicitly not copied** | System fonts |

**Directly copied into this Netie docs repo this turn:** nothing from those trees. The scorecard cites them.

---

## 3. Parallelism (the "infinite subagents" line)

Deep Agents + LangGraph can fan out async subagents. That is a *mechanism*.

Netie still has a *WIP law*: two epics in flight, ticket batching by shared mental model, every tool through Cortex. "Infinite" without that law is eight workstreams at 80 percent, which this estate already measured.

Scale knob when Crew exists: N ticket runners, each a Deep Agent wrapped by `wrap_deepagents_tools`, Cortex `tool_runner` as the only write/read path, OpenVault `POST /api/crew/gate` on every leave-machine call, token budget per batch, different-run verify before DONE. Concurrency is a config with a ledger, not a slogan.

Netie portable contract (this repo, 2026-08-27): wrap, cap-2 parallel, parent-run graph (`crew_runs.py`: children cannot replace parent, WIP 2, named deficit, OV gate), `close_ticket` refuses same-run verify, token budget, hash ledger, OV gate strips `skill_body`.

---

## 4. PRD / epic holes this scorecard opens (do not start until PRD-001 wave 1)

| Gap | Product | Why it is not a ticket yet |
|---|---|---|
| Space ACL + eval gate | DMS / Cortex | Already PRD-001. First. Portable contract in `scripts/dms_space_acl.py`: two Spaces, one warehouse, abstain outside ACL. Not wired into dms (repo 404). |
| TAS-AIRGPT chunker corpus (tables, repeated headers, labels, multilingual embedding choice) | AirGPT | Repo not in this environment. `TAS/TAS-AIRGPT.md` is the hole list. |
| TAS-POINTER vs UACC tool-for-tool | Pointer | Repo not in this environment. `TAS/TAS-POINTER.md`. |
| Crew repo + Deep Agents wrap | Crew | `PRD-002` drafted; queued after Space boundary. OpenVault #44 crew_gate exists. |
| HT1 live Cloudflare Pages | OpenVault | HUMAN_STOP on OpenVault #18 |
| Leave-machine on Space AI path | Space | Repo not in this environment |
| GitHub Actions billing | Netie docs-ci | Job never started: spending limit. Local `scripts/check_docs.py` is the gate until billing works. OpenVault **main CI is already green**. Constructor pages.yml green; unit tests not on default. |
| Sibling repo write | OpenVault, constructor | cursor[bot] 403 on push. Local branches ready: `cursor/detect-stacks-no-skip-ca9b`, `cursor/constructor-compiler-tests-ca9b`. |

---

## 5. Verify this document

- OpenVault clone HEAD `3030cad` (2026-08-27): `route/strategies.py` says "8 of 18 for pass 1" (comment stale vs OmniRoute's **19** user-facing strategies at `2acbfc6`). `STATUS.md` ~75%; `SHIPPING_MODEL.md` Pages adapter real, HT1 not done. **This VM after fixture unskip:** OpenMW `pytest tests -q` -> 840 passed, 4 skipped (DPAPI). Sibling push 403. **GitHub `main` CI success** 2026-08-25 (merge #43).
- Constructor clone: `node --test tests/compiler.test.cjs` -> 3 passed. Sibling push 403. Default **pages.yml** green; no `test.yml` on HEAD.
- Analogues this turn: `langchain-ai/deepagents` 0.7.9 MIT; OmniRoute `ROUTING_STRATEGY_VALUES` 19 + `quota-share`; NVIDIA llm-router Apache-2.0 **deprecated** for Switchyard.
- Cortex / DMS / AirGPT / Pointer / Space / Control: **not cloned**. Numbers from TAS dated 2026-08-02 or UNVERIFIABLE. Portable specs: `dms_space_acl.py`, `airgpt_chunk.py`, `pointer_click.py`.
- Netie docs-ci on GitHub: job **did not start** (Actions billing: "account payments have failed or spending limit"). Local `python3 scripts/check_docs.py` is the gate (required files + laptop-ASCII + `scripts/test_*.py`).

If a later session has those remotes, replace the UNVERIFIABLE rows with file:line evidence and bump the date on this file.
