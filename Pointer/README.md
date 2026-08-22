# Pointer

Laptop-control client (plane 4). Sees the screen, clicks, types, verifies. Cortex plans.
This tree is the **bootstrap daemon** that this cloud environment can actually run.

The product repo is `Netie-AI/Pointer` (private). This cloud GitHub token cannot clone it.
Gmail shows it is alive (PR #26, #27 on 2026-08-22). Until the token can see that repo,
run this daemon.

## Run on this machine

```bash
cd Pointer
PYTHONPATH=. python3 -m pointer serve
```

Health: `GET http://127.0.0.1:7420/health`

## Prove control (Linux with a display)

```bash
cd Pointer
PYTHONPATH=. python3 -m pointer live-click --x 220 --y 180
./scripts/verify.sh
```

## Run on the Windows laptop

```powershell
cd D:\Netie\Pointer
$env:PYTHONPATH = (Get-Location)
.\scripts\install_windows.ps1
```

That script starts `python -m pointer serve` on loopback if needed, runs
`live-click`, writes `.pointer-state/PAIR_CARD.txt`, and copies
`POINTER_CARD.txt` plus `POINTER_RM300.png` to the Desktop.

`live-click` screenshots go to `.pointer-state/shots`, not `/tmp`.
Do not set `POINTER_ALLOW_REMOTE=1`. Do not email pair tokens.
This cloud VM still cannot click `D:\Pointer`.

OpenClaw / Hermes: **not** a Pointer replacement. `NETIE.md` forbids a third
orchestrator. Check with `python -m pointer verify`. Install via `ollama launch openclaw`
or `ollama launch hermes` only on the laptop if this daemon cannot start.

## Pay (does not expire)

Open `pay/index.html` or, with the daemon up, http://127.0.0.1:7420/pay

## Cradle CIP Spark

`docs/CRADLE_SPARK.md`. Founder submits on GMS. Do not paste unverified traction.

## Fiverr

`docs/FIVERR_GIG.md`. Founder publishes. Pay on Fiverr for that gig.
