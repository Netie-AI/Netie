# TAS-POINTER - Pointer technical architecture

**Plane:** 4 (application) · **Repo:** bootstrap in `Netie-AI/Netie` `Pointer/`
**Product remote (unreachable here):** `Netie-AI/Pointer` · `D:\Pointer`
**Measured:** 2026-08-22, by running the bootstrap on this cloud VM (`DISPLAY=:1`).

This file describes the **bootstrap daemon this checkout can run**. It does not
pretend to be the Electron HUD in the private product repo.

---

## 1. What it is

A localhost client that lets Cortex (or an explicit local test) act on a real
desktop: screenshot, mouse, type, sandbox files, kill switch, hash-chained ledger.

**It is not an orchestrator.** It does not choose what work to do. Cortex does.
OpenClaw and Hermes are not part of this process.

---

## 2. Entry points

| Path | Role |
|---|---|
| `Pointer/pointer/server.py` | `ThreadingHTTPServer` on `127.0.0.1:7420` |
| `Pointer/pointer/__main__.py` | `serve`, `verify`, `live-click` |
| `Pointer/scripts/verify.sh` | unit tests + live mouse/screenshot |
| `Pointer/scripts/install_windows.ps1` | laptop checker |

---

## 3. HTTP surface - measured from code

| Method | Path | Auth |
|---|---|---|
| GET | `/health`, `/healthz` | none |
| GET | `/v1/status` | none (loopback) |
| POST | `/v1/intent` | pair token if `source=remote-paired` |
| POST | `/v1/kill` | none (loopback kill is intentional) |
| POST | `/v1/unkill` | pair token |

Non-loopback bind is refused unless `POINTER_ALLOW_REMOTE=1`.

---

## 4. Trust boundaries

| Boundary | Enforced by | Bypass |
|---|---|---|
| Cortex required for act | `gate.py` | explicit `source=local-test` or `allow_local_act`, always listed in `degraded` |
| Irreversible act | approval token | none in code |
| `shell` | engine always refuses | none |
| File IO | name-only path under `.pointer-state/sandbox` | none; `../x` collapses to sandbox/`x` |
| Remote act | pair token + approval token | none |
| Kill switch | `.pointer-state/KILL` | `POST /v1/unkill` with pair token |

---

## 5. Executor backends

| OS | Mouse | Type | Screenshot |
|---|---|---|---|
| Linux | `xdotool` (measured working on this VM) | `xdotool type` | `ffmpeg -f x11grab` (measured PNG) |
| Windows | `ctypes.windll.user32` SetCursorPos / mouse_event | not wired | not wired |

Display on this VM: `:1`, `1920x1200`.

---

## 6. What this TAS does not cover

The private product at `Netie-AI/Pointer` (Word coworker, 60s recall ring, Electron HUD,
Clicky). This token cannot clone it. Do not claim the bootstrap is that app.
