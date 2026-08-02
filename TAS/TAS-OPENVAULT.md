# TAS-OPENVAULT - OpenVault technical architecture

**Plane:** 2 (custody and routing) · **Repo:** `Netie-AI/OpenVault` · `D:\OpenVault`
**Measured:** 2026-08-03. OpenAPI path count obtained by **importing the app**, not by
reading route tables.

---

## 1. What it is

The single custody and routing plane: encrypted key vault, password/card secrets,
FreeRoute model proxy (`/v1/chat/completions`), leave-machine and deploy gate, local
mesh into Cortex and FreeIDE, and FreeBuild ship/deploy. NVMe Sentinel and Profiler
measurement libraries live beside the app but are adjacent hardware tooling, not the
product story.

**It is not an agent loop.** It never decides what work to do. It answers where, with
what key, and whether-allowed. See `PRODUCT_ROLES.md` and `NETIE.md` section 2.

---

## 2. Entry points

| Path | Role |
|---|---|
| `OpenMW/openmw/openvault/app.py` | `create_app()` - FastAPI custody API |
| `OpenMW/openmw/cli.py:165` | `console_cmd` - `uv run openmw console --port 5000` |
| `apps/cli/openvault_cli.py` | `openvault up` / `demo` / `app` / `doctor` - starts API + UI |
| `apps/web/package.json` | Next 16 UI on `:3010` (`next dev --port 3010`) |
| `apps/shell/package.json` | Electron shell wrapping API + web |
| `scripts/windows/Start-OpenVaultDemo.ps1` | Operator demo launcher |
| `nvme_sentinel/cli.py` | `nvme-sentinel` CLI - separate `uv sync` root |
| `Profiler/` | PathTrace probe - separate `uv sync` root |
| `OpenMW/rust/openvault-console/` | Optional Rust auth on `:5055` - skipped when `cargo` missing |

`:5000/` redirects humans to `OPENVAULT_APP_URL` (default `http://127.0.0.1:3010/`).
Real UI is `apps/web`; mesh UI at `http://127.0.0.1:3010/peers`.

---

## 3. HTTP surface - measured

| Surface | Paths |
|---|---|
| OpenMW custody API (`create_app`) | **122** |

```powershell
cd D:\OpenVault\OpenMW
uv run python -c "from openmw.openvault.app import create_app; print(len(create_app().openapi()['paths']))"
```

Prefix groups (from OpenAPI): `/api/ship` (22) · `/api/cloud` (9) · `/api/keys` (8) ·
`/api/deploy` (8) · `/api/sentinel` (7) · `/api/secrets` (7) · `/api/local` (6) ·
`/api/route` (5) · `/api/accounts` (5) · `/api/providers` (5) · `/api/freebuild` (4) ·
`/api/access` (3) · `/api/cortex` (3) · `/v1/chat/completions` (1) · `/keys/*` JWKS/root
· `/api/gate/check` · `/api/freeroute/ratelimit`.

Hidden aliases remain for shipped clients: `/api/openide/*` mirrors `/api/freeide/*`
(`include_in_schema=False`). Old paths pinned by `OpenMW/tests/test_access_routing.py`.

---

## 4. Trust boundaries

| Boundary | Enforced by | Bypass / gap |
|---|---|---|
| Key custody SoT | `vault/store.py` + `keys.db` under `~/.openvault` | **`env.local` / `user.env` elsewhere are caches, not a second vault** - but unsynced copies are a drift risk |
| Secret reveal | loopback + intent gate + audit (`vault/secrets.py`, DR-0005) | closed for mutation routes; **master key has no KDF/DPAPI wrap** |
| Leave-machine / deploy gate | `ship/gate.py` `check_gate()` via `POST /api/gate/check` | Cortex/AirGPT/FreeIDE must call; callers that skip are bugs |
| FreeRoute proxy | `vault/proxy.py` + `POST /v1/chat/completions` | upstream providers see OpenVault keys, not app keys |
| Access resolve (no content) | `route/access.py` `POST /api/access/resolve` | returns location + verdict, **never memory rows** |
| Mesh handshake | `mesh/local_mesh.py` | `/api/access/resolve` reports **last probe**, not live - `POST /api/local/mesh/refresh` on demand |
| GitHub PAT custody | `ship/github_auth.py` | **PAT bypasses the vault** - tracked open in DR-0005 |
| NVMe measurement | `nvme_sentinel` HAL + hostile corpus tests | hardware tests need `NVME_SENTINEL_REAL_DEVICE=1` |

---

## 5. Data stores

