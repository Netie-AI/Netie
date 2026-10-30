# TAS-AIRGPT - AirGPT technical architecture

**Plane:** 4 (customer host shell) · **Repo:** `jian-hong/AirGPT` (this token: not found)
**Measured:** 2026-08-27 from OpenVault contracts and TAS-dated estate docs, **not** from an AirGPT checkout. Chunker claims below are UNVERIFIABLE until the repo is in this environment.

---

## 1. What it is

The customer host shell: chat, settings, pairing, apps hub, phone-PC sync, ClipDrop key ingest, optional FreeIDE on `:8765`. Thin client of OpenVault for custody and of Cortex for brains.

**Is not:** a second vault, a second `dag_runner`, or ChatGPT.

---

## 2. Entry points (from OpenVault evidence)

| Path | Role | Evidence |
|---|---|---|
| `:8765` | AirGPT + FreeIDE | OpenVault DR-0004 ports table |
| `FreeIDE/openvault_bridge.py` | ping/status/mesh/gate | DR-0004 |
| ClipDrop ingest | `POST /api/keys/ingest` on OpenVault | `CLIPDROP_CONTRACT.md` |
| `rag/ingest.py` | source ingest jobs | `ASKS_CLAUDE_QUEUES_RAG.md` Ask C/D |
| `rag/store.py` `ingest_jobs` | job store | same |
| `docs/who-does-what.md` | named, not fetched | same |

---

## 3. RAG / chunking - the founder's questions

Asked: regex-friendly on broken tables, repeated headers, keyword labels, multilingual embeddings, selectable models.

**What the OpenVault notes actually say:**

- Spaces exist; "Good Good" Space 5 must not cite `chat_*.md` after purge (`chats_as_evidence: false`).
- Fabrication scrub on chat-ingest is a *plan*, path `rag/ingest.py`.
- Ingest-time authority column: spec only.
- File-scoped retrieve on @-mention must not leak other spaces.
- Async create: `POST .../sources` returns `{ job_id }`; poll `pollRagIngestJob`.
- NVIDIA_RAG_EVAL is a *model catalog* (NIM 8B-70B), not a chunker.

**What we cannot claim:** regex vs semantic split, table reconstitution, embedding model picker, multilingual adaptive routing. Those need `rag/` on HEAD.

Portable corpus in this repo (AirGPT still 404): `scripts/airgpt_chunk.py`. Repeated headers are not extra rows, ragged short rows do not invent cells, extra cells are dropped (not a nameless column), `# warehouse:` labels stick to following rows. `retrieve_space` cites only complete chunks labeled for that Space; unlabeled and incomplete rows are not evidence; north cannot cite south; `chat_*.md` is not evidence (`chats_as_evidence` defaults false); file mention cannot pull another Space's file. `chunk_table(splitter="nvidia_rag_eval")` / `semantic` / `llamaindex` raises; retrieve with that embedder abstains. `cross_chat_memory` abstains. Retrieve over DitchContext 12k abstains (no silent drop). `python3 scripts/test_airgpt_chunk.py`. Not LlamaIndex; a splitter we own until HEAD is measured.

Closest licensed kits *after* measure, not before: LlamaIndex (MIT) or a small splitter we own. Do not paste ChatGPT.

---

## 4. Trust boundaries (from contracts)

| Boundary | Enforced? |
|---|---|
| No second vault | ClipDrop: secret in RAM only; fail closed if OpenVault down |
| Leave-machine | OpenVault gate; DR-0004 said gate closed offline |
| RAG isolation across Spaces | Required in Ask C; not verified here |

---

## 5. vs ChatGPT

ChatGPT is a hosted assistant with memory, tools, and a huge eval set. AirGPT is a *shell* that is supposed to show Cortex answers with sources. Distance without HEAD: **UNVERIFIABLE**. Historical size (619 files, 158 tests) is founder-stated, not cloned.

---

## 6. Verify

```
NEEDS-YOU TAS-AIRGPT  add jian-hong/AirGPT (or Netie-AI/AirGPT) to this environment
```

Then: pytest on `rag/` against this corpus, and a live Space-5 cite check with zero `chat_*.md`.

---

## Appendix - checkout-measured map (2026-08-03, from PR #1)

Kept on merge so the checkout-measured detail is not lost. Main body above is newer; where they disagree, the body wins until re-measured.

### TAS-AIRGPT - AirGPT technical architecture

**Plane:** 4 (application / host shell) · **Repo:** `jian-hong/AirGPT` · `D:\AirGPT`
**Measured:** 2026-08-03. Route surface counted from `clipdrop.py` path handlers; **374**
tests collected (`pytest --collect-only`).

