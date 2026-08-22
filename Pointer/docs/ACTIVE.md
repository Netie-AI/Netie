# Active map

What exists in this bootstrap and where.

| Path | Role |
|------|------|
| `pointer/protocol.py` | Frozen request/response payloads (`pointer.intent/v1`) |
| `pointer/gate.py` | Kill switch, Cortex requirement, approval, pair token |
| `pointer/ledger.py` | Hash-chained jsonl |
| `pointer/executor.py` | Linux xdotool/ffmpeg; Windows mouse + SendInput + PowerShell screenshot |
| `pointer/windows_input.py` | Windows SendInput + PowerShell screenshot (unit-tested off-Windows) |
| `pointer/engine.py` | Perceive/act/prove; sandbox file IO |
| `pointer/server.py` | `127.0.0.1:7420` HTTP; `GET /` laptop steps |
| `pointer/pair.py` | Pair tokens + `PAIR_CARD.txt` (no tokens unless `--show`) |
| `pointer/fallback.py` | OpenClaw/Hermes/Ollama presence report |
| `scripts/verify.sh` | Unit tests + live mouse |
| `scripts/install_windows.ps1` | Laptop start + prove + pair card + Desktop copies |
| `tests/test_pointer.py` | Gate, ledger, sandbox, Windows input, pay-page URLs |
| `pay/index.html` | Durable pay page: live Stripe + Drive sheet + Pointer RM 300 QR |
| `docs/CRADLE_SPARK.md` | Founder-only CIP Spark submit pack; traction honesty |
| `docs/HACKERONE.md` | Founder-only H1 signup pack; no exploits/PoCs from this agent |
| `docs/FIVERR_GIG.md` | Founder-only Fiverr paste pack; no false traction |
| `docs/FORHIRE.md` | Founder-only r/forhire paste; one post / 7 days |
| `docs/BUGCROWD.md` | Founder-only Bugcrowd signup; no exploits/PoCs |
| `docs/STRIPE_PAYOUTS.md` | Founder Dashboard identity; no NRIC in git |
| `docs/AGENTIC_HACK.md` | Founder-only Devpost submit pack; Gemini/ADK/GCP required |
| `hackathon/` | Cloud Run + google-genai planner scaffold; fail-closed without GEMINI_API_KEY |

Default listen: `http://127.0.0.1:7420`
Root: `GET /` (laptop steps, no tokens)
Health: `GET /health`
Pay: `GET /pay` (static `pay/index.html`)
QR: `GET /pay/pointer-rm300.png`
Status: `GET /v1/status`
Intent: `POST /v1/intent`
Kill: `POST /v1/kill`
