# 2026-11-12 - voice capture (personal tool on shdennlin/whisper-wrap)

Preflight: KB `D:\Netie-KB` absent in this cloud box. `docs/subagents_findings/INDEX.md`
read. PREFLIGHT: PARTIAL (the freeide-ext "refused by auto mode, not run" row is the same
class as F1 below). No subagents spawned: one upstream, one seam, nothing to parallelise.

Branch `claude/friendly-feynman-x4hd1v`. Deliverable: `docs/patches/voice-capture-0001-capture.patch`
and `voice-capture-0002-ask-claude.patch` against `shdennlin/whisper-wrap` at `56e5cf6` (MIT).

## Upstream choice (measured by reading the trees)

| Candidate | License | Verdict |
|---|---|---|
| `shdennlin/whisper-wrap` | MIT | Taken. FastAPI, in-process Whisper, ships an iOS Shortcut, one LLM seam. |
| `Mitchymayo/unpinned` | MIT | Folder sync only. No server, no LLM step. |
| `harshbirajdar/ig-fact-checker` | MIT | Shortcut to Claude, but built around Instagram. |
| `eitanfire/memnon` | no LICENSE file | Class C. Not usable. |

## F1. Half of the new tests never ran

- **Expected:** every test in the patch runs before the patch is called done.
- **Actual:** 13 service tests ran and pass (7 capture, 6 Claude `/ask`), in an isolated venv
  holding only `anthropic`, `pydantic` and `pytest`, with the Anthropic client stubbed. The 5
  endpoint tests (token unset -> 503, bad token -> 401, response JSON) and the whole upstream
  suite did not run: `uv sync --extra dev` inside the clone was refused by auto mode twice.
- **Repro:** in a session under auto mode, clone the upstream and run `uv sync --extra dev`.
- **Root-cause class:** verification blocked by a permission control, then reported as a
  partial pass. Same class as the freeide-ext `bun run test:unit` row.
- **Invariant:** a skipped test is a failing test. The auth gate on `/capture` is unproved
  until `uv run pytest tests/test_capture.py` runs on a machine that can install the tree.

## F2. The capture gate was proved able to fail (service half only)

- **Expected:** removing the inbox write breaks a test.
- **Actual:** with `save_unsorted` replaced by `pass`, 4 of 7 capture tests fail.
- **Repro:** edit `app/services/capture.py`, run `pytest tests/test_capture.py`.
- **Root-cause class:** none, the gate held.
- **Invariant:** prove a gate can fail before trusting it green.

## F3. The tool is off the safe path by construction

- **Expected (Netie law):** app -> Cortex -> OpenVault -> run.
- **Actual:** the patched server holds `ANTHROPIC_API_KEY` and calls Anthropic directly. The
  other upstream endpoints (`/transcribe`, `/ask`, `/listen`) have no auth at all.
- **Repro:** read `app/services/capture.py` and `app/main.py` in the patched tree.
- **Root-cause class:** a personal tool parked in the constitution repo because the session
  token can push nowhere else. It is not a catalog entry and claims no stage.
- **Invariant:** a path that skips a box is a bug for a product. Do not promote this without
  a PRD and an OpenVault route. Keep the server on LAN or a tailnet.

## Not measured

No live Claude call (no key in the session). No phone ran the Shortcut. The Shortcut steps in
the patched `docs/CAPTURE.md` follow the upstream upload format and are an assumption.
