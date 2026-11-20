# 2026-11-20 - voice capture track: accuracy from audio, Docker

Preflight: KB `D:\Netie-KB` absent in this cloud box. `docs/subagents_findings/INDEX.md` and
`2026-11-12-voice-capture.md` read. PREFLIGHT: PARTIAL (same class as the 11-12 F1 and F4:
packaging and verification left unrun by an earlier session).

Branch `claude/voice-capture`, from `claude/friendly-feynman-x4hd1v` (draft PR #59; draft PR #65 for this track). Fork:
`shdennlin/whisper-wrap` at `56e5cf6` (MIT, class A), patches `0004` (audio eval) and `0005`
(Docker). Not a Netie product; not in the catalog, `NETIE.md` or `STATUS.md`.

Shape: one executor session did both parts itself (the work is serial on one clone and one
free Gemini key at 15 requests a minute, so there was nothing to parallelise); Opus-class
judgment was not needed. One subagent (sonnet, isolated context, read-only on this repo)
replayed the series; see "Replay". The commit order is B (0004) then A (0005); 0005 does not
depend on 0004 (checked, see Replay).

## Part B: accuracy from audio

### B1. The large-v3-turbo registry entry pointed at a repo that cannot be downloaded

- **Expected:** every `repo_id` in `registry/models.yaml` resolves, so `model-manager.sh download`
  works for each model the registry lists.
- **Actual:** `Systran/faster-whisper-large-v3-turbo` answers HTTP 401 on the Hugging Face API
  (the 11-12 session saw "not found"). faster-whisper 1.2.1 maps `large-v3-turbo` to
  `mobiuslabsgmbh/faster-whisper-large-v3-turbo`, which Hugging Face redirects (307) to
  `dropbox-dash/faster-whisper-large-v3-turbo` (MIT, `model.bin` plus tokenizer, CTranslate2).
  The entry now names that repo and pins revision `0a363e91`. Proof: faster-whisper loads the
  downloaded directory and transcribes ("Remind me to call the dentist and book a cleaning.");
  `model-manager.sh download large-v3-turbo` installs it; the server reports `large-v3-turbo`
  from `/status` and transcribes all 59 clips; the Docker entrypoint fetched it at run time.
- **Repro:** `curl -s -o /dev/null -w '%{http_code}' https://huggingface.co/api/models/Systran/faster-whisper-large-v3-turbo`
- **Root-cause class:** an external reference written from memory and never resolved.
- **Invariant:** assert the artifact the user receives (a model that downloads and transcribes),
  not the config that names it.

### B2. From audio the pipeline is 3 to 4 cases worse than from clean text

- **Expected (11-12 claim):** 57 of 59 on clean text says "no obvious breakage"; nothing was
  known about audio.
- **Actual:** breeze-asr-25 gets 53 of 59 (run 1) and 54 of 59 (run 2) from audio; turbo 49 and
  50. Of breeze's 4 losses against clean text, 3 are Malay words mis-heard ("cakap" as "kakup",
  "tol" as "toddy", "seratus lima puluh" as 50) and 1 is sorter noise. Numbers and the full
  case table are in the patched tree's `evals/audio/README.md`.
- **Repro:** `evals/audio/README.md` in the patched tree, "Reproduce".
- **Root-cause class:** speech-to-text errors on non-English words reach the sorter unmarked;
  nothing downstream knows the transcript is doubtful.
- **Invariant:** assert the artifact the user actually receives, not the stage under test.

### B3. The speech model with the lower word error rate filed fewer cases right

- **Expected:** large-v3-turbo (WER 7.5% folded) beats breeze-asr-25 (10.6%).
- **Actual:** it hears English better and files 4 fewer cases correctly in both runs (49 and 50
  against 53 and 54), takes 15.6 s a clip against 12.0 s, and holds 4.0 GB against 2.4 GB. Its
  extra losses are mostly Malay "esok" (heard as "isaq", "Isak"), a sentence break that moved
  "Friday" to the wrong task, and a keyword check tripped by "Y-15". Re-sorting the clean text
  three times separates hearing (8 cases pass 3 of 3 on clean text) from sorter noise (3 cases).
  Default stays `breeze-asr-25`; the registry is unchanged. This is not evidence that breeze
  is better: 4 cases of 59, one synthetic English voice reading Malay with English sounds.
- **Repro:** `evals/audio/run_audio.py` steps in the README.
- **Root-cause class:** a component metric (WER) that does not track the end-to-end outcome.
- **Invariant:** separate verified fact from assumption; a lower WER is not a better filing rate.

### B4. A transient Gemini error was scored as a wrong answer

- **Expected:** a case fails only when the answer is wrong.
- **Actual:** the first breeze pass read 52 of 59 because 2 cases hit Gemini "503 high demand"
  and scored as `error`; run 2 lost one case to a classify timeout. The runner kept the error in
  the record (never silently retried), then re-ran only errored cases (`--retry-errors-of`) and
  treats 429, 503 and timeout as retryable. The 52 is reported next to the 53.
