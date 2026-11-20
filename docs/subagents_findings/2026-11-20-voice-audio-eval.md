# 2026-11-20 - voice capture, accuracy from audio and the second speech model

Preflight: KB `D:\Netie-KB` absent in this cloud box. `docs/subagents_findings/INDEX.md` and
`2026-11-12-voice-capture.md` read; F7 there ("first accuracy number, and what it is not") is
the hit. PREFLIGHT: PARTIAL. One lane of a wave started by a parent session. No subagents
spawned by this lane: one clone, one CPU, the passes had to run one after another to keep the
timings clean.

Branch `claude/voice-audio-eval`. Deliverable: `docs/patches/voice-capture-audio-eval.patch`,
one commit on top of `voice-capture-0001..0003` against `shdennlin/whisper-wrap` at `56e5cf6`
(MIT, class A). It adds `evals/audio/` (runner, 20 tests, five result files, a README) and
changes one line of `registry/models.yaml`. Upstream `LICENSE` untouched. The tool is still
personal, not a Netie product, and claims no stage.

All numbers are from the real path (`uv sync --extra dev` was allowed; the patched server,
`POST /transcribe`, raw body, `application/octet-stream`). Nothing here is a proxy number.

## Result (measured)

59 synthetic clips (gTTS, US English voice), 655 source words. Sorter `gemini-3.1-flash-lite`.

| Speech model | Word error rate, raw | numbers normalised | End to end | Seconds per clip (median) | Peak memory |
|---|---|---|---|---|---|
| `breeze-asr-25` (default) | 14.2% (93/655) | 9.6% (63/655) | answered 59, correct 52 | 12.4 | 3.4 GB |
| `large-v3-turbo` (float32) | 10.7% (70/655) | 7.5% (49/655) | answered 59, correct 48 | 16.4 | 4.5 GB |
| `large-v3-turbo`, `COMPUTE_TYPE=int8` | 11.0% (72/655) | 7.9% (52/655) | not run | 10.0 | 2.4 GB |

Clean text, stored run: 57 of 59. Second voice (gTTS UK), speech to text only: both models
62/655 after number normalisation. Default model: not changed (F3).

## F1. The speech-to-text half costs cases, and on this set all of them are Malay

- **Expected:** unknown. The only number was the sorter on clean text, 57 of 59.
- **Actual:** from audio, 52 of 59 with `breeze-asr-25` and 48 of 59 with `large-v3-turbo`.
  Every case that flipped because a word was misheard is one of the six Malay-tagged cases
  (3 with breeze, 5 with turbo): `seratus lima puluh` filed as 50 or 350 instead of 150,
  `bayar tol` filed as lunch, `esok` (tomorrow) lost. On the 53 other clips no case was lost to
  a misheard word. The remaining flips are the sorter varying between runs (checked: 6 cases
  re-asked 3 times each with the same heard text; 4 of the 6 passed at least once), one full
  stop placed by turbo that moved a date (`...the loan Friday. Send...`, failed 3 of 3), and one
  scorer keyword miss (`Y15` written `Y-15`, the filed note is right).
- **Repro:** apply the four patches, start the server, then the three commands in
  `evals/audio/README.md` ("Run"). Stored rows: `evals/audio/results-*.jsonl`.
- **Root-cause class:** an English text-to-speech voice mispronounces Malay, so the Malay rows
  measure the voice, not the model. The test input is the weak part, not yet the product.
- **Invariant:** say what is measured and what is assumed. Do not claim an error rate below
  n = 300; n is 59 here and 6 for Malay.

## F2. The `large-v3-turbo` registry entry pointed at a repository that does not exist

- **Expected:** `scripts/model-manager.sh download large-v3-turbo` fetches a model.
- **Actual:** `registry/models.yaml` named `Systran/faster-whisper-large-v3-turbo`. The Hugging
  Face API answers 401 for it (no such public repository). faster-whisper 1.2.1 maps its own
  alias `large-v3-turbo` to `mobiuslabsgmbh/faster-whisper-large-v3-turbo`, and the API
  redirects (307) that name to `dropbox-dash/faster-whisper-large-v3-turbo` (MIT, CTranslate2,
  `model.bin` 1.6 GB, float16). The entry now names that repository. Proved: downloaded through
  the project's model manager, loaded by the server with `MODEL_NAME=large-v3-turbo`, and it
  transcribed 177 clips (three passes).
- **Repro:** `curl -s -o /dev/null -w "%{http_code}" https://huggingface.co/api/models/Systran/faster-whisper-large-v3-turbo`
  then the same for `dropbox-dash/faster-whisper-large-v3-turbo` (200).
- **Root-cause class:** a registry entry written from a naming pattern, never downloaded.
- **Invariant:** assert the artifact the user actually receives. A model entry is not done
  until the download has run.

## F3. The evidence does not pick a default, so the default stays

