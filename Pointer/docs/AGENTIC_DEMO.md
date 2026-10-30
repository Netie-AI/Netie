# All Things Agentic - 4 minute demo shot list

This is not a submitted video. This agent cannot film your laptop or Cloud Console. A win is not confirmed. No math or research exam.

Judges (rules measured 2026-08-22): Innovation 40%, Architecture 30%, Demo 30%. They want unedited live execution plus visual proof of Google Cloud.

Phone copy (Drive): https://docs.google.com/document/d/1BE_tt-bZB47vTRJsDgHHJsLMlXEz-dcpvP1cDz3L8uo/edit

Film AFTER Cloud Run is live (`DEPLOY=1` on a billed GCP project). Do not fake a `.run.app` URL. The cloud VM local daemon is already running; that clip alone is not a valid entry.

## Shot list

0:00-0:30 Friction

- Say: I need a fail-closed see/click agent on MY Windows laptop. Loopback only. Kill switch.
- Show `INSTALL.txt` or `GET http://127.0.0.1:7420/`

0:30-1:30 Proof of action (unedited, one take)

- Double-click `scripts\install_windows.cmd` or run `python -m pointer prove`
- Show Desktop `POINTER_PROVE.json` with `"ok": true` and screenshot_bytes >= 100
- Show a mouse move and the screenshot file
- `POST /v1/kill` then an act that is refused

1:30-2:30 Google stack (required)

- Cloud Console: service `pointer-hackathon` in `asia-southeast1`
- `GET` the `.run.app /health` must be 200 with no `missing_gemini_key`
- `POST /plan {"goal":"move to 220,180 and perceive"}` returns `pointer.intent/v1`
- Say: Gemini 3.5 + google-genai SDK + Cloud Run

2:30-3:30 Architecture

- Show the ASCII diagram in `hackathon/README.md`
- Cortex plans. Pointer acts on loopback. OpenVault holds `GOOGLE_API_KEY`.
- Say: `POINTER_ALLOW_REMOTE` stays unset

3:30-4:00 Honest close

- Track: Individual/Hobbyist
- Do not say 100K downloads. Do not claim a win.
- Show the GitHub repo + `hackathon/README.md` spin-up

## Do not film

- Pair tokens
- Binding `0.0.0.0` or `POINTER_ALLOW_REMOTE=1`
- `pointer serve` as the whole product
- A Cloud Run URL that does not exist yet

Unlock: YouTube or Drive video URL in Pointer/STATUS.md. This file is not the demo.