- **Repro:** `sort_all` with a stub that raises `503 UNAVAILABLE`; `test_sort_retries_a_503_overload`.
- **Root-cause class:** infrastructure failure indistinguishable from model failure in the score.
- **Invariant:** fail loud with cause; silent fallback is a lie. No test or expected answer was
  changed.

### B5. Two defects in my own tooling, found by reading outputs

- **Actual:** (a) the first number normaliser summed spoken digits, so "one two three" became "6"
  and the WER was wrong; seen when "testing testing one two three" showed 3 errors against
  "Testing testing 1 2 3". Fixed (units only join after a tens word, hundred, thousand or "and"),
  test added. WER moved from 10.2% to 10.6% (breeze) and from 7.9% to 7.5% (turbo).
  (b) the first sort used the system python, which lacks `anthropic`; the run died at import
  while a wait loop kept waiting, about 10 minutes lost.
- **Root-cause class:** (a) a metric trusted before its outputs were read; (b) a wait on a file
  instead of on the process.
- **Invariant:** prove a gate can fail before trusting it green (the new tests fail on the old
  normaliser).

### B6. The sorter is not deterministic, and the stored 57 is one sample

- **Actual:** sorting the same transcripts twice changed the verdict of 1 case (breeze) and 3
  (turbo). On clean text, `ambig-balance-due` failed 3 of 3 today though the stored 11-12 run
  passed it. Read differences of one to three cases as noise.
- **Root-cause class:** a single sample reported as a rate.
- **Invariant:** do not claim "0 wrong" below n = 300; one run is one sample.

### Measured (Part B)

- 59 clips (gTTS, English voice), `/transcribe` raw octet-stream, CPU, per model: WER, seconds
  per clip, server RSS, end to end on `gemini-3.1-flash-lite` twice, clean-text re-sort three
  times for 11 cases. 20 runner tests pass with the network stubbed; the 46 `evals/` tests pass.
- Registry fix proved by load, transcription, `model-manager.sh`, server and Docker run time.

### Not run (Part B)

- Claude as the sorter (no Anthropic key). A human voice or a phone microphone. A real
  Malaysian speaker saying the Malay words (gTTS read them with English sounds, so the Malay WER
  ranks nothing). A GPU. Windows. `language=` hints. A second synthetic voice.

## Part A: Docker

Built and run with Docker Engine 29 and Compose v5 in this sandbox. The sandbox egress needs the
session CA inside containers, so the runs used `Dockerfile.sandbox` and `docker-compose.sandbox.yml`,
both uncommitted. `Dockerfile.sandbox` differs from the committed `Dockerfile` by exactly the
three CA lines at the top (`diff` shown in the session). No forwarder to the egress proxy was
tried or needed: bridge networking reached the internet once the CA was trusted. Nothing was
refused by the permission system.

### A1. The image could not start or build as shipped

- **Expected:** `docker compose up --build` produces a running server.
- **Actual:** three defects, all fixed in `0005`. (a) The Dockerfile never copies `alembic.ini` and
  `alembic/`, and the lifespan runs `alembic upgrade head` from the working directory: read from
  `app/main.py:217-224`, the original Dockerfile was not built (the lost run's crash is
  consistent, not reproduced). With the files copied the migrations run at start (log seen).
  (b) `hf` is not on `PATH` in the image, so `model-manager.sh download` stops with "Neither
  'hf' nor 'huggingface-cli' found"; reproduced in my first rewrite, the original has the same
  PATH. `ENV PATH=/app/.venv/bin` fixes it. (c) `CMD uv run ...` would re-sync at every start
  (and pull the dev group); read from uv behaviour, not measured. The entrypoint calls the venv.
- **Repro:** `docker compose up --build` on the pre-0005 tree (not run for the original);
  (b) visible in a build of my first rewrite.
- **Root-cause class:** packaging outside the unit tests' reach, never executed (same as 11-12 F4).
- **Invariant:** assert the artifact the user receives; uncommitted/unrun is not done.

### A2. CPU-only wheels: image 15.2 GB to 5.47 GB, and a wrong first attempt

- **Expected:** a small image that still sorts notes end to end.
- **Actual:** with the lockfile's wheels the image is 15.2 GB (cold build 492 s, measured with
  `TORCH_INDEX=`). With CPU wheels it is 5.47 GB (cold build 130 s, base images cached): Python
  and apt 0.7 GB, venv 1.3 GB, model 1.57 GB. Capture still works: 76 capture tests pass inside
  the container, silero VAD loads (`/status` shows `silero`), text and audio captures sort, torch
  is `2.8.0+cpu`. The first attempt filtered the nvidia and torch lines out of `uv export` but
  installed the rest with dependency resolution, so uv fetched a newer CUDA 13 torch and its
  nvidia wheels (seen in the build log, build stopped). `--no-deps` installs exactly the lock.
