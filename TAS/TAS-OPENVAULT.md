# TAS-OPENVAULT - OpenVault technical architecture

**Plane:** 2 (custody and routing) · **Repo:** `Netie-AI/OpenVault` (public)
**Measured:** 2026-08-27 against clone HEAD `62bb1c7` (GitHub `main`, CI green).
This cloud environment does not vendor OpenVault; measurements are from a throwaway clone under `/tmp/netie-measure/OpenVault`.

---

## 1. What it is

The custody and routing plane: encrypted keys, leave-machine / deploy gate, FreeRoute OpenAI-compatible gateway on the same process as `:5000`, FreeBuild ship adapters, local mesh to Cortex.

**Is not:** an agent loop, OmniRoute, Vercel, or a second Cortex.

---

## 2. Entry points

| Path | Role |
|---|---|
| `OpenMW/` uv app | Custody API `:5000` |
| `apps/web/` Next 16 | UI `:3010`, wired only to `:5000` (DR-0003) |
| `apps/shell/` Electron | Desktop shell |
| `nvme_sentinel/` | NVMe HAL library (own uv root) |
| `Profiler/` | PathTrace library (own uv root) |
| `OpenMW/openmw/openvault/route/` | FreeRoute strategies, breaker, rotator |
| `OpenMW/openmw/openvault/ship/` | Detect / build / host adapters |
| `OpenMW/openmw/openvault/vault/` | Keys, proxy, metering |

---

## 3. Trust boundaries

| Boundary | Enforced by | Note |
|---|---|---|
| Keys | vault store; STATUS still has custody reopen #13 | One vault. `env.local` elsewhere is cache. |
| Leave-machine / deploy | `/api/gate/check`, `ship/gate.py` | HUMAN_STOP on live HT1-HT5 |
| FreeRoute identity | metering: issued `ov_` keys, not spoofable headers | tests in `test_freeroute_metering.py` |
| Circuit breaker | `route/breaker.py` | 408/500/502/503/504 trip |
| Ship honesty | `SHIPPING_MODEL.md`: never report success not observed | Pages adapter real; simulated host is a loud fail |

---

## 4. FreeRoute vs OmniRoute vs NVIDIA (short)

FreeRoute is **OpenVault `:5000/v1`**, not a process on `:20128`. OmniRoute remaining as an external optional.

Shipped strategies on **main** (8): priority, weighted, fill-first, round-robin, p2c, random, least-used, cost-optimized.

This VM patches (not on main, push 403): 15 *sorts* through `cache-optimized`, then 4 *execution shapes* that `apply_strategy` refuses, then `openvault-quota-share.patch`. Portable: `scripts/freeroute_execution.py` (`dispatch_combo`, `hop_call_model`, `hop_serves_listed`, `classify_hop_status`, `sse_wrap_text`, `resolve_relay_handoff`). `/v1` fail-closes nameless fusion; with `combo.models` sequential hop posts classify like the key walk; last hop may SSE; context-relay uses caller available/handoff and persists caller blobs in-process scoped by issued seat (32-blob cap, no Codex fetch). Anthropic-only shape hops return 503 `anthropic chat not via /v1 proxy yet` (no Messages API). No matching hop is 503 `no hop can serve model`. Execution-shape `serves()` is catalog-true (garbage / other-provider ids do not rewrite). Usage names the last hop and copies that hop's `usage` (not OmniRoute parallel quorum-grace). Asking for `parallel` / `quorum_grace` / Codex quota fetch / SQLite persist / autoCombo / token compression / MCP/A2A / `quota-share` is 501, not a silent sequential walk. Product `/v1` `combo.strategy: quota-share` (and PUT `/api/route/strategy`) is 501 `openvault_unported`, not unknown 400. Body `parallel` / sqlite persist / autoCombo / compress / MCP/A2A / quota-fetch are the same 501. Hop posts drop `combo` / `skill_body` / `transcript`; sidecar `metadata` / `extra` bags with those keys are 400 and stripped from the hop. `/v1` with a Crew body is 400 `openvault_crew_body`. `model: auto` stays catalog pick. Strategy+shape+chat tests **145 passed**.

Not shipped vs OmniRoute: provider catalog at OmniRoute scale, Electron Next-on-20128. Asking for MCP/A2A / token compression / autoCombo / quorum-grace / Codex quota fetch / SQLite persist / `quota-share` is a named 501.

Not the same job as NVIDIA llm-router (trained task/complexity classifier on Triton; deprecated for NeMo Switchyard). Portable `scripts/switchyard_honesty.py`: host Switchyard behind OpenVault leave-machine; `host_switchyard(ov=)` POSTs `/api/crew/gate` with skill ids; refuse vendoring `llm-router`; refuse rewriting Triton; refuse claiming FreeRoute is Switchyard. Score stays **2 / 10**.

---

## 5. FreeBuild vs Vercel (short)

Design: user machine builds, user cloud hosts, OpenVault is the button. Cloudflare Pages via wrangler is the first real adapter. STATUS: no live box has completed HT1. This is not a Vercel replacement until HT1 is green on a stranger's token. Product patch `docs/patches/openvault-ship-netie.patch`: live labels go through `claim_deploy` / `netie.route.report_deploy` when Netie is installed. Follow-on `openvault-ship-claim-ov.patch`: `claim_deploy(ov=)` POSTs skill ids; the engine and `/api/ship/engine` forward that gate when `parent_run_id` is on the body. HT1 is still not done. Score stays **2 / 10**.

