# How to run Pointer, and the backend payloads

Answers the external questions in `asking.txt`.

## How does a user run Pointer on their local machine?

There are two trees:

1. **Product app** (Electron HUD / Clicky / Word coworker): `D:\Pointer`, remote
   `Netie-AI/Pointer`. That repo is private. This cloud token gets GitHub 404. Gmail
   shows PRs #26 and #27 landing on 2026-08-22, so the product exists on the laptop
   GitHub org, not in this checkout.
2. **Bootstrap daemon** (this repo, `Pointer/`): a localhost HTTP server this environment
   can actually start and test.

### Product app (laptop)

```powershell
cd D:\Pointer
# whatever README that repo ships; historical OpenVault stub was:
# cd "D:\Netie Clicks"; npm start
# Hotkey was Ctrl+Space -> drag frame -> chat.
```

If `D:\Pointer` is missing, run the bootstrap:

```powershell
cd D:\Netie\Pointer
$env:PYTHONPATH = (Get-Location)
.\scripts\install_windows.ps1
```

The script starts the daemon on `127.0.0.1:7420` if it is down, runs
`python -m pointer prove`, and writes `.pointer-state/PAIR_CARD.txt`.
Open http://127.0.0.1:7420/ for the laptop card. `prove` writes PNG
files under `.pointer-state/shots` (not `/tmp`) and `PROVE.json` with no tokens.

Default bind is `127.0.0.1:7420`. Non-loopback bind is refused unless
`POINTER_ALLOW_REMOTE=1`. Pair + approval tokens are written to
`Pointer/.pointer-state/pair.json` with mode 600. Do not commit that file.
`python -m pointer pair --show` dumps tokens locally. Do not email them.

Kill switch: `POST http://127.0.0.1:7420/v1/kill`.

### Bootstrap on Linux / this cloud VM

```bash
cd Pointer
PYTHONPATH=. python3 -m pointer serve
./scripts/verify.sh
```

A cloud agent **cannot** drive `D:\Pointer` until the laptop is running this daemon
(or the product app) and a pair token is present. Remote clicks still need the
approval token. That is fail-closed, not a missing feature.

## Exact request and response payloads

Schema id: `pointer.intent/v1`

### `GET /health`

```json
{"ok": true, "schema": "pointer.intent/v1"}
```

### `POST /v1/intent` request

```json
{
  "schema": "pointer.intent/v1",
  "intent_id": "it-20260822-1",
  "source": "human",
  "goal": "Move the pointer to 220,180 and prove it",
  "allow_local_act": false,
  "approval_token": null,
  "actions": [
    {"type": "perceive"},
    {"type": "move", "x": 220, "y": 180},
    {"type": "click", "x": 220, "y": 180, "button": "left"},
    {"type": "type", "text": "hello"},
    {"type": "hotkey", "keys": ["ctrl", "s"]},
    {"type": "wait", "ms": 250},
    {"type": "verify"},
    {"type": "file_write", "path": "note.txt", "content": "sandbox only"},
    {"type": "file_delete", "path": "note.txt"}
  ]
}
```

`source` is one of: `human`, `cortex`, `remote-paired`, `local-test`.

`local-test` or `allow_local_act: true` is the only way to act when Cortex is down.
The response then includes `degraded: ["local_act_without_cortex"]`. A silent fallback
is a lie; this field is the tell.

`shell` is always refused.

Remote (`source=remote-paired`) requires `Authorization: Bearer <pair_token>`. Any
act besides `perceive` also requires `approval_token`.

### `POST /v1/intent` response

```json
{
  "schema": "pointer.intent/v1",
  "intent_id": "it-20260822-1",
  "verdict": "executed",
  "reason": "gate open",
  "degraded": [],
  "ledger_hash": "64-hex",
  "screenshot_path": "/path/to/shot.png",
  "actions": [
    {
      "type": "move",
      "ok": true,
      "detail": "moved",
      "evidence": {"requested": {"x": 220, "y": 180}, "actual": {"x": 220, "y": 180}}
    }
  ]
}
```

`verdict` is `executed` | `refused` | `needs_approval`.

HTTP status: 200 executed, 409 needs_approval, 403 refused, 400 bad payload.

### `GET /v1/status`

Process status plus the OpenClaw/Hermes/Ollama presence report. Presence is
informational. This daemon does not launch those assistants.
