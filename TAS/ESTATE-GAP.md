# TAS-ESTATE-GAP - measured distance to named analogues

**Measured:** 2026-08-28. Scores are 0-10 against the analogue's *buyer-visible job*, not against a vibe.
**This VM clones public:** Netie, Cortex (`bf4ecee`), OpenVault (`62bb1c7`), constructor (`4896ddd`), Pointer (`8c0e6c2`), dms (`3f9a9be`), netie-control, Netie-KB. **Still missing:** Cortex-Crew, Space, AirGPT. Sibling **push 403**. Secret scan of those HEADs: CLEAN (no live `sk-or-v1-` / `csk-` dumps).

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

Executable contract in this repo (Cortex remote still 404): `scripts/cortex_path.py`. `jepa` / `gen-cfsm` candidates are refused. DMS answers are tagged `keyword_cascade`; C7 SQL is `off` (`c7_sql=True` refuses: 17 confidently wrong). Ungoverned writes other than `export_pptx` / `item.intake` / `amend.apply` / `call_action` are refused. A write without an actor is refused. An answer without `verified=True` is refused. `/a2a/messages` is dms-pack only. A tool that skips `tool_runner` is refused. Coding-agent tools (`bash` / filesystem) are refused even via `tool_runner`. `python3 scripts/test_cortex_path.py`.

---

## 1. Scorecard