- **Expected:** one model clearly better for an English and Manglish speaker.
- **Actual:** turbo has fewer word errors with the US voice (49 vs 63) and the same with the UK
  voice (62 vs 62). End to end breeze is ahead, 52 vs 48, but turbo failed six cases breeze
  passed and breeze two that turbo passed, and of those eight one is the scorer and four passed
  on some repeat. The difference is inside the sorter's own run-to-run movement. Turbo as
  shipped is slower and larger on this CPU; with `COMPUTE_TYPE=int8` it is faster and smaller
  than breeze. `registry/models.yaml` still has `default: true` on `breeze-asr-25`.
- **Repro:** `python evals/audio/run_audio_eval.py report --results <file>` on each stored file.
- **Root-cause class:** a decision asked of a sample too small and too clean to carry it.
- **Invariant:** separate verified fact from assumption. Recommendation, not a measurement:
  try `MODEL_NAME=large-v3-turbo COMPUTE_TYPE=int8` on the owner's own recordings; decide after
  twenty or so real captures, corrected by hand, have gone through both models.

## F4. The registry `compute_type` does not decide what the server loads

- **Expected:** the `large-v3-turbo` entry says `compute_type: int8_float16`, so the server
  loads a quantised model.
- **Actual:** the CTranslate2 log says the float16 weights were converted to float32 (4.5 GB
  peak). `COMPUTE_TYPE` defaults to `default`, which follows the saved weights, not the entry.
  Breeze is saved as int8_float16 and loads as int8_float32, which is why it looked lighter.
  `COMPUTE_TYPE=int8` is the working control. Not fixed here: `app/` is another lane's.
- **Repro:** `MODEL_NAME=large-v3-turbo python -m uvicorn app.main:app`, read the first warning.
- **Root-cause class:** a config field that reads as a control and is not wired on this path
  (read from the log and `app/config.py`; the loader code was not traced line by line).
- **Invariant:** silent fallback is a lie. The log does say it; the registry does not.

## F5. Observations for the parent, no code changed

- `breeze-asr-25` reported `language: zh` for all 59 US-voice clips while writing English.
  Harmless today; it would matter if anything starts to branch on the language field.
- The live mis-hearing of 2026-11-12 (`collect it this Saturday` -> `Collected this
  Saturday`) did not reproduce: both models, both voices, four clips, all correct.
- `evals/score.py` keyword `y15` fails a correct note that spells the bike `Y-15`. Not edited
  (other lanes own `evals/score.py` and the cases). Proposed, in `evals/capture_cases.jsonl`,
  case `quote-motorcycle`: old `"must_contain": ["y15"]`, new `"must_contain": ["y15|y-15"]`.
  This loosens a keyword, it does not change an expected answer.
- `date-year-rollover` with the heard text `...by 8 this Saturday...` failed 3 of 4
  calls; the first came back due `2026-01-03` (expected `2027-01-02`). The clean-text run passed once. Worth a
  repeat on clean text: it may be a sorter weakness the single stored run did not show.
- Each sorter call through `asyncio.run` can print "Event loop is closed" from the
  google-genai client on teardown after a retry. Noise on stderr only; results unaffected.

## Measured

- `uv sync --extra dev` in the patched clone: exit 0. Both models downloaded with
  `scripts/model-manager.sh`.
- Speech to text through the running server, 59 clips per pass, five passes: breeze US and UK
  voice, turbo US and UK voice, turbo int8 US voice. 0 failed requests. Numbers above and in
  `evals/audio/README.md`.
- Sorting from the heard text, real `CaptureService._classify` via `evals/run_eval.py`,
  each case with its own date: breeze answered 59 correct 52, turbo answered 59 correct 48.
  One 503 and one timeout were retried and answered. No 429, no daily-quota stop.
- Repeat check: 6 cases x 3 calls, same heard text.
- Runner tests: 20 passed. Two were proved able to fail by mutation (daily-quota detection
  turned off; heard text replaced by the clean text): 1 failed each time, then restored.
- The artifact: on a second fresh clone at `56e5cf6`, `git am` of the three existing patches
  and then this one applied cleanly; `pytest evals -c /dev/null` there gave 46 passed (20 new,
  26 existing); `report` on the two stored result files reproduced 52 and 48.
- `make ci` in this repository: ok, 30 files, laptop-ASCII clean, 46 script tests passed.

## Not run

- A human voice, a real phone recording, the Shortcut on a phone. The voice is gTTS: one
  steady synthetic speaker, no noise. A person in a car park will be heard worse.
- Sorting for the UK voice and for the int8 pass (speech to text only), to spare the shared
  free-tier quota.
- A second full sorting pass per model. One run is one sample.
- Claude as the sorter. A GPU. The Apple `ggml` variant. Breeze with `language=en` forced.
- The whole upstream test suite on the four-patch tree (only `evals/` was run).
- Memory for the two UK passes. Timing was one pass on a shared 4-core cloud CPU.
