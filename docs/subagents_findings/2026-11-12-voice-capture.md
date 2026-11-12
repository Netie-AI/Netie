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

## Update, same day: installed, run end to end, reviewed (3 agents)

Shape: 3 background agents, isolated contexts, one shared clone. (1) phone page, item list
and tick-off, with the token check moved to a module with no upstream imports; (2) a 59-case
accuracy eval and scorer, files under `evals/` only; (3) an adversarial reviewer, read-only,
on the committed state. Why: the three did not share files, and the reviewer had to be a
different context from the author. The parent applied the review fixes and ran everything.

F1 is closed. The founder allowed the install; with upstream present the 5 endpoint tests ran
and pass. Numbers are in `docs/patches/README.md`.

## F4. The review found two defects that tests could not have caught

- **Expected:** a tree that passes its tests also boots and fails closed when deployed.
- **Actual:** `uv.lock` did not list `anthropic`, so the Docker image (`uv sync --frozen`) would
  not import. `.env.example` carried an inline comment on the `CAPTURE_TOKEN=` line; under
  systemd `EnvironmentFile` the comment text becomes the token, so the endpoint would be open
  with a published value. Both fixed in `0003`. Neither was executed here (read from documented
  parser behaviour).
- **Repro:** `docker compose up --build` on the two-patch tree; a systemd unit with the old
  example file copied as `.env`.
- **Root-cause class:** config and packaging are outside the unit tests' reach.
- **Invariant:** assert the artifact the user actually receives, not the code under test.

## F5. Setting one key silently changed an unauthenticated endpoint

- **Expected:** adding a Claude key for `/capture` (token-gated) changes only `/capture`.
- **Actual:** `0002` moved the unauthenticated `/ask` onto Claude whenever the key was set, so
  anyone who could reach the server could spend it. Now a separate `ASK_BACKEND=claude` opt-in.
- **Repro:** two-patch tree, set `ANTHROPIC_API_KEY`, `POST /ask` with no token.
- **Root-cause class:** a credential scoped by intent, not by code.
- **Invariant:** never cut on trust-boundary validation.

## F6. Model output was written raw

- **Expected:** a transcript cannot forge lines in the files.
- **Actual:** `topic`, `due` and `currency` went to disk unvalidated; a newline in `topic` could
  add a forged task line, and expense text starting with `=` ran as a spreadsheet formula. `0003`
  validates every field and has a test that feeds hostile values.
- **Repro:** two-patch tree, stub the model to return `topic="x\n- [ ] forged"`.
- **Root-cause class:** treating structured model output as trusted because it parsed.
- **Invariant:** never cut on trust-boundary validation.

## F7. First accuracy number, and what it is not

57 of 59 on `gemini-3.1-flash-lite`. n is 59 and the cases were written by a model, so this
says "no obvious breakage", not an error rate (rule of three: below n = 300 do not claim zero).
Claude was not measured. The prompt before it was tightened was not measured either, so there
is no before/after. The first run lost 4 cases to the free tier's 15 requests a minute and one
timeout; those were re-run. A rate-limited capture in real use lands in the inbox, visibly.