**Tier 4 map:** purpose · plane · surface · dependencies · stores · trust · shipped vs
scaffold · verify

---

#### 1. What it is

**One line:** local-first Windows host shell - clipboard, chat, phone sync, settings, apps
hub - thin client of OpenVault (keys, gate) and Cortex (brains, workflows).

A local-first Windows host shell: clipboard capture, chat, phone-to-PC sync, settings,
pairing QR/tunnel, apps hub, RAG spaces, and thin clients over OpenVault (keys, gate,
mesh) and Cortex (brains, workflows, computer-use). Ships as a portable tree beside
`data\` - copy the folder, install Python once, run `restart.bat`.

**It is not a second key vault and not a second orchestrator.** Custody and leave-machine
decisions belong to OpenVault; architecture presets and agent loops belong to Cortex.
See `PRODUCT_ROLES.md` (copied in-repo).

---

#### 2. Entry points

| Path | Role |
|---|---|
| `clipdrop.py:6215` | `main()` - `ThreadingHTTPServer` on `0.0.0.0:8765` |
| `server.py` | re-exports `clipdrop.main` |
| `restart.bat` / `start.bat` | install deps + launch |
| `config.py:60` | `ROOT` - parent of `clipdrop.py`; `DATA_DIR` beside app |
| `ai_engine.py` | provider cascade - **openvault leads every role band** |
| `OpenIDE/openvault_bridge.py` | loopback HTTP to OpenVault `:5000` |
| `control_plane/app.py` | **optional** FastAPI license server on `:8787` |
| `apps/*/index.html` | static demo widgets (counter, todo, hello-ship, etc.) |
| `OpenIDE/` | FreeIDE backend + UI served under `/OpenIDE/ui/` |

Default port **8765**. LAN phone access uses firewall rules + QR; tunnel via
`cloudflared` downloaded into `bin\`.

---

#### 3. HTTP surface - measured

Monolithic `BaseHTTPRequestHandler` in `clipdrop.py` - **no OpenAPI**. Approximately
**275** `if path ==` / `if path.startswith` branches (grep count, not a stable route table).

Host-only prefixes (`clipdrop.py:787-803`) - LAN phone cannot call these without host
session:

```
/api/fs/  /api/terminal/  /api/workspace  /api/git/  /api/agents/
/api/cortex/  /api/workflows  /api/invoke/  /api/openide/
/api/openvault/  /api/openforge/  /api/rag  /api/github
/api/engine  /api/desktop  /api/admin  /api/audit
```

Public / phone-safe surface includes `/api/messages`, `/api/sessions`, `/api/wait`,
`/api/presence`, `/api/qr*`, `/api/hub`, `/api/probe`, `/api/health`.

OpenVault thin client routes (delegate to `openvault_bridge`):

- `/api/openvault/status`, `/ping`, `/mesh`, `/connect-pack`, `/keyvault/*`, `/gate/check`

Cortex-facing routes under `/api/cortex/*`, `/api/engine/*`, `/api/workflows`, RAG under
`/api/rag*`, desktop computer-use under `/api/desktop/*`.

Legacy display names still in code: `/api/openfree/*` (FreeRoute), `/api/hosting*`
(deploy UX - must stay thin vs OpenVault ship).

---

#### 4. Trust boundaries

| Boundary | Enforced by | Bypass / gap |
|---|---|---|
| Keys SoT | should be OpenVault via bridge + `ai_engine` openvault lead | **`env.local` and `DATA_DIR` caches** - second copy if not synced; `ai_engine.py:730` still falls through to direct provider keys |
| Leave-machine gate | `openvault_bridge.gate_check()` -> `POST /api/gate/check` | routes that call providers without gate check are bugs |
| Host-only dangerous ops | `_HOST_ONLY_PREFIXES` + session check in `do_GET`/`do_POST` | misclassified prefix = phone can reach FS/terminal |
| WASM upload inspection | `wasm_gate.js` - **client-side regex redaction stub** | not a sandbox; not Wasm execution |
| Passcode / lockdown | `security.py`, tests in `test_passcode_gate.py` | local app gate, not network authn |
| RAG authority scrub | multiple `test_rag_*` modules | host-only ingest paths |

---

#### 5. Data stores

| Store | Where |
|---|---|
| Runtime data root | `DATA_DIR` - default `D:\AirGPT\data\` (`AIRGPT_DATA_DIR` override) |
| Chat / sessions | SQLite and JSON under `data/` (clipdrop persistence) |
| Markdown vault wings | `data/vault/{project}/rooms/{topic}/` (`vault.py`) |
| OpenVault connect cache | `data/openvault_connect_pack.json` |
| Local env cache | `env.local` at repo root - **offline key cache, not SoT** |
| License | `data/license.json`; optional verify against `control_plane` |
| Binaries | `bin/cloudflared.exe`, tunnel tooling |
| Demo mock tree | `data-demo-mock/` when demo flag set (`config.py:69`) |

All portable with the folder copy. `D:` exFAT constraint: use `npm` not `bun`/`pnpm` in
any frontend subprojects.

---

#### 6. Dependencies + what depends on it

| On | How |
|---|---|
| OpenVault `:5000` | `openvault_bridge`, `/api/openvault/*`, `ai_engine` `_p_openvault` |
| Cortex `:8010` | `/api/cortex/*`, workflows, engine plan/apply, optional computer-use |
| Upstream LLM APIs | direct fallback when OpenVault or keys unavailable |
| `cloudflared` / tunnel providers | phone access without LAN firewall |
| Optional `control_plane :8787` | business license when `AIRGPT_API_BASE` set |

| Depends on AirGPT | How |
|---|---|
| OpenVault mesh | `openide-url` default `http://127.0.0.1:8765` |
| Netie Space | plugin manifest + chat sync |
| Static demo apps | served/hosted from AirGPT apps hub |

**Not the product:** `OpenIDE/research/` (orca, superset monorepos) - research vendored
trees, not the shipped `:8765` shell.

---

#### 7. Shipped vs scaffold - honest

**Shipped and exercised:**

- `clipdrop.py` monolith - chat, clipboard, phone sync, tunnel QR, hub, RAG foundation,
  audit trail, settings, keyvault UI bridge
- `ai_engine.py` multi-provider cascade with OpenVault first
- `openvault_bridge.py` - mesh, connect-pack, gate check, keyvault upsert
- `tests/` - **374 tests collected**; full suite slow (~8+ min). Spot-check:
  `test_passcode_gate` + `test_memory_safety` **68 passed** in 5.6s on 2026-08-03
- Static demo apps in `apps/` (offline-first widgets with `.airgpt/rules.md`)
- `wasm_gate.js` served at `/wasm_gate.js` - client payload inspection

**Scaffold / partial / PLANNED:**

- **`control_plane/`** - optional license FastAPI; personal clients work without it
- **`wasm_gate.js`** - regex redaction stub; **not** a Wasm sandbox (name is misleading)
- **`/api/openforge/*`** - chip design pipeline module; adjacent experiment
- **`online_personal_stub`** string in `/api/info` - hosted AI paywall **PLANNED**
- **`OpenIDE/research/superset`**, **`OpenIDE/research/orca`** - full IDE research
  monorepos; not required to run the host shell
- **`CortexOS/`** tree inside repo - working mirror; not the engine (`D:\Cortex` is)
- **A1 async `/sources` job** - STATUS.md in OpenVault points here as next slice;
  backend not finished while UI owned elsewhere
- **`docs/ACTIVE.md`** - 4-line stub; map not maintained
- **`STATUS.md`** - empty Now/Next/Later; no recorded current priorities in-repo

---

#### 8. Structure problems

1. **`clipdrop.py` is the entire product** - thousands of lines, no router module split;
   grep is the only route index.
2. **Second vault risk** - `env.local` + `ai_engine` direct provider paths coexist with
   OpenVault bridge; PRODUCT_ROLES says cache-only but nothing enforces sync.
3. **Repo clutter beside the five governed files** - `HR.md`, `Interview Resources/`,
   duplicate `control_plane` vs deleted `control-plane/` (README confirms underscore wins).
4. **Remote org mismatch** - only estate repo under `jian-hong/AirGPT`, not `Netie-AI`
   (`NETIE.md` table).
5. **`CLAUDE.md` Hard rules empty** - no recorded invariants despite large attack surface
   (FS, terminal, git, desktop automation).

---

#### 9. Verify

```powershell
cd D:\AirGPT
python -m pytest tests/ -q --ignore=tests/playwright
restart.bat   # or: python clipdrop.py
```

```powershell
### optional license plane
uvicorn control_plane.app:app --host 0.0.0.0 --port 8787
```

Health: `http://127.0.0.1:8765/api/probe`, `http://127.0.0.1:8765/api/health`.

Measured 2026-08-03: prior full run **370 passed, 1 failed** in 459.86s (`374` collected,
`--ignore=tests/playwright`). Single failure:
`tests/test_rag_foundation.py::RagFoundationTests::test_corrective_loop_caps` -
expected `rounds == 1`, got `2`.

No `lint-imports` or mypy gate at repo root - verification is pytest-centric.
