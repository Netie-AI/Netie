# TAS-AIRGPT - AirGPT technical architecture

**Plane:** 4 (application / host shell) · **Repo:** `jian-hong/AirGPT` · `D:\AirGPT`
**Measured:** 2026-08-03. Route surface counted from `clipdrop.py` path handlers; tests
collected without running the full 371-test suite (subset verified).

---

## 1. What it is

A local-first Windows host shell: clipboard capture, chat, phone-to-PC sync, settings,
pairing QR/tunnel, apps hub, RAG spaces, and thin clients over OpenVault (keys, gate,
mesh) and Cortex (brains, workflows, computer-use). Ships as a portable tree beside
`data\` - copy the folder, install Python once, run `restart.bat`.

**It is not a second key vault and not a second orchestrator.** Custody and leave-machine
decisions belong to OpenVault; architecture presets and agent loops belong to Cortex.
See `PRODUCT_ROLES.md` (copied in-repo).

---

## 2. Entry points

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

## 3. HTTP surface - measured

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

## 4. Trust boundaries

| Boundary | Enforced by | Bypass / gap |
|---|---|---|
| Keys SoT | should be OpenVault via bridge + `ai_engine` openvault lead | **`env.local` and `DATA_DIR` caches** - second copy if not synced; `ai_engine.py:730` still falls through to direct provider keys |
| Leave-machine gate | `openvault_bridge.gate_check()` -> `POST /api/gate/check` | routes that call providers without gate check are bugs |
| Host-only dangerous ops | `_HOST_ONLY_PREFIXES` + session check in `do_GET`/`do_POST` | misclassified prefix = phone can reach FS/terminal |
| WASM upload inspection | `wasm_gate.js` - **client-side regex redaction stub** | not a sandbox; not Wasm execution |
| Passcode / lockdown | `security.py`, tests in `test_passcode_gate.py` | local app gate, not network authn |
| RAG authority scrub | multiple `test_rag_*` modules | host-only ingest paths |

---

## 5. Data stores

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

## 6. Dependencies + what depends on it

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

## 7. Shipped vs scaffold - honest

**Shipped and exercised:**

- `clipdrop.py` monolith - chat, clipboard, phone sync, tunnel QR, hub, RAG foundation,
  audit trail, settings, keyvault UI bridge
- `ai_engine.py` multi-provider cascade with OpenVault first
- `openvault_bridge.py` - mesh, connect-pack, gate check, keyvault upsert
- `tests/` - **371 tests collected**; subset `test_passcode_gate` + `test_memory_safety`
  **68 passed** in 5.6s on 2026-08-03
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

## 8. Structure problems

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

## 9. Verify

```powershell
cd D:\AirGPT
python -m pytest tests/ -q --ignore=tests/playwright
restart.bat   # or: python clipdrop.py
```

```powershell
# optional license plane
uvicorn control_plane.app:app --host 0.0.0.0 --port 8787
```

Health: `http://127.0.0.1:8765/api/probe`, `http://127.0.0.1:8765/api/health`.

Measured 2026-08-03: **370 passed, 1 failed** in 459.86s (`371` collected,
`--ignore=tests/playwright`). Single failure:
`tests/test_rag_foundation.py::RagFoundationTests::test_corrective_loop_caps` -
expected `rounds == 1`, got `2`.

No `lint-imports` or mypy gate at repo root - verification is pytest-centric.
