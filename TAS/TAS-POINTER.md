# TAS-POINTER - Pointer technical architecture

**Plane:** 4 (computer control) · **Repo:** `Netie-AI/Pointer` (public clone; push 403)
**Measured:** 2026-08-28 HEAD `8c0e6c2`. Tray exists. UACC catalog names planner/clipboard/windows; native observe still publishes uncropped PNG. Additive `guard_observe` is opt-in. Score in `TAS/ESTATE-GAP.md`.

---

## 1. What it is

The hands and eyes: an Electron tray client that sees a screen region, takes an instruction, and executes clicks/types as a coworker rather than a macro. Holds no keys. Trusts nothing on screen. Sends intents to Cortex and executes what comes back, fail-closed.

**Is not:** a second orchestrator, UACC itself, Perplexity Computer, or a billing bypass into Cursor/Claude Code.

---

## 2. Entry points (founder inventory)

| Claim | Status |
|---|---|
| Electron tray, Ctrl+Space, crop a region, instruct | founder table; not cloned |
| ~216 files, 120 JS/TS | founder table |
| Was NetieClicks / `jian-hong/NetieClicks` | `NETIE.md` |
| Founder: "not working as expected" | treat as broken until HEAD is green |

---

## 3. vs Perplexity Computer and UACC

| Analogue | License | Job | Pointer |
|---|---|---|---|
| Perplexity Computer | closed | hosted computer-use agent | not a host; local tray |
| `uacc` (PyPI, MCP, ~68 tools) | open MCP server | pixel/a11y desktop tools for any agent | should be *optional hands* behind Cortex `tool_runner`, not a second brain |
| `e2b-dev/open-computer-use` | Apache-2.0 | sandboxed desktop | different threat model (cloud VM vs operator laptop) |

Fail-closed click contract in this repo: `scripts/pointer_click.py`. Unlabeled or unknown-role elements do not click. Password / OTP / cookie fields do not click even when labeled. No Cortex intent, no click. The file does not mention API keys or `os.environ`. Product copy: `docs/patches/pointer-netie-hands.patch`.

MCP wrap of UACC 1.1.0's **68** public tool names: `scripts/pointer_hands.py`. Cortex must allow the name. Planner / workflow / memory / `get_action_history` / clipboard / `browser_execute_js` / ungated `open_url` refuse. `invoke_hand(ov=)` POSTs `/api/crew/gate` with skill ids; boolean `ov_leave` stays the stand-in. Screenshot / snapshot / screen-diff / `detect_elements_visual` / `get_screen_info` / `get_screen_info_enhanced` / `vlm_locate_element` need a labeled non-secret crop (`screenshot_uncropped` otherwise). `browser_get_page_info`, `list_processes`, `get_system_info`, `list_windows`, and `get_active_window` refuse. Hover/drag/`wait_for_element` reuse fail-closed click. `hotkey` / `scroll` / `paint_image` / `paint_preset` on a password/OTP field refuse (uncropped paint refuses). `acknowledge_user_override` / `set_kill_distance` refuse (UACC safety is not a second Cortex). `bind_computer` refuses e2b / Perplexity Computer / open-computer-use (local tray, not a hosted computer). Native `computer.observe` stays DR-0005. Opt-in Cortex path: `scripts/pointer_observe.py` `guard_observe` (product `governed: true`). We do not import `uacc`. `python3 scripts/test_pointer_click.py`, `python3 scripts/test_pointer_hands.py`, and `python3 scripts/test_pointer_observe.py`. Not a UACC clone.

---

## 4. Trust boundaries (constitution)

| Boundary | Required | Verified on HEAD |
|---|---|---|
| No keys in the tray | yes | UNVERIFIABLE |
| Cortex decides the intent | yes | UNVERIFIABLE |
| Fail closed on ambiguous UI | yes | UNVERIFIABLE |
| Leave-machine via OpenVault | yes | UNVERIFIABLE |

---

## 5. Verify

```
NEEDS-YOU TAS-POINTER  add Netie-AI/Pointer to this environment
```

Then: a tool-for-tool matrix against UACC, a fail-closed test (refuse to click unlabeled), and a proof the tray never reads `env.local`.

---

## Appendix - checkout-measured map (2026-08-03, from PR #1)

Kept on merge so the checkout-measured detail is not lost. Main body above is newer; where they disagree, the body wins until re-measured.

### TAS-POINTER - Pointer technical architecture

**Plane:** 4 (application / computer control) · **Repo:** `Netie-AI/Pointer` · `D:\Pointer`
**Measured:** 2026-08-03. Tests run locally; HTTP surfaces are outbound clients only
(no server in this repo). `npm test` sums **147 passed** across 17 unit suites.

**Tier 4 map:** purpose · plane · surface · dependencies · stores · trust · shipped vs
scaffold · verify

---

#### 1. What it is

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

#### 2. Entry points

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

#### 3. HTTP surface - measured

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

#### 4. Trust boundaries

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

#### 5. Data stores

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

#### 6. Dependencies + what depends on it

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

#### 7. Shipped vs scaffold - honest

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

#### 8. Structure problems

1. **No CI workflow** in repo - 147 unit tests exist but nothing runs them on push.
2. **Rename incomplete** - Pointer repo / package vs NetieClicks AppData confuses cross-repo docs.
3. **Hard dependency on two live peers** - without Cortex + OpenVault the app fails closed
   (correct) but reads as broken AI to users.
