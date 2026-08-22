# All Things Agentic - Taskmaster scaffold

This folder is the Devpost entry shape. It is **not** Cortex and **not** a second orchestrator.

Deadline: 31 Aug 2026 17:00 PDT.
Official: https://allthingsagentichackathon.devpost.com/

## Required Google stack

1. Gemini 3.5+ via `google-genai` (`GEMINI_API_KEY` or OpenVault `GOOGLE_API_KEY`)
2. This HTTP service on Cloud Run (the GCP service)
3. Pointer daemon stays on loopback `127.0.0.1:7420`

Without a key the planner refuses. A silent fallback is a lie.

Key source of truth is OpenVault (cloneable `Netie-AI/OpenVault`), provider id `google`, env `GOOGLE_API_KEY` (AI Studio: https://aistudio.google.com/apikey). `pointer serve` does not import this planner and does not copy vault secrets. Export `GOOGLE_API_KEY` or `GEMINI_API_KEY` into the hackathon process only.

## Architecture (ASCII)

```
founder laptop                  Google Cloud
-----------------               -----------------
browser / Meet                  Cloud Run :8080
        |                         GET /health
Pointer daemon                    POST /plan {goal}
127.0.0.1:7420  <---JSON intent---  Gemini 3.5 Flash
POST /v1/intent                     (google-genai SDK)
gate + ledger + prove
loopback mouse only
POINTER_ALLOW_REMOTE stays unset
```

## Spin-up (local)

```bash
cd Pointer
python3 -m pip install -r hackathon/requirements.txt
export GOOGLE_API_KEY=...   # from OpenVault provider google, or GEMINI_API_KEY; not in git
PYTHONPATH=. python3 hackathon/app.py
# GET http://127.0.0.1:8080/health
# POST http://127.0.0.1:8080/plan  {"goal":"move to 220,180 and perceive"}
```

Then, only on the laptop, POST the returned intent to `http://127.0.0.1:7420/v1/intent`.

## Spin-up (Cloud Run)

From the `Pointer/` directory (build context must include `pointer/`):

```bash
gcloud run deploy pointer-hackathon --source . --dockerfile hackathon/Dockerfile
# set GOOGLE_API_KEY or GEMINI_API_KEY as a Cloud Run secret. Do not --allow-unauthenticated unless you accept public planners.
```

Demo video must show the Cloud Run dashboard or `.run.app` URL plus the Pointer prove screenshot. Do not enable `POINTER_ALLOW_REMOTE=1`.

## What this is not

- Not a $1M claim. Individual/Hobbyist is USD 10k x2.
- Not OpenClaw/Hermes.
- Not an unattended remote-control product.
