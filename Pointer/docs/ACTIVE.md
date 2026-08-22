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
| `scripts/install_windows.ps1` | Laptop start + live-click + pair card |
| `tests/test_pointer.py` | Gate, ledger, sandbox, Windows input, pay-page URLs |
| `pay/index.html` | Durable pay page: live Stripe + Drive sheet + Pointer RM 300 QR |
| `docs/CRADLE_SPARK.md` | Founder-only CIP Spark submit pack; traction honesty |

Default listen: `http://127.0.0.1:7420`
Root: `GET /` (laptop steps, no tokens)
Health: `GET /health`
Pay: `GET /pay` (static `pay/index.html`)
Status: `GET /v1/status`
Intent: `POST /v1/intent`
Kill: `POST /v1/kill`