---

## 6. Data stores

Vault SQLite (sealed), optional Redis for FreeRoute buckets, `openvault.local.json`. Master-key plaintext backup is a named DR (DR-0010) - treat as dangerous.

---

## 7. Shipped vs scaffold

**Shipped enough to test:** vault, gate refuse paths, FreeRoute metering/tests, 8 sorts on `main` (9th-15th sorts plus 4 execution-shape contracts in `docs/patches/`, 77 tests passed here, push 403), Pages adapter code, Next UI, Electron shell, NVMe library, CI.

**Local evidence 2026-08-27** (clone HEAD `3030cad`, this VM):

- `uv run pytest tests -q` after replacing D:\\ tree skips with tmp_path fixtures -> **840 passed, 4 skipped** (Windows DPAPI only)
- Push of that patch to `Netie-AI/OpenVault` returned **403** (cursor[bot] cannot write sibling repos). Patch lives on local clone branch `cursor/detect-stacks-no-skip-ca9b` until a token with OpenVault write lands it.

**Not shipped as a buyer claim:** live deploy (HT1), pricing, "better than Vercel", OmniRoute-complete routing, NVMe product as the thing we sell (library, not the SKU).

STATUS.md 2026-08-25: **~75%**, HUMAN_STOP on #18.

---

## 8. Verify (in the OpenVault repo, not here)

```bash
uv sync && uv run ruff check . && uv run pytest tests/unit tests/integration -q
cd OpenMW && uv sync && uv run pytest tests -q --cov=openmw.openvault --cov-fail-under=75
```

**GitHub CI on default `main`:** last push (docs/status #45, 2026-08-27 15:12 UTC) **success**. `POST /api/crew/gate` is **not** on main (OpenVault PR #44 plus focused `docs/patches/openvault-crew-gate.patch`: unknown `skill` kind refuses, no skill body). HT1-HT5 HUMAN_STOP. STATUS ~78%.

---

## Appendix - checkout-measured map (2026-08-03, from PR #1)

Kept on merge so the checkout-measured detail is not lost. Main body above is newer; where they disagree, the body wins until re-measured.

### TAS-OPENVAULT - OpenVault technical architecture

**Plane:** 2 (custody and routing) · **Repo:** `Netie-AI/OpenVault` · `D:\OpenVault`
**Measured:** 2026-08-03. OpenAPI path count obtained by **importing the app**, not by
reading route tables.

**Tier 4 map:** purpose · plane · surface · dependencies · stores · trust · shipped vs
scaffold · verify

---

#### 1. What it is

**One line:** single custody and routing plane - encrypted vault, FreeRoute proxy,
leave-machine gate, local mesh, FreeBuild ship/deploy.

The single custody and routing plane: encrypted key vault, password/card secrets,
FreeRoute model proxy (`/v1/chat/completions`), leave-machine and deploy gate, local
mesh into Cortex and FreeIDE, and FreeBuild ship/deploy. NVMe Sentinel and Profiler
measurement libraries live beside the app but are adjacent hardware tooling, not the
product story.

**It is not an agent loop.** It never decides what work to do. It answers where, with
what key, and whether-allowed. See `PRODUCT_ROLES.md` and `NETIE.md` section 2.

---

#### 2. Entry points

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

#### 3. HTTP surface - measured

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

#### 4. Trust boundaries

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

#### 5. Data stores

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

#### 6. Dependencies + what depends on it

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

#### 7. Shipped vs scaffold - honest

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

#### 8. Structure problems

1. **CI covers `nvme_sentinel` only** - `OpenMW` and `apps/web` have no workflow job;
   clone-and-verify in STATUS.md is manual.
2. **Three `uv sync` roots** (repo root, `OpenMW/`, `Profiler/`) - easy to test the
   wrong tree.
3. **Vendor trees** (`vendor/clicky`, etc.) pollute greps; `bin/` is a quarantine pile.
4. **Wire identifiers deliberately frozen** - `openship`, `OPENVAULT_HOME`, `X-OpenVault-Reveal`
   coexist with Free* display names; grepping one spelling undercounts.
5. **`docs/ACTIVE.md` Cortex URL says `:8000`** while mesh default and DMS smoke use `:8010`.

---

#### 9. Verify

```bash
### nvme_sentinel (repo root)
uv sync && uv run pytest tests/ -q
uv run mypy nvme_sentinel tests

### OpenMW custody API
cd OpenMW && uv sync && uv run pytest tests/ -q

### Operator stack
python apps/cli/openvault_cli.py doctor
python apps/cli/openvault_cli.py demo   # mock-health API + :3010 UI

### Profiler
cd Profiler && uv sync && uv run pytest tests/ -q
```

Measured 2026-08-03:

- `nvme_sentinel`: **97 passed, 6 skipped** (real NVMe tests skipped)
- `OpenMW`: **563 passed** in ~322s

Windows note: use `uv run openmw console`, not raw `python -m importlinter.cli` patterns
from other repos.
