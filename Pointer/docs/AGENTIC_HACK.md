# All Things Agentic hackathon - founder submit pack

This agent cannot submit on Devpost. Founder submits.

Official: https://allthingsagentichackathon.devpost.com/
Rules: https://allthingsagentichackathon.devpost.com/rules
Deadline measured 2026-08-22: **31 Aug 2026 17:00 PDT**.

Phone copy (Drive): https://docs.google.com/document/d/1P3E2rf1NSnNUrf454YB6dL5P34ObNv3PmICVu1yb59Y/edit

Malaysia is not on the excluded-residence list (Italy, Quebec, Crimea, Cuba, Iran, Syria, North Korea, Sudan, Belarus, Russia, OFAC). Age-of-majority applies. This agent will not store DOB in git.

## What a valid entry MUST include (not optional)

Every project must use:

1. Gemini 3.5 or newer (Gemini API or Vertex AI)
2. At least one Google agent framework: ADK, GenAI SDK, Antigravity SDK, or Genkit
3. At least one Google Cloud service (Cloud Run, Cloud SQL, Firestore, GKE, or Pub/Sub)

The Netie Pointer **daemon** on this VM (stdlib HTTP + xdotool) does **not** satisfy those three by itself. Do not submit `pointer serve` as the whole entry.

Scaffold in this PR (still needs the founder's Gemini key + Cloud Run deploy):

- `pointer/gemini_planner.py` -- GenAI SDK, fail-closed without the key, refuses `shell`. Reads `GEMINI_API_KEY` or OpenVault's `GOOGLE_API_KEY` (provider `google`). Does not copy secrets from OpenVault.
- `hackathon/app.py` + `hackathon/Dockerfile` -- Cloud Run HTTP `POST /plan`
- `hackathon/README.md` -- spin-up + architecture diagram
- `scripts/deploy_hackathon.sh` / `.ps1` -- dry-run unless `DEPLOY=1`; refuses remote Pointer and missing key/gcloud; `--no-allow-unauthenticated`

This agent has no Gemini key on the cloud VM and cannot submit Devpost. Store the key in OpenVault (`POST /api/keyvault/upsert`, env_key `GOOGLE_API_KEY`), then export it into Cloud Run. Not a second Pointer vault.

Track fit if you add the Google stack: Taskmaster (agent takes action, not just chat). Collaborative Partner if you keep the human in the loop (Pointer kill switch + approval token).

Do not set `POINTER_ALLOW_REMOTE=1` to please judges. Demo loopback prove + a Cloud Run/Gemini planner that emits `pointer.intent/v1`. Laptop stays local.

## Prize lanes that match evidence

- Individual/Hobbyist: USD 10,000 x2. Use this if you submit as a person. Stripe account is `individual`.
- Startup Excellence: USD 20,000. Needs an incorporated org + corporate email. Not in evidence. Skip unless SSM Sdn Bhd exists.
- Grand Prize USD 50,000 is not a plan. Do not write "we will win $1M".

Submit: public or private GitHub (share private with testing@devpost.com and cloudhackathons@google.com), README spin-up, architecture diagram, ~4 min demo that shows Google Cloud running.

## What not to claim

- 100K downloads / 10K paid users (false vs Stripe: MYR 0, 0 charges)
- Slingshot 2026 winner (closed 2026-07-27; no confirmation mail)
- OpenClaw/Hermes as the product (forbidden third orchestrator)
- Unattended remote control of a stranger's PC

## Also open (not this pack)

Y Combinator Fall 2026: on-time deadline was 2026-07-27; late applications still accepted with no promised decision date. Pack: `docs/YC_FALL_2026.md`. https://www.ycombinator.com/apply -- same traction honesty. This agent cannot fill the YC form.

Gmail measured 2026-08-22: Devpost newsletter from darlyze@devpost.com on 2026-08-20 (Backblaze hackathon recap). A Devpost login exists. Submit All Things Agentic with that account. Still no project URL.

## Unlock

Devpost project URL in Pointer/STATUS.md. This file is not a submitted entry.
