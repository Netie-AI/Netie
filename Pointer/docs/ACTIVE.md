# Active map

What exists in this bootstrap and where.

| Path | Role |
|------|------|
| `pointer/protocol.py` | Frozen request/response payloads (`pointer.intent/v1`) |
| `pointer/gate.py` | Kill switch, Cortex requirement, approval, pair token |
| `pointer/ledger.py` | Hash-chained jsonl |
| `pointer/executor.py` | Linux xdotool/ffmpeg; Windows mouse via ctypes |
| `pointer/engine.py` | Perceive/act/prove; sandbox file IO |
| `pointer/server.py` | `127.0.0.1:7420` HTTP |
| `pointer/fallback.py` | OpenClaw/Hermes/Ollama presence report |
| `scripts/verify.sh` | Unit tests + live mouse |
| `scripts/install_windows.ps1` | Laptop installer/checker |
| `tests/test_pointer.py` | Gate, ledger, sandbox |

Default listen: `http://127.0.0.1:7420`
Health: `GET /health`
Status: `GET /v1/status`
Intent: `POST /v1/intent`
Kill: `POST /v1/kill`