| Product | Closest analogue | License | Score | Why that number | Move |
|---|---|---|---|---|---|
| **Cortex** vs Claude / Claude Code | `langchain-ai/deepagents` (harness) + our gates | MIT | **2 / 10** as a coding agent. **4 / 10** as governed Q&A | Tool loop and `dag_runner` exist. HEAD still one invocable write (`export_pptx`). Portable path also gates `item.intake` / `amend.apply` / `call_action` as writes needing an actor; `agent.checked` stays an event. Portable path refuses anonymous writes, unverified answers, non-dms `/a2a/messages`, tools that skip `tool_runner`, `c7_sql=True` (17 confidently wrong), and coding-agent tools (`bash` / `shell` / `execute` / filesystem) even via `tool_runner` (Cortex is not Claude Code). HEAD still: web tools can skip `tool_runner`; RBAC absent on the modules that execute; `verified` optional on `/dms/query`. Keyword cascade, not a Claude-class prompt+tool runtime. Internal prompts live in `AGENT_SYSTEM.md`, not in a shipped harness. | Depend Deep Agents *under* `tool_runner`. Do not fork Claude. Do not claim stronger. |
| **OpenVault FreeRoute** vs OmniRoute | `diegosouzapw/OmniRoute` MIT (`2acbfc6`) | MIT | **4 / 10** as a gateway. **6 / 10** as a vault+gate | OmniRoute: **19** user-facing names. FreeRoute **main still 8**. This VM: **15 sorts** plus **4 execution shapes**. `apply_strategy` refuses the 4. `dispatch_combo` runs them. `/v1` fail-closes nameless fusion; with `combo.models` a sequential hop-walk posts panel then judge, falls through an empty first hop, classifies like the key walk, SSE-streams only the last hop, context-relay reads caller `available`/`handoff` and persists caller blobs in-process scoped by issued seat (32-blob cap, no Codex fetch, not SQLite), Anthropic-only shape hops name the skip (no Messages API), no matching hop is 503 not empty, execution-shape `serves()` is catalog-true (garbage / other-provider ids do not rewrite to first choice; key walk still does), and the usage row names the last hop with that hop's `usage` (not a panel sum, not `dispatch`). `model: auto` is catalog pick. Asking for `parallel` / `quorum_grace` / Codex quota fetch / SQLite persist / autoCombo / token compression / MCP/A2A / `quota-share` is 501, not a silent sequential walk. Product patch: `/v1` `combo.strategy: quota-share` (and PUT `/api/route/strategy`) is 501 `openvault_unported`, not unknown 400 and not a key walk. Body `parallel` / sqlite persist / autoCombo / compress / MCP/A2A / quota-fetch are the same 501. Hop posts drop `combo` / `skill_body` / OmniRoute flags (handoff blobs do not ride to the provider). `/v1` with `skill_body` is 400 `openvault_crew_body`. Sidecar `metadata` / `extra` bags with those keys are the same 400; hop posts strip them. Chat `messages` text may still say the word. No autoCombo engine, no quorum-grace, not parallel fan-out. Strategy+shape+chat tests **145 passed**. Do not count 19 sorts. Push 403. OpenVault **main CI green**. | Land the patches. Do not vendor OmniRoute. |
| **FreeRoute** vs NVIDIA LLM Router | `NVIDIA-AI-Blueprints/llm-router` HEAD `07b0fb6` (deprecated for NeMo Switchyard) | Apache-2.0 | **2 / 10** | README: **deprecated** for NVIDIA NeMo Switchyard. v1 was BERT+Triton proxy; v2 experimental is Qwen 1.7B or CLIP+NN, classify-only. Switchyard's job is `llm_classifier` / `stage_router`. FreeRoute still classifies *cost/quota/health* and picks a key. Different job. Portable `scripts/switchyard_honesty.py`: host Switchyard only behind OpenVault leave-machine; refuse vendoring `llm-router`; refuse rewriting Triton; refuse claiming FreeRoute *is* Switchyard. Score stays **2 / 10**. | Host Switchyard *behind* OpenVault leave-machine. Do not rewrite Triton. Do not vendor the blueprint. |
| **OpenVault FreeBuild** vs Vercel | `ship/hosts/cloudflare_pages.py` vs Vercel | n/a (Vercel closed) | **2 / 10** | OpenVault main `62bb1c7` STATUS ~78% (2026-08-27). Pages adapter real; **HT1 not done** (HUMAN_STOP #18). Portable `scripts/freebuild_honesty.py`: never construct `*.pages.dev`; simulated is not live. Product patch `openvault-ship-netie.patch`: a live label goes through `claim_deploy` (`from netie.route import report_deploy` when Netie is installed; same rule locally otherwise). `classify_deployment` still names simulated. **main CI green** same day. | Finish HT1 on one real Pages deploy. Then Netlify/Coolify. Not ECS first. |
| **DMS** vs "ChatGPT for the warehouse" | AnythingLLM / evidence-QA, later Palantir | mixed | **3 / 10** | TAS-DMS 2026-08-02: 166 passed, Space ACL decorative, no auth, two warehouses, 2 of 5 sheet classes ingest. Cannot demo two customers in one room. Portable `scripts/dms_space_acl.py` now copies rows, abstains a row that declares another table, abstains Cortex DuckDB for a DMS-bound Space, abstains an answer with no SQL, abstains SQL that names an ungranted table or omits the asked table, abstains bronze/warehouse browse of an ungranted table, abstains `chat_mode=True` (AnythingLLM overlay), and abstains an answer over DitchContext 12k (no silent drop). Do not clone Palantir. Do not clone AnythingLLM over the envelope. | PRD-001 wave 1. No second repo. |
| **Cortex-Crew** vs Deep Agents | `langchain-ai/deepagents` 0.7.9 | MIT | **0 / 10** as a product. **3 / 10** as a portable wrap | No `Netie-AI/Cortex-Crew` remote. Netie `scripts/crew_deepagents.py` is the only `create_deep_agent` call site: wrap first, public `crew_harness_profile` (`HarnessProfile.excluded_tools` covers filesystem / `glob` / `grep` / `delete` / `execute` / `task` / `write_todos`; `excluded_middleware` drops `SummarizationMiddleware` so `/conversation_history` is not a transcript dump; general-purpose subagent off). Injected `factory=` without `register=` refuses (else builtins stay on). `bind_deep_agent` / `execute_capability` / `execute_capabilities` / `run_open_ticket` / `run_batch` require `TokenBudget` (Deep Agents default is unbounded spend). Wrap `skill_body` refuses and does not spend; over-budget wrap / ticket does not execute (ticket stays open). Product-caller test registers into Deep Agents 0.7.9 and asserts lookup still excludes `task`/`ls`/`execute` with GP off. `skills` / `memory` / `subagents` / `system_prompt` / `middleware` / `backend` / `response_format` / `debug` refuse, checkpointer is `False` (ids-only is `crew_checkpoint`). Empty wrap and extra unwrapped names refuse. HITL on known writes (`export_pptx` / `item.intake` / `amend.apply` / `call_action`), cap-2, parent-run, `skill` kind refused until a registry row exists, ticket runner, verify, budget, ledger, OV gate. Talon README: not a production security boundary. OpenVault `POST /api/crew/gate` still not on main; focused patches `openvault-crew-gate.patch` then `openvault-crew-netie.patch` (`check_crew_gate` uses `from netie.crew import refuse_crew_gate` when Netie is installed; same rule locally otherwise). Do not vendor the tree. | Create repo. `uv add git+https://github.com/Netie-AI/Netie.git` then `from netie.crew import bind_deep_agent, crew_harness_profile, TokenBudget`. `uv add deepagents`. Land the gate patch. |
| **Cortex-Crew** vs OpenWork | `different-ai/openwork` | MIT core; `ee/` is FSL-1.1-MIT (no competing Den for 2 years) | **0 / 10** as a product. **2 / 10** as a portable session+capability MCP | Session UX + capability MCP are the take. Portable `project_session` is ids/todos/permissions/handoff only (no transcript). Portable `scripts/crew_capabilities.py` is `search_capabilities` / `execute_capability` / `execute_capabilities`: granted ids only, ungranted does not execute, Deep Agents builtins and billing-bypass names never list or run, skill_body refuses, leave-machine needs OpenVault, batch is cap-2. `load_den` refuses OpenWork `ee/` (FSL) and a second desktop. Session permissions drop builtins. Do not vendor the desktop (AirGPT+Pointer exist). Do not ship `ee/` as a competing control plane. | Create repo. Import `execute_capability`. Do not vendor `ee/`. |
| **Cortex-Crew** vs Grok Bot reconstructed | `b-nnett/grok-bot-0.18-reconstructed` | **none** | **0 / 10** and **do not clone** | Seat-router *idea* only. Original `scripts/seat_router.py` queues cursor/claude-code/codex when `operator_logged_in`. Grok Bot / pointer-drive / cursor-ui name as `billing-bypass product`. No browser drive. | Keep original. Do not clone. |
| **AirGPT** vs ChatGPT | Open WebUI / LibreChat | MIT | **UNVERIFIABLE** HEAD. Corpus exists | Repo 404. Portable table-chunk corpus in `scripts/airgpt_chunk.py` (repeated headers, ragged short rows, extra cells dropped not kept as a nameless column, labels). `retrieve_space` cites only complete chunks labeled for that Space; unlabeled and incomplete rows are not evidence; `chat_*.md` is not evidence unless `chats_as_evidence`; file mention cannot pull another Space. NVIDIA_RAG_EVAL / semantic / LlamaIndex as a chunker refuses (catalog, not a splitter). `cross_chat_memory` abstains (ChatGPT memory, not AirGPT). Retrieve over DitchContext 12k abstains. Chunker in `rag/ingest.py` still unread. | Add AirGPT remote. Run corpus against `rag/`. |
| **Netie Control** vs Apache Guacamole | `apache/guacamole-client` | Apache-2.0 | **1 / 10** as Guacamole. **2 / 10** as a Crew board view | Wrong analogue for RDP. Portable `scripts/control_board.py` projects run / Factory ticket / epic / ledger / refusal cards plus a session view (no transcript), refuses prompt/transcript/key leaks, refuses RDP/VNC/SSH/telnet/Kubernetes/Guacamole kinds, refuses a dag_runner, and refuses a board/session over DitchContext 12k (no silent drop). `scripts/crew_runner.py` puts Cortex refusals on that board and leaves the ticket open. `Netie-AI/netie-control` is public. | Fold into Crew. Do not clone Guacamole. |
| **Pointer** vs Perplexity Computer / UACC | `uacc` on PyPI; `e2b-dev/open-computer-use` Apache-2.0 | MIT / Apache | **3 / 10** as hands | Pointer HEAD `8c0e6c2` clones. Catalog is 15 `uacc_*` ids in `electron/netie/uacc.js` (planner labeled read on HEAD). Portable wrap maps those ids and still refuses planner/clipboard/window dump/uncropped screen-info. UACC 68 MCP names stay behind Cortex. `windows-mcp` binds local. Do not import `uacc`. | Tray callers for `bind_pointer_skill`. |
| **Netie Space** vs Peek / macOS Preview | Windows: PowerToys Peek. macOS: Quick Look + `altic-dev/PeekX` (MIT) | mixed | **6 / 10** as a preview app. **2 / 10** as governed | TAS-SPACE: most finished product, leave-machine ungated on HEAD. Portable `scripts/space_leave.py` now refuses ungated leave, `user.env` key writes, local vault scan, secret-file preview (`.env` / `.pem` / `.netrc`), secret-file writes even when not marked plaintext (`id_rsa` / `.pem`), poor-OCR-as-Baidu-grant, and AI chat over a preview (Peek never POSTs the file; excerpt over DitchContext 12k refuses). Not wired into Space (repo 404). | Add CI + call this gate from AiService/OCR. Rename one "Space". |
| **Constructor** vs React Flow | `xyflow/xyflow` (`@xyflow/react`) | MIT | **2 / 10** as a node editor. **4 / 10** as a Cortex IR compiler | Live clone `4896ddd`: 11 files, custom canvas, `app.js` before `engine.js` until patched. Portable `scripts/constructor_honesty.py` refuses `@xyflow/react` as the compiler (`compileIR` stays ours). This VM on public HEAD: 12 patches, `node --test` **29 passed** (listed object drop, no invented `T0`, Kahn emit, unknown action, `NOTE_LEAK`, `cortexPayload`, engine-before-app). `inspect-object` still fails. Unpushed `eebff20` 26-patch stack was 62 passed. Default branch **pages.yml green**; **no unit-test workflow** on HEAD. Push 403. See `TAS/TAS-CONSTRUCTOR.md`. | Land the 12 patches that fit `4896ddd`. Portable `scripts/constructor_ir.py` + `constructor_action_bind.py`. Do not vendor Activeflow. `npm i @xyflow/react` only if the canvas must feel like React Flow. |

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

Scale knob when Crew exists: N ticket runners, each a Deep Agent from `bind_deep_agent` with a `TokenBudget`, Cortex `tool_runner` as the only write/read path, OpenVault `POST /api/crew/gate` on every leave-machine call, token budget per batch, different-run verify before DONE. Concurrency is a config with a ledger, not a slogan.

Netie portable contract (this repo, 2026-08-28): product repos import `from netie.crew import bind_deep_agent, crew_harness_profile, TokenBudget` (`uv add git+https://github.com/Netie-AI/Netie.git`; wheel ships contracts as `netie._contracts`). Wrap (empty wrap and extra unwrapped names refuse; Deep Agents builtins `ls`/`read_file`/`write_file`/`edit_file`/`delete`/`glob`/`grep`/`execute`/`task`/`write_todos` refuse even if a gate would allow; wrap `skill_body` refuses and does not spend; over-budget wrap does not execute), `bind_deep_agent` / `execute_capability` / `execute_capabilities` / `run_open_ticket` / `run_batch` (MIT factory + OpenWork-shaped MCP + ticket runner + cap-2 parallel; require `TokenBudget`; builtins excluded via `crew_harness_profile`; injected factory without harness register refuses; `task` subagent off; `system_prompt` / `middleware` / `backend` refuse), OpenWork-shaped `search_capabilities` (ungranted / builtin / billing-bypass / skill_body refuse; leave-machine needs OV; batch cap-2), cap-2 parallel (hard refuse above 2), parent-run graph (`crew_runs.py`: children cannot replace parent, WIP 2, named deficit, OV gate; `skill` kind refused until a registry row exists), factory `index()` drops prompts, ledger refuses skill_body on append, `close_ticket` refuses same-run verify, token budget (HITL / builtin / skill_body refusals do not spend; over-budget tickets stay open), hash ledger, OV gate strips `skill_body`, checkpoint/summarise ids-only (`scripts/crew_checkpoint.py`; resume cannot recover a prompt).

---

## 4. PRD / epic holes this scorecard opens (do not start until PRD-001 wave 1)

| Gap | Product | Why it is not a ticket yet |
|---|---|---|
| Space ACL + eval gate | DMS / Cortex | Already PRD-001. First. Portable contract in `scripts/dms_space_acl.py`: two Spaces, named warehouse bind, abstain outside ACL, copy rows so mutation cannot punch the warehouse, abstain if a row declares another table, abstain Cortex DuckDB for a DMS-bound Space, abstain if the answer has no SQL, abstain if SQL names an ungranted table or omits the asked table, abstain an answer over DitchContext 12k. Not wired into dms (repo 404). |
| TAS-AIRGPT chunker corpus (tables, repeated headers, labels, multilingual embedding choice) | AirGPT | Repo not in this environment. Portable `retrieve_space` does not cite another Space, incomplete rows, unlabeled rows, or `chat_*.md`. NVIDIA_RAG_EVAL / semantic split is not a chunker. `cross_chat_memory` abstains. Over-budget retrieve abstains. `TAS/TAS-AIRGPT.md` is the hole list. |
| TAS-POINTER vs UACC tool-for-tool | Pointer | Repo not in this environment. Portable wrap lists UACC 1.1.0's 68 names and refuses planner/history/clipboard/JS/uncropped screenshot/`get_screen_info`/page dump/process list/window dump/env dump/uncropped paint. `TAS/TAS-POINTER.md`. |
| Crew repo + Deep Agents wrap | Crew | `PRD-002` drafted; queued after Space boundary. Portable HITL + ticket runner + ids-only checkpoint + `search_capabilities` / `execute_capability` exist in Netie (`scripts/crew_runner.py`, `scripts/crew_checkpoint.py`, `scripts/crew_capabilities.py`). OpenVault #44 crew_gate exists; focused `openvault-crew-gate.patch` fail-closes unknown kinds on `main`; `openvault-crew-netie.patch` wires that endpoint through Netie when installed. |
| HT1 live Cloudflare Pages | OpenVault | HUMAN_STOP on OpenVault #18 |
| Leave-machine on Space AI path | Space | Repo not in this environment. Portable `may_preview` / `chat_preview` / `ocr_cloud` / `persist_key` refuse secrets, ungated chat-over-preview, over-budget excerpts, and Baidu-on-poor-OCR. |
| GitHub Actions billing | Netie docs-ci | Job never started: spending limit. Founder path: `docs/ACCESS.md`. Local `make ci` / `python3 scripts/check_docs.py` is the gate. OpenVault main CI is already green. |
| Sibling repo write | OpenVault, constructor | cursor[bot] 403 on push. Local branches ready: `cursor/detect-stacks-no-skip-ca9b`, `cursor/constructor-compiler-tests-ca9b`. |

---

## 5. Verify this document

- OpenVault clone HEAD `62bb1c7` (2026-08-27): `route/strategies.py` on **main** still 8 of 19. After routing patches through `openvault-hop-catalog.patch`: 15 sorts + 4 named execution shapes, `/v1` fail-closes nameless fusion, hop-walks `combo.models` sequentially (empty first hop falls through; classify_attempt on posts; last hop may SSE; context-relay uses caller available/handoff and persists caller blobs in-process scoped by issued seat with a 32-blob cap; Anthropic-only hops name the skip; no matching hop is 503; execution-shape serves() is catalog-true, not first-choice rewrite; usage names the last hop and copies that hop's `usage`), `pytest tests/test_route_strategies.py tests/test_execution_shapes.py tests/test_execution_chat.py tests/test_freeroute_acceptance.py` -> **77 passed**. `STATUS.md` ~78%; HT1 not done. Earlier full OpenMW `pytest tests -q` after detect-stacks unskip: 840 passed, 4 skipped (DPAPI). Sibling push 403. **GitHub `main` CI success** 2026-08-27 (docs/status #45).
- Constructor clone `4896ddd`: 12 patches then `node --test tests/compiler.test.cjs` -> **29 passed**. `constructor-inspect-object.patch` fails. Sibling push 403. Default **pages.yml** green; no `test.yml` on HEAD.
- Analogues this turn: `langchain-ai/deepagents` 0.7.9 MIT; OmniRoute `ROUTING_STRATEGY_VALUES` 19 + `quota-share`; NVIDIA llm-router Apache-2.0 **deprecated** for Switchyard (portable host gate in `scripts/switchyard_honesty.py`; score stays 2/10).
- Cortex / DMS / AirGPT / Pointer / Space / Control: Cortex `bf4ecee`, dms `3f9a9be`, Pointer `8c0e6c2`, netie-control, Netie-KB **cloned public 2026-08-28** (secret scan CLEAN). AirGPT / Space / Cortex-Crew still missing. Portable specs: `dms_space_acl.py`, `dms_ontology.py`, `airgpt_chunk.py`, `pointer_click.py`, `pointer_hands.py` (Pointer HEAD 15 catalog ids), `constructor_ir.py`, `crew_durable.py`, `crew_skills.py`, `freeroute_free_pool.py`.
- Netie docs-ci on GitHub: job **did not start** (Actions billing). Local `python3 scripts/check_docs.py` is the gate.

If a later session has those remotes, replace the UNVERIFIABLE rows with file:line evidence and bump the date on this file.

---

## 6. Handwritten trees -> Netie products (copy nothing wholesale)

E:\\ paths are the founder's study machines. This cloud VM does not mount them. GitHub HEADs measured 2026-08-28 are the source of truth. License law in section 0 still wins: depend, port with attribution, or reimplement. Do not vendor a tree.

| Local tree | Product | Already here (do not rebuild) | Next for a specialist agent |
|---|---|---|---|
| `E:\\Cortex\\myactiveflow`, `myactivepieces` | **Constructor first** | 12 patches on public `4896ddd`, **29 passed**. Portable `scripts/constructor_honesty.py` plus `constructor_ir.py` + `constructor_action_bind.py` | Land the 12 patches. Unknown piece refuses. No n8n clone. |
| `E:\\Netie\\mygastown`, `E:\\openworker`, `E:\\mydeepagents` | **Cortex-Crew** | `scripts/crew_*.py` wrap/HITL/cap-2/OV gate/ids-only checkpoint. `crew_durable.py` resumes after process death. **New:** `crew_skills.py` (skill kind needs a registry row, no body) | Create `Netie-AI/Cortex-Crew`. `uv add deepagents`. Import Netie wrap. Study OpenWork session UX. Do not vendor `ee/` or gastown. |
| `E:\\Netie\\mypaperclip` | Control, fold into Crew | Public `Netie-AI/netie-control`. Portable `control_board.py` | Merge UI into Crew. Not Guacamole. |
| `E:\\Netie\\myOmniRoute` | **OpenVault FreeRoute** | 15 sorts + 4 shapes in patches (push 403). `scripts/freeroute_free_pool.py` + product `openvault-free-pool.patch` (`pick_free_pool`; empty pool 503 + register_url; no invented keys) | Land patches including free-pool. Do not vendor OmniRoute. |
| `E:\\mycogitorium`, `E:\\mysemantica`, `E:\\myzep` | DMS / Palantir-class | Portable `dms_space_acl.py` + **new** `dms_ontology.py` (objects = granted tables; evidence must cite; Palantir vendor refuses). dms HEAD `3f9a9be` `live_ask` still mints `demo_acl` | PRD-001: stop `live_ask` using `demo_acl`. Ontology from granted tables. Do not clone Palantir. |
| `E:\\mygraphiti`, `E:\\zep-go`, `E:\\mygraphify` | AirGPT / OV `memory` kind | OV gate already has `memory`. AirGPT chunker portable | Wire retrieve_space. Memory is OpenVault+Cortex, not a fourth store. |
| `E:\\Cortex\\Windows-MCP` | Pointer | `pointer_click.py` + `pointer_hands.py`. Pointer HEAD `8c0e6c2` has 15 `uacc_*` catalog ids mapped by `bind_pointer_skill`. `windows-mcp` binds local | Tray callers. Depend Windows-MCP/UACC under the wrap. |
| `E:\\Cortex\\myguaca`, `E:\\Cortex\\myrakazo` | Cortex UI tokens only | Cortex public HEAD `bf4ecee`. Guaca/Rakazo not vendored; CSS credit only | Role gate on execute modules (`cortex_path.py` now refuses write/tool without `role`). Do not clone Guacamole into Control. |

### Agent lanes (send one specialist per lane)

1. **Constructor** - on `4896ddd`: apply README 12 patches; `node --test` 29 passed; import `from netie.route import compile_ir, bind_action`. Rebase `app.js` inspect-object separately. Add `test.yml`. Do not vendor Activeflow.
2. **Cortex-Crew** - new empty repo; `uv add git+https://github.com/Netie-AI/Netie.git` then `from netie.crew import bind_deep_agent, crew_harness_profile, TokenBudget, persist, resume, register_skill`; `uv add deepagents`; fold Control board; WIP 2. Do not vendor `ee/`.
3. **OpenVault** - apply `docs/patches/` README order through `openvault-free-pool.patch`; `from netie.route import assist_free_pool` / `pick_free_pool`; never commit keys.
4. **DMS Palantir-next** - replace `Executor.live_ask` `demo_acl` with `resolve_session_acl`; import `from netie.dms import mint_object, evidence_or_abstain`; no second warehouse brain; do not clone Palantir.
5. **Pointer** - `from netie.pointer import bind_pointer_skill, invoke_hand`; HEAD 15 catalog ids; Windows-MCP behind Cortex only.

C2/MIN_TESTS stand. Do not mint Cortex #42. Do not clone `b-nnett/grok-bot-0.18-reconstructed`.

