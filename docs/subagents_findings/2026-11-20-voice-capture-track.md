# 2026-11-20 - voice capture track: accuracy from audio, Docker

Preflight: KB `D:\Netie-KB` absent in this cloud box. `docs/subagents_findings/INDEX.md` and
`2026-11-12-voice-capture.md` read. PREFLIGHT: PARTIAL (same class as the 11-12 F1 and F4:
packaging and verification left unrun by an earlier session).

Branch `claude/voice-capture`, from `claude/friendly-feynman-x4hd1v` (draft PR #59). Fork:
`shdennlin/whisper-wrap` at `56e5cf6` (MIT, class A), patches `0004` (audio eval) and `0005`
(Docker). Not a Netie product; not in the catalog, `NETIE.md` or `STATUS.md`.

Shape: one executor session did both parts itself (the work is serial on one clone and one
free Gemini key at 15 requests a minute, so there was nothing to parallelise). A different
agent replays the series; see "Replay" below.

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