- **Root-cause class:** removing pins from a lock export hands the choice back to the resolver.
- **Invariant:** reproduce on a live stack; do not weaken a check (torch is still pinned by the lock).

### A3. Compose bugs found by reading and running

- **Actual:** (a) the port mapping was `API_PORT:API_PORT`, but the server always listens on 8000,
  so any other `API_PORT` mapped to nothing; now `API_PORT:8000`. (b) `GEMINI_MODEL` defaults to
  `gemini-2.5-flash` in compose and `gemini-3.1-flash-lite` in `app/services/llm.py`:
  **reported, not changed**; it only affects `/ask` (`/status` in the container shows
  `gemini-2.5-flash`). (c) pass-through of an empty `CAPTURE_BACKEND` would give "" and not "auto"
  (read from `app/config.py`), so compose supplies the defaults `auto`, `gemini`, `MYR`.
  (d) a source edit re-ran the 1.5 GB model layer; the model now comes before `app/`: `up
  --build` after an edit went from 99 s to 19 s.
- **Root-cause class:** config copied between two places that drifted.
- **Invariant:** silent fallback is a lie; report a mismatch rather than hide it.

### A4. Windows line endings would break the scripts

- **Expected:** a Windows checkout works.
- **Actual:** with `autocrlf`, `docker-entrypoint.sh` and `scripts/*.sh` become CRLF and `sh`
  cannot run them. The Dockerfile strips `\r`. Checked by converting the scripts to CRLF on
  Linux, rebuilding (healthy in 107 s, 0 CR bytes in the image). **A real Windows checkout was
  not run.**
- **Root-cause class:** platform assumption.
- **Invariant:** assert the artifact received (the file in the image), not the checkout.

### A5. docs/CAPTURE.md still says Docker is not set up (not edited, exact text below)

`docs/CAPTURE.md` is outside the files this track may change. Old text, section "Docker":

    `docker-compose.yml` is not set up for capture: it passes none of the variables above and
    keeps `DATA_DIR` inside the container, so a rebuild would delete your files. Run from a
    checkout (`make dev`, launchd or systemd) until you add the variables and a data volume.

New text:

    Run it in Docker with `docker compose up -d --build`; see `docs/CAPTURE-DOCKER.md` for the
    `.env`, the data volume, backups and phone access.

### Measured (Part A), on Linux, final committed Dockerfile plus the three sandbox CA lines

| Check | Result |
|---|---|
| Cold build (base images cached, cache pruned) | 130 s |
| Image size | 5.47 GB (lockfile wheels: 15.2 GB, 492 s) |
| Time to healthy after `up` | 16 to 20 s |
| Idle memory (`docker stats`) | 1.8 GiB |
| No token / wrong token on `/capture` | 401 / 401 |
| `CAPTURE_TOKEN` empty | 503 (also with a guessed or empty bearer) |
| Text capture "paid 500 ringgit deposit for the bike, collect it Saturday" | sorted: expense 500 MYR, task due 2026-11-21; files in `/data/capture` |
| Audio capture (mp3 posted as octet-stream) | sorted, 13.5 to 14.3 s end to end |
| `down` then `up` | items kept (4 open tasks, 3 expenses after the later runs) |
| `up --build` after editing `app/main.py` (reverted) | items kept, healthy in 19 s |
| `CAPTURE_TZ=Asia/Kuala_Lumpur` | timestamps `+08:00`; `ZoneInfo('Asia/Kuala_Lumpur')` loads |
| Run-time model fetch (`MODEL_NAME=large-v3-turbo`) | downloaded into the volume, served, healthy in 30 s |
| `docker compose cp` backup and restore of `/data/capture` | worked both ways |
| Capture tests inside the container | 76 passed |

### Not run (Part A)

Anything on Windows or Docker Desktop. A real phone (the Shortcut over HTTP, the page over HTTPS,
Tailscale). The original Dockerfile (not built, defects read from code). GPU containers. The
whole upstream suite inside the container. A build on a machine without the base images cached.

## Replay

A different agent (sonnet, isolated) cloned `shdennlin/whisper-wrap` fresh at `56e5cf6`, ran
`git am` on `0001` to `0005` in order: all applied cleanly, no warnings; the tree hash equals the
builder's (`f96e388a`); upstream `LICENSE` unchanged. It also applied `0001-0003` plus `0005`
without `0004`: clean, so the two new patches are independent apart from order. After `uv sync
--extra dev`: capture tests 76 passed, `evals` 46 passed (includes the 20 runner tests). Static
checks passed (yaml, `sh -n`). The only key-like strings in the tree are the documented
placeholders `sk-ant-...` and `AIza...` in upstream docs. The agent ran no Docker.
