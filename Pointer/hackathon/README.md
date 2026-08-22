# All Things Agentic - Taskmaster scaffold

This folder is the Devpost entry shape. It is **not** Cortex and **not** a second orchestrator.

Deadline: 31 Aug 2026 17:00 PDT.
Official: https://allthingsagentichackathon.devpost.com/

## Required Google stack

1. Gemini 3.5+ via `google-genai` (`GEMINI_API_KEY`)
2. This HTTP service on Cloud Run (the GCP service)
3. Pointer daemon stays on loopback `127.0.0.1:7420`

Without `GEMINI_API_KEY` the planner refuses. A silent fallback is a lie.

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
export GEMINI_API_KEY=...   # founder GCP / AI Studio key, not in git
PYTHONPATH=. python3 hackathon/app.py
# GET http://127.0.0.1:8080/health
# POST http://127.0.0.1:8080/plan  {"goal":"move to 220,180 and perceive"}
```

Then, only on the laptop, POST the returned intent to `http://127.0.0.1:7420/v1/intent`.

## Spin-up (Cloud Run)

From the `Pointer/` directory (build context must include `pointer/`):

```bash
gcloud run deploy pointer-hackathon --source . --dockerfile hackathon/Dockerfile
# set GEMINI_API_KEY as a Cloud Run secret. Do not --allow-unauthenticated unless you accept public planners.
```

Demo video must show the Cloud Run dashboard or `.run.app` URL plus the Pointer prove screenshot. Do not enable `POINTER_ALLOW_REMOTE=1`.

## What this is not

- Not a $1M claim. Individual/Hobbyist is USD 10k x2.
- Not OpenClaw/Hermes.
- Not an unattended remote-control product.
