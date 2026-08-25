# TAS-POINTER - Pointer technical architecture

**Plane:** 4 (application / computer control) · **Repo:** `Netie-AI/Pointer` · `D:\Pointer`
**Measured:** 2026-08-03. Tests run locally; HTTP surfaces are outbound clients only
(no server in this repo). `npm test` sums **147 passed** across 17 unit suites.

**Tier 4 map:** purpose · plane · surface · dependencies · stores · trust · shipped vs
scaffold · verify

---

## 1. What it is

**One line:** Windows Electron buddy - region capture, governed plan, human-confirmed
clicks/types - hands and eyes for the estate, not a second orchestrator.

A Windows Electron desktop buddy: Ctrl+` arms a session, drag a rectangle for region
capture, ask or act on what is on screen with bubbles + subtitles hidden from screen
capture. Pointer is the estate's "hands and eyes" - it sees the desktop, plans through
governed peers, and executes clicks/types after human confirmation.

**It is not a second orchestrator.** Intents go to Cortex for secure/classify/audit;
vision and LLM calls go to OpenVault so Pointer never holds provider API keys. Package
name `netie-pointer`; user-facing folder still `%APPDATA%\NetieClicks` (rename lag).

---

## 2. Entry points

| Path | Role |
|---|---|
| `package.json` | `npm start` -> `electron electron/main.js` |
| `electron/main.js` | Electron main - tray, hotkey, capture, HUD, IPC |
| `electron/hud.html` + `hud.js` | Center chat HUD + frame drag UI |
| `electron/netie/ecosystem.js` | Cortex + OpenVault client (injectable fetch for tests) |
| `electron/netie/driver.js` | Input execution (click, type, scroll, launch) |
| `electron/netie/brain.js` | Personal encrypted brain + fleet telemetry queue |
| `scripts/netie-launch.ps1` | Stack launcher with Cortex + OpenVault |
| `scripts/install-desktop-icons.ps1` | Desktop shortcut install |

Requires **Cortex `:8010`** (pack dms for `/dms/*` routes) and **OpenVault `:5000`**
for vision/LLM proxy. README still references `D:\Netie Clicks` path alias.

---

## 3. HTTP surface - measured

**No inbound HTTP server.** Outbound calls only:

| Peer | Endpoints used | Role |
|---|---|---|
| Cortex `:8010` | `POST /dms/secure` | pre-LLM injection/PII gate - **fail-closed** |
| Cortex `:8010` | `POST /dms/classify` | intent classification |
| Cortex `:8010` | `POST /dms/audit/append` | hash-chained action log |
| Cortex `:8010` | `POST /dms/agents/computer-use` | governed planner when `NETIE_CU_PLANNER=1` |
| OpenVault `:5000` | OpenAI-shaped chat + vision | keys and provider failover owned by OV |

Default Cortex key: `dms-demo-steward-key` unless `NETIE_CORTEX_KEY` set or
`NETIE_CORTEX_DEMO_KEY=0` (`ecosystem.js:58-60`).

---

## 4. Trust boundaries

| Boundary | Enforced by |
|---|---|
| Screen bytes untrusted | every LLM path through `POST /dms/secure` first |
| Planner cannot self-approve | `PLANNER_FIELDS` whitelist strips `_approved`, `_custody`, etc. |
| Action allowlist | `plan-guard.test.js` - unknown verbs dropped |
| Human confirmation | `safety.js` `reviewPlan` - open/navigate always need a beat |
| Secret / irreversible policy | wins over auto-run guard |
| Credential custody | OpenVault templates via `vault-fill.js` - Pointer does not store API keys |
| Privacy veil | `privacy-veil.js` - HUD hidden from capture |
| Personal brain encryption | `crypto/vault` dual-envelope on device |
| Fleet telemetry | encrypted queue to Cortex `/v1/telemetry` - consent-gated |

| Gap | Status |
|---|---|
| Cortex CU planner | **OFF by default** - `NETIE_CU_PLANNER=1` required; OpenVault fallback planner is live path |
| UIA targeting | optional PowerShell probe; 3 failures -> vision fallback |
| Redis hot memory | optional; defaults to **60s in-process ring** |

---

## 5. Data stores

| Store | Location |
|---|---|
| App data root | `%APPDATA%\NetieClicks\` |
| Encrypted personal brain | vault envelope under data root (`brain.js` + `crypto/vault`) |
| Conversations | `%APPDATA%\NetieClicks\conversations\` - markdown per session |
| Settings | `%APPDATA%\NetieClicks\settings.json` |
| Device id | `%APPDATA%\NetieClicks\device.json` |
| Hot memory ring | in-process 60s ticks; optional Redis ZSET via `OPENVAULT_REDIS_URL` |
| Demo debug shots | `%APPDATA%\NetieClicks\demo-debug\shots` when enabled |
| Recall / memory import | `recall/` subtree under data root |

No cloud SoT - fleet learning uploads encrypted envelopes to Cortex telemetry only.

---

## 6. Dependencies + what depends on it

| On | How |
|---|---|
| Cortex `:8010` | secure gate, classify, audit, optional computer-use planner |
| OpenVault `:5000` | vision + chat completions - no local provider keys |
| Electron 35 | desktop shell, `desktopCapturer`, global shortcuts |
| PowerShell | UIA probes, optional STT bridge scripts |
| Optional `ioredis` | hot memory when `OPENVAULT_REDIS_URL` set |
| Optional Playwright | acceptance tests only (`devDependencies`) |

| Depends on Pointer | How |
|---|---|
| Netie stack demos | README positions Pointer beside Space + Cortex + OpenVault |
| OpenVault vendor | `D:\OpenVault\vendor\clicky` cited as MIT Clicky reference |

Pointer does not depend on AirGPT or DMS directly.

---

## 7. Shipped vs scaffold - honest

**Shipped and exercised:**

- Electron HUD + frame drag + capture-hidden stage
- Full act loop: secure -> classify -> plan (OpenVault vision) -> plan-guard -> driver
- Recipes, skills expansion, enquire panel, vault template fill, privacy veil
- Personal brain encrypt + fleet telemetry queue with consent defaults ON
- Conversation save to markdown; folder/Space hooks for Explorer integration
- **147 unit tests passed** across 17 suites via `npm test` on 2026-08-03
- Acceptance pack: `npm run test:acceptance` (optional strict HUD/CU flags)

**Scaffold / partial / PLANNED:**

- **`NETIE_CU_PLANNER`** - **PLANNED** primary planner on Cortex
  `/dms/agents/computer-use`; off until explicitly enabled
- **Redis hot memory** - optional; unset URL -> in-process ring only (`hotMemory.js`)
- **`STATUS.md` / `docs/ACTIVE.md`** - empty stubs; no in-repo current priorities
- **`CLAUDE.md` Hard rules** - "None recorded yet"
- **Package vs folder naming** - `netie-pointer` package, `NetieClicks` AppData path,
  README alias `D:\Netie Clicks`
- **Coworker code-gen path** - regex detects "scaffold/build app" intents; not a shipped
  app builder integration

---

## 8. Structure problems

1. **No CI workflow** in repo - 147 unit tests exist but nothing runs them on push.
2. **Rename incomplete** - Pointer repo / package vs NetieClicks AppData confuses cross-repo docs.
3. **Hard dependency on two live peers** - without Cortex + OpenVault the app fails closed
   (correct) but reads as broken AI to users.
4. **`docs/` plan pile** - `ACTIVE_PLAN.md`, `MEMORY_DESIGN.md`, etc. beside five-file law;
   not the governed state surface.
5. **Old git remote** - `old-netieclicks` kept locally after move from `jian-hong/NetieClicks`
   (`NETIE.md`).

---

## 9. Verify

```powershell
# Unit suites (fast)
cd D:\Pointer
npm test

# Full agentic pack (slow - needs peers for strict acceptance)
npm run test:agentic-pack

# Manual stack (from README)
powershell -File D:\Cortex\scripts\start_cortex_engine.ps1 -Port 8010 -Pack dms
cd D:\OpenVault\OpenMW
$env:CORTEX_URL = "http://127.0.0.1:8010"
uv run openmw console --host 127.0.0.1 --port 5000 --cortex-url http://127.0.0.1:8010 --no-open-browser
cd D:\Pointer
npm start
```

Dry-run (no real clicks): `$env:NETIE_CLICK_DRY_RUN=1; npm start`

Measured 2026-08-03: **`npm test` -> 147 passed, 0 failed** across bundled unit suites.

Health checks when stack is up: `http://127.0.0.1:8010/health`, OpenVault `:5000/api/healthz`,
`POST /dms/secure` with steward key.
