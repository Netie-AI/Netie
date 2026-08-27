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

Executable contract in this repo (Cortex remote still 404): `scripts/cortex_path.py`. `jepa` / `gen-cfsm` candidates are refused. DMS answers are tagged `keyword_cascade`; C7 SQL is `off`. Ungoverned writes other than `export_pptx` are refused. `python3 scripts/test_cortex_path.py`.

---

## 1. Scorecard

| Product | Closest analogue | License | Score | Why that number | Move |
|---|---|---|---|---|---|
| **Cortex** vs Claude / Claude Code | `langchain-ai/deepagents` (harness) + our gates | MIT | **2 / 10** as a coding agent. **4 / 10** as governed Q&A | Tool loop and `dag_runner` exist. One invocable write action (`export_pptx`). Web tools can skip `tool_runner`. RBAC absent on the modules that execute. Keyword cascade, not a Claude-class prompt+tool runtime. Internal prompts live in `AGENT_SYSTEM.md`, not in a shipped harness. | Depend Deep Agents *under* `tool_runner`. Do not fork Claude. Do not claim stronger. |
| **OpenVault FreeRoute** vs OmniRoute | `diegosouzapw/OmniRoute` MIT (`2acbfc6`) | MIT | **4 / 10** as a gateway. **6 / 10** as a vault+gate | OmniRoute: **19** user-facing names. FreeRoute **main still 8**. This VM: **15 sorts** plus **4 execution shapes**. `apply_strategy` refuses the 4. `dispatch_combo` runs them. `/v1` fail-closes nameless fusion; with `combo.models` a sequential hop-walk posts panel then judge, falls through an empty first hop, classifies like the key walk, SSE-streams only the last hop, context-relay reads caller `available`/`handoff` and persists caller blobs in-process scoped by issued seat (32-blob cap, no Codex fetch, not SQLite), Anthropic-only shape hops name the skip (no Messages API), no matching hop is 503 not empty, execution-shape `serves()` is catalog-true (garbage / other-provider ids do not rewrite to first choice; key walk still does), and the usage row names the last hop with that hop's `usage` (not a panel sum, not `dispatch`). `model: auto` is catalog pick. No autoCombo engine, no quorum-grace, not parallel fan-out. Strategy+shape+chat tests **77 passed**. Do not count 19 sorts. Push 403. OpenVault **main CI green**. | Land the patches. Do not vendor OmniRoute. |
| **FreeRoute** vs NVIDIA LLM Router | `NVIDIA-AI-Blueprints/llm-router` HEAD `07b0fb6` | Apache-2.0 | **2 / 10** | README: **deprecated** for NVIDIA NeMo Switchyard. v1 was BERT+Triton proxy; v2 experimental is Qwen 1.7B or CLIP+NN, classify-only. FreeRoute still classifies *cost/quota/health* and picks a key. Different job. | Optional later: host Switchyard *behind* OpenVault leave-machine. Do not rewrite Triton. Do not vendor the blueprint. |
| **OpenVault FreeBuild** vs Vercel | `ship/hosts/cloudflare_pages.py` vs Vercel | n/a (Vercel closed) | **2 / 10** | OpenVault main `62bb1c7` STATUS ~78% (2026-08-27). Pages adapter real; **HT1 not done** (HUMAN_STOP #18). Portable `scripts/freebuild_honesty.py`: never construct `*.pages.dev`; simulated is not live. **main CI green** same day. | Finish HT1 on one real Pages deploy. Then Netlify/Coolify. Not ECS first. |
| **DMS** vs "ChatGPT for the warehouse" | AnythingLLM / evidence-QA, later Palantir | mixed | **3 / 10** | TAS-DMS 2026-08-02: 166 passed, Space ACL decorative, no auth, two warehouses, 2 of 5 sheet classes ingest. Cannot demo two customers in one room. Do not clone Palantir. Do not clone AnythingLLM over the envelope. | PRD-001 wave 1. No second repo. |
| **Cortex-Crew** vs Deep Agents | `langchain-ai/deepagents` 0.7.9 | MIT | **0 / 10** as a product. **2 / 10** as a portable wrap | No `Netie-AI/Cortex-Crew` remote. Netie `scripts/crew_*.py` now: wrap (empty wrap and extra unwrapped names refuse), cap-2 hard refuse above 2, parent-run graph, verify, budget, ledger, OV gate. Deep Agents `create_deep_agent(tools=require_wrapped(...))` is the depend path. Talon README: not a production security boundary. OpenVault `POST /api/crew/gate` still not on main; focused patch `openvault-crew-gate.patch` fail-closes unknown kinds (incl. `skill`) and strips bodies. | Create repo. `uv add deepagents`. Wrap every tool. Land the gate patch. |
| **Cortex-Crew** vs OpenWork | `different-ai/openwork` | MIT core; `ee/` is FSL-1.1-MIT (no competing Den for 2 years) | **0 / 10** | Session UX + capability MCP are the take. Do not vendor the desktop (AirGPT+Pointer exist). Do not ship `ee/` as a competing control plane. | Study; reimplement session board in Crew. |
| **Cortex-Crew** vs Grok Bot reconstructed | `b-nnett/grok-bot-0.18-reconstructed` | **none** | **0 / 10** and **do not clone** | Seat-router *idea* only. Original `scripts/seat_router.py` queues cursor/claude-code/codex when `operator_logged_in`. No browser drive. | Keep original. Do not clone. |
| **AirGPT** vs ChatGPT | Open WebUI / LibreChat | MIT | **UNVERIFIABLE** HEAD. Corpus exists | Repo 404. Portable table-chunk corpus in `scripts/airgpt_chunk.py` (repeated headers, ragged rows, labels). Chunker in `rag/ingest.py` still unread. | Add AirGPT remote. Run corpus against `rag/`. |
| **Netie Control** vs Apache Guacamole | `apache/guacamole-client` | Apache-2.0 | **1 / 10** as Guacamole. **2 / 10** as a Crew board view | Wrong analogue for RDP. Portable `scripts/control_board.py` projects run/ledger/refusal cards and refuses a dag_runner. Repo still 404. | Fold into Crew. Do not clone Guacamole. |
| **Pointer** vs Perplexity Computer / UACC | `uacc` on PyPI; `e2b-dev/open-computer-use` Apache-2.0 | MIT / Apache | **UNVERIFIABLE** HEAD. Fail-closed click spec exists | Tray still not cloned. `scripts/pointer_click.py` refuses unlabeled / no Cortex intent and does not touch `os.environ`. | Measure Pointer HEAD. MCP-wrap UACC behind `tool_runner` if the 68 tools are the gap. |
| **Netie Space** vs Peek / macOS Preview | Windows: PowerToys Peek. macOS: Quick Look + `altic-dev/PeekX` (MIT) | mixed | **6 / 10** as a preview app. **2 / 10** as governed | TAS-SPACE: most finished product, leave-machine ungated on HEAD. Portable `scripts/space_leave.py` now refuses ungated leave, plaintext keys, and local vault scan. Not wired into Space (repo 404). | Add CI + call this gate from AiService/OCR. Rename one "Space". |
| **Constructor** vs React Flow | `xyflow/xyflow` (`@xyflow/react`) | MIT | **2 / 10** as a node editor. **4 / 10** as a Cortex IR compiler | Live clone: 11 files, custom canvas. This VM: `node --test tests/compiler.test.cjs` **20 passed** (empty graph / unknown kind / cycle / dangling edge / missing id / duplicate id invent no Cortex nodes; `ghostWalk` refuses those instead of walking `topo()` leftovers; connector-only does not invent `EMIT`; unlabeled `tool_call` does not invent `export_pptx`; inspect shows `(pick)` not a silent first-choice). Default branch **pages.yml green**; **no unit-test workflow** on HEAD. Push 403. See `TAS/TAS-CONSTRUCTOR.md`. | Land the test branch when write access exists. `npm i @xyflow/react` only if the canvas must feel like React Flow. |

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

Netie portable contract (this repo, 2026-08-27): wrap (empty wrap and extra unwrapped names refuse), cap-2 parallel (hard refuse above 2), parent-run graph (`crew_runs.py`: children cannot replace parent, WIP 2, named deficit, OV gate), `close_ticket` refuses same-run verify, token budget, hash ledger, OV gate strips `skill_body`.

---

## 4. PRD / epic holes this scorecard opens (do not start until PRD-001 wave 1)

| Gap | Product | Why it is not a ticket yet |
|---|---|---|
| Space ACL + eval gate | DMS / Cortex | Already PRD-001. First. Portable contract in `scripts/dms_space_acl.py`: two Spaces, one warehouse, abstain outside ACL. Not wired into dms (repo 404). |
| TAS-AIRGPT chunker corpus (tables, repeated headers, labels, multilingual embedding choice) | AirGPT | Repo not in this environment. `TAS/TAS-AIRGPT.md` is the hole list. |
| TAS-POINTER vs UACC tool-for-tool | Pointer | Repo not in this environment. `TAS/TAS-POINTER.md`. |
| Crew repo + Deep Agents wrap | Crew | `PRD-002` drafted; queued after Space boundary. OpenVault #44 crew_gate exists; focused `openvault-crew-gate.patch` fail-closes unknown kinds on `main`. |
| HT1 live Cloudflare Pages | OpenVault | HUMAN_STOP on OpenVault #18 |
| Leave-machine on Space AI path | Space | Repo not in this environment |
| GitHub Actions billing | Netie docs-ci | Job never started: spending limit. Founder path: `docs/ACCESS.md`. Local `make ci` / `python3 scripts/check_docs.py` is the gate. OpenVault main CI is already green. |
| Sibling repo write | OpenVault, constructor | cursor[bot] 403 on push. Local branches ready: `cursor/detect-stacks-no-skip-ca9b`, `cursor/constructor-compiler-tests-ca9b`. |

---

## 5. Verify this document

- OpenVault clone HEAD `62bb1c7` (2026-08-27): `route/strategies.py` on **main** still 8 of 19. After routing patches through `openvault-hop-catalog.patch`: 15 sorts + 4 named execution shapes, `/v1` fail-closes nameless fusion, hop-walks `combo.models` sequentially (empty first hop falls through; classify_attempt on posts; last hop may SSE; context-relay uses caller available/handoff and persists caller blobs in-process scoped by issued seat with a 32-blob cap; Anthropic-only hops name the skip; no matching hop is 503; execution-shape serves() is catalog-true, not first-choice rewrite; usage names the last hop and copies that hop's `usage`), `pytest tests/test_route_strategies.py tests/test_execution_shapes.py tests/test_execution_chat.py tests/test_freeroute_acceptance.py` -> **77 passed**. `STATUS.md` ~78%; HT1 not done. Earlier full OpenMW `pytest tests -q` after detect-stacks unskip: 840 passed, 4 skipped (DPAPI). Sibling push 403. **GitHub `main` CI success** 2026-08-27 (docs/status #45).
- Constructor clone: `node --test tests/compiler.test.cjs` -> 20 passed after constructor-compiler-tests, empty-graph, ir-refuse, ir-ids, ghost-refuse, ir-emit, tool-action, and inspect-action patches. Sibling push 403. Default **pages.yml** green; no `test.yml` on HEAD.
- Analogues this turn: `langchain-ai/deepagents` 0.7.9 MIT; OmniRoute `ROUTING_STRATEGY_VALUES` 19 + `quota-share`; NVIDIA llm-router Apache-2.0 **deprecated** for Switchyard.
- Cortex / DMS / AirGPT / Pointer / Space / Control: **not cloned**. Numbers from TAS dated 2026-08-02 or UNVERIFIABLE. Portable specs: `dms_space_acl.py`, `airgpt_chunk.py`, `pointer_click.py`.
- Netie docs-ci on GitHub: job **did not start** (Actions billing: "account payments have failed or spending limit"). Local `python3 scripts/check_docs.py` is the gate (required files + laptop-ASCII + `scripts/test_*.py`).

If a later session has those remotes, replace the UNVERIFIABLE rows with file:line evidence and bump the date on this file.