| Store | Where |
|---|---|
| Vault home | `~/.openvault` (`OPENVAULT_HOME` override) - `paths.py:10` |
| Encrypted keys + secrets | `keys.db` + `master.key` in vault home |
| Orchestration prefs | `orchestration.json`, `fallback.json` in vault home |
| Ship clones / GitHub PAT | `OPENVAULT_HOME/clones`, `OPENVAULT_HOME/github/` |
| Cloud multiplayer v0 | in-memory + JSON under `OPENVAULT_HOME` |
| Sentinel snapshots | optional persist under `OPENVAULT_HOME` |
| Profiler / observe timings | `last_admin_timings.json` fused into observe path |

Runtime state is per-machine. Copying `master.key` + `keys.db` to another user scope
does not decrypt (DPAPI user scope on Windows - `vault/crypto.py`).

---

## 6. Dependencies + what depends on it

| On | How |
|---|---|
| Cortex `:8010` (typical) | `mesh/cortex_client.py`, deploy-from-cortex, mesh probe |
| FreeIDE `:8765` (typical) | mesh `openide_invoke`, handshake connect-pack |
| Upstream model APIs | FreeRoute proxy fans out to OpenAI-compat providers |
| `nvme_sentinel` + `Profiler` | bound into app via `sentinel/` tier |

| Depends on OpenVault | How |
|---|---|
| DMS | `POST /keys/services` + `/keys/intermediate` for Ed25519 manifest signing |
| AirGPT | `openvault_bridge`, `/api/openvault/*`, `ai_engine` cascade lead provider |
| Pointer | vision/LLM via `:5000` - no local API keys |
| Netie Space | `OpenVaultKeySync` for key sync |
| Cortex | FreeRoute client path for litellm default |

---

## 7. Shipped vs scaffold - honest

**Shipped and exercised:**

- FastAPI custody API with 122 measured routes and 563 OpenMW pytest passes
- Encrypted key vault, secrets (passwords/cards), reveal gate, JWKS signing keys
- `POST /v1/chat/completions` FreeRoute proxy with provider registry and rate limits
- `POST /api/gate/check` leave/deploy gate
- FreeBuild ship engine (`/api/ship/*`, `/api/freebuild/*`, `/api/deploy/*`)
- Local mesh, handshake, connect-pack, slots
- NVMe Sentinel library - 97 pytest passes (6 skipped without real device)
- Next UI `apps/web` on `:3010` wired to `:5000` only (DR-0003)

**Scaffold / partial / PLANNED:**

- **Q2 in-memory Q0+Q1 kill-and-send** - blocked (STATUS.md, `DESIGN_TIERED_QUEUE_LB.md`)
- **Streaming reserve/refund** - does not refund when upstream sends `stream_options.include_usage`
- **Rust console `:5055`** - optional; skipped when `cargo` missing
- **Cloud tier** - v0 in-memory multiplayer + JSON persistence, not production LAN cloud
- **apps/shell** Electron - exists; verify is manual, no CI job
- **Master-key KDF, unseal/lock state** - open per DR-0005, no confirming test
- **C2 `POST /api/keys/ingest`** - gated until AirGPT client lands (STATUS.md)

---

## 8. Structure problems

1. **CI covers `nvme_sentinel` only** - `OpenMW` and `apps/web` have no workflow job;
   clone-and-verify in STATUS.md is manual.
2. **Three `uv sync` roots** (repo root, `OpenMW/`, `Profiler/`) - easy to test the
   wrong tree.
3. **Vendor trees** (`vendor/clicky`, etc.) pollute greps; `bin/` is a quarantine pile.
4. **Wire identifiers deliberately frozen** - `openship`, `OPENVAULT_HOME`, `X-OpenVault-Reveal`
   coexist with Free* display names; grepping one spelling undercounts.
5. **`docs/ACTIVE.md` Cortex URL says `:8000`** while mesh default and DMS smoke use `:8010`.

---

## 9. Verify

```bash
# nvme_sentinel (repo root)
uv sync && uv run pytest tests/ -q
uv run mypy nvme_sentinel tests

# OpenMW custody API
cd OpenMW && uv sync && uv run pytest tests/ -q

# Operator stack
python apps/cli/openvault_cli.py doctor
python apps/cli/openvault_cli.py demo   # mock-health API + :3010 UI

# Profiler
cd Profiler && uv sync && uv run pytest tests/ -q
```

Measured 2026-08-03:

- `nvme_sentinel`: **97 passed, 6 skipped** (real NVMe tests skipped)
- `OpenMW`: **563 passed** in ~322s

Windows note: use `uv run openmw console`, not raw `python -m importlinter.cli` patterns
from other repos.