4. **`docs/` plan pile** - `ACTIVE_PLAN.md`, `MEMORY_DESIGN.md`, etc. beside five-file law;
   not the governed state surface.
5. **Old git remote** - `old-netieclicks` kept locally after move from `jian-hong/NetieClicks`
   (`NETIE.md`).

---

#### 9. Verify

```powershell
### Unit suites (fast)
cd D:\Pointer
npm test

### Full agentic pack (slow - needs peers for strict acceptance)
npm run test:agentic-pack

### Manual stack (from README)
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

---

## Appendix - Pointer bootstrap daemon in this repo (2026-08-22, from PR #3)

Describes the `Pointer/` bootstrap daemon this checkout carries, not the product repo. Main body above is newer.


**Plane:** 4 (application) · **Repo:** bootstrap in `Netie-AI/Netie` `Pointer/`
**Product remote (unreachable here):** `Netie-AI/Pointer` · `D:\Pointer`
**Measured:** 2026-08-22, by running the bootstrap on this cloud VM (`DISPLAY=:1`).

This file describes the **bootstrap daemon this checkout can run**. It does not
pretend to be the Electron HUD in the private product repo.

---

#### 1. What it is

A localhost client that lets Cortex (or an explicit local test) act on a real
desktop: screenshot, mouse, type, sandbox files, kill switch, hash-chained ledger.

**It is not an orchestrator.** It does not choose what work to do. Cortex does.
OpenClaw and Hermes are not part of this process.

---

#### 2. Entry points

| Path | Role |
|---|---|
| `Pointer/pointer/server.py` | `ThreadingHTTPServer` on `127.0.0.1:7420` |
| `Pointer/pointer/__main__.py` | `serve`, `verify`, `live-click`, `prove`, `pair --card` |
| `Pointer/scripts/verify.sh` | unit tests + live mouse/screenshot |
| `Pointer/scripts/install_windows.ps1` | laptop start + prove + pair card |

---

#### 3. HTTP surface - measured from code

| Method | Path | Auth |
|---|---|---|
| GET | `/` | none (laptop next steps, no tokens) |
| GET | `/health`, `/healthz` | none |
| GET | `/pay` | none (live Stripe HTML) |
| GET | `/pay/pointer-rm300.png` | none (QR of Pointer RM 300 link) |
| GET | `/v1/status` | none (loopback; `pair_ready` boolean, no tokens) |
| POST | `/v1/intent` | pair token if `source=remote-paired` |
| POST | `/v1/kill` | none (loopback kill is intentional) |
| POST | `/v1/unkill` | pair token |

Non-loopback bind is refused unless `POINTER_ALLOW_REMOTE=1`.

---

#### 4. Trust boundaries

| Boundary | Enforced by | Bypass |
|---|---|---|
| Cortex required for act | `gate.py` | explicit `source=local-test` or `allow_local_act`, always listed in `degraded` |
| Irreversible act | approval token | none in code |
| `shell` | engine always refuses | none |
| File IO | name-only path under `.pointer-state/sandbox` | none; `../x` collapses to sandbox/`x` |
| Remote act | pair token + approval token | none |
| Kill switch | `.pointer-state/KILL` | `POST /v1/unkill` with pair token |

---

#### 5. Executor backends

| OS | Mouse | Type | Screenshot |
|---|---|---|---|
| Linux | `xdotool` (measured working on this VM) | `xdotool type` | `ffmpeg -f x11grab` (measured PNG) |
| Windows | `ctypes.windll.user32` SetCursorPos / mouse_event | `SendInput` unicode + VK hotkeys (`pointer/windows_input.py`, unit-tested) | PowerShell `CopyFromScreen` |

Display on this VM: `:1`, `1920x1200`.

---

#### 6. What this TAS does not cover

The private product at `Netie-AI/Pointer` (Word coworker, 60s recall ring, Electron HUD,
Clicky). This token cannot clone it. Do not claim the bootstrap is that app.

---

#### 7. Org-clone evidence (measured 2026-08-22)

This cloud token can list org repos: Vertex, AIM, OpenHBM, CI-Doctor, OpenForge,
OpenVault, AnalogCrawler, Cassandra, VKing, Netie. `Netie-AI/Pointer` and
`Netie-AI/Cortex` remain GitHub 404.

Cloneable vault: https://github.com/Netie-AI/OpenVault

| Peer | OpenVault mesh (clone) | This meta repo TAS | Pointer gate |
|---|---|---|---|
| OpenVault | `:5000` `/api/healthz` | not a Pointer TAS | probe only (`OPENVAULT_URL`) |
| Cortex | `:8000` `/health` | TAS-CORTEX uvicorn `:8010` | `CORTEX_URL` default `:8010` |
| Pointer | not in OpenVault mesh pack | this file, `:7420` | listen loopback |

Pointer `python -m pointer mesh` probes both Cortex URLs independently.
`silent_port_remap` is always false. If the laptop runs Cortex the OpenVault way,
set `CORTEX_URL=http://127.0.0.1:8000` before `pointer serve`.

`POST /api/engine/auto` on Cortex is `race_router.auto_route`, not Pointer ingest.
Pointer `submit_intent` returns None and does not POST `pointer.intent/v1` there.
Cortex reaches Pointer via `POST /v1/intent` on `:7420`.

Gemini keys: OpenVault provider id `google`, env `GOOGLE_API_KEY`, register
https://aistudio.google.com/apikey . Pointer must not grow a second vault.
