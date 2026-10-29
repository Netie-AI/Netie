# 2026-10-22 - Crew Edge stage 2 (ZeroClaw gate wired and tested)

Preflight: KB `D:\Netie-KB` absent in this cloud box. `docs/subagents_findings/INDEX.md`
and both findings it lists were read, plus the airgpt, freeide and freeroute stage 2
findings on their branches. PREFLIGHT: PARTIAL. No subagents spawned; one session
cloned, built, edited, tested and cut the patch directly. Started 2026-10-22 on Fable,
halted by the founder, resumed 2026-10-29 on Opus at the founder's "Continue".

Branch `claude/stage2-crew-edge`, base `claude/netie-ecosystem-rebrand-uq9q3z` (PR #43).
Upstream zeroclaw-labs/zeroclaw at f7bd2b9e94 (MIT OR Apache-2.0), overlay
`ecosystem/overlays/crew-edge/0002-gate.patch`.

## F1. Upstream defaults reach vendors directly and offer four subscription logins

- **Expected (catalog gate, DR-0002 rule 6):** one default model endpoint, OpenVault
  `${NETIE_OPENVAULT_URL}/v1`, no key field in the default config, no provider that
  reuses an end user's subscription login.
- **Actual on the stage 1 tree:** Quickstart lists 82 provider families, OpenRouter
  first; the OpenAI-compatible `custom` family is 61st and asks for `api_key`. It
  offers `copilot`, `gemini_cli`, `grok_cli` and `kilocli`, the `openai-codex` login
  alias, and the `codex` and `setup_token` auth modes. Five builtin tools
  (`claude_code`, `claude_code_runner`, `codex_cli`, `gemini_cli`, `opencode_cli`)
  drive another vendor's CLI on the user's login.
- **Fix:** `openvault` is the first Quickstart choice. It writes
  `[providers.models.custom.openvault]` with `uri` set to `${NETIE_OPENVAULT_URL}/v1`
  (default `http://127.0.0.1:5000/v1`) and no `api_key`. A key on that entry is
  refused. The four families are dropped from the picker and refused by the provider
  factory; both auth modes and the alias are refused; the five tools never run.
- **Repro:** `clone` + `apply` crew-edge, then
  `cargo test --locked -p zeroclaw-runtime --lib netie_gate`. Stage 1: 0 of 10 pass.
  Stage 2: 10 of 10.
- **Root-cause class:** a multi-provider upstream default standing in for a product
  decision (same class as airgpt F1).
- **Invariants:** assert the artifact the operator receives (the picker list, the
  config file re-read from disk by the real loader); prove a gate can fail first.

## F2. Porting the Python body check literally broke upstream's own delegate tool

- **Expected:** `crew_tool_wrap.run_tool` refuses payloads carrying `skill_body`,
  `prompt`, `instructions` or `transcript`, so the Rust tool gate should too.
- **Actual:** the first port refused every tool argument named `prompt`. Upstream
  `delegate`, `spawn_subagent` and `cron_add` take `prompt` as a required input, so
  delegation was refused in production. About 40 delegate tests failed.
- **Fix:** tool arguments never leave the machine; only the gate ask does, and the ask
  is ids only (checked, and asserted in `allowed_tool_posts_ids_only` and
  `prompt_argument_stays_local_and_is_not_sent`). Arguments are refused only for
  `skill_body`, since skills are passed by id.
- **Root-cause class:** a contract written for one call shape (a Crew child job
  payload) applied to a different one (a local tool input).
- **Invariants:** a control that blocks legitimate work is itself a failure; re-check
  after hardening. It was the upstream suite, not the gate test, that caught it.

## F3. Fail-closed tool gate turns every upstream tool test red without a harness

- **Expected:** upstream suites keep testing upstream behavior.
- **Actual:** with no OpenVault listening, the first full run refused every tool:
  169 failures against 8 on baseline (channels 7, providers 11, runtime 151).
- **Fix:** a test-harness transport that allows every ask, installed only under
  `cfg(any(test, feature = "test-util"))`. It forwards asks under the reserved run id
  `netie-gate-turn` to the real HTTP transport, so the gate test still exercises the
  shipped path. The ask is built and checked before it reaches any transport.
  `shipped_default_transport_is_http` asserts the shipped default, and
  `cargo tree -e normal,build,features -i zeroclaw-runtime` on the binary shows
  `test-util` 0 times: it arrives only through dev-dependencies.
- **Root-cause class:** a gate on the single execution point touches every test that
  executes a tool.
- **Invariants:** never weaken or skip a check to force green (no test skipped or
  ignored; the ignored set is identical before and after); prove the default-off path
  in the gate test.

## F4. Eleven upstream tests asserted the behavior the gate removes

- 5 in `zeroclaw-providers` (`factory_copilot`, `factory_grok_cli`,
  `factory_kilocli`, `factory_all_canonical_model_providers_create_successfully`,
  `listed_model_providers_are_constructible`) and 6 in Quickstart (Claude alias with
  setup-token, Codex auth mode, Codex alias, Codex field rows, Gemini CLI runtime
  defaults, channel picker labels). Each was rewritten to assert the gated outcome
  through `crate::netie` constants. None was deleted or ignored. Where the original
  intent survives it is kept: Codex still persists no key, and the `claude` alias
  still canonicalizes to `anthropic` with a Console key.
- **Root-cause class:** upstream tests pin upstream product decisions.
- **Invariant:** a skipped test is a failing test.

## F5. The secrets scan flags upstream's fake Claude token carried in the patch

- **Expected:** `scripts/secrets_scan.py` clean on the new overlay.
- **Actual:** "Anthropic live key in ecosystem/overlays/crew-edge/0002-gate.patch". The
  match is `sk-ant-oat01-test-token`, a fake key in upstream's Quickstart tests. Any
  hunk within 3 lines of it carries it as context or as a removed line, so a patch
  that rewrites that test cannot avoid it. Renaming upstream's fixture still left it
  on the removed lines.
- **Fix:** `UPSTREAM_FIXTURES` in `secrets_scan.py`, an exact-literal list with one
  entry, matched as a whole token. The first version used substring removal. The new
  test `test_upstream_fixture_is_exact_literal_only` caught that a longer key starting
  with the fixture then passed. The bounded match fixes that, and the test fails
  against the naive version (run, 1 failure). Upstream's fixture is left as shipped.
- **Root-cause class:** patches carry upstream test data verbatim; a scanner tuned
  for this repo's own fixtures (`sk-ant-test-`) meets another project's convention.
- **Invariants:** never weaken a check to force green (one exact literal, not a
  pattern; a live-shaped key still fails); a control that blocks legitimate work is a
  failure; prove a gate can fail.

## Measured before/after

Box: 4 cores, 15 GB RAM, cargo 1.97.0. Scope is the upstream CI test job narrowed to
the five crates the patch touches, `--lib`, debug profile with
`CARGO_PROFILE_DEV_DEBUG=0` and `CARGO_INCREMENTAL=0` (CI sets the latter).

| Measure | Stage 1 | Stage 2 |
|---|---|---|
| `cargo test --no-run` (5 crates, lib), empty target | exit 0, 689 s (includes crate download) | exit 0, 488 s |
| `cargo test` wall | 126 s | 104 s |
| zeroclaw-channels lib | 1966 pass, 1 fail, 2 ignored | 1966 pass, 1 fail, 2 ignored |
| zeroclaw-config lib | 1762 pass | 1762 pass |
| zeroclaw-infra lib | 311 pass | 312 pass (+1 ids-only test) |
| zeroclaw-providers lib | 1913 pass, 6 fail, 4 ignored | 1920 pass, 6 fail, 4 ignored (+7 gate unit tests) |
| zeroclaw-runtime lib | 5448 pass, 1 fail, 8 ignored | 5459 pass, 0 fail, 8 ignored (+10 gate test, +1 flake) |
| Ignored tests, by name | 14 | the same 14 |
| Gate test `netie_gate` | 0 of 10 pass (10 ran) | 10 of 10 pass (10 ran), same on 3 full reruns |
| `cargo build -p zeroclaw` (debug binary) | exit 0, 271 s, 0 warnings | exit 0, 288 s, 0 warnings |
| `zeroclaw config get channels.session_backend` | `sqlite` | `ids-only` |
| Patch | | 69,146 bytes, 12 files, 1309 insertions, 48 deletions |
| Replay `git write-tree` | | `bec08417dc0e` on both checkouts |
| LICENSE-MIT sha256 | `69ad6d0b...bcc94` | unchanged; LICENSE-APACHE, NOTICE byte-identical |

The 7 failures common to both columns are upstream and environmental: 5 share the
poisoned `env_lock` after `bedrock::tests::env_vars_take_precedence_over_credential_process`,
`bedrock::tests::chat_fails_without_credentials` gets a decode error instead of a
credentials error, and `tts::tests::edge_tts_removes_temp_output_when_read_fails` runs
as root (uid 0 can read the file the test makes unreadable). Not root-caused further.
`daemon::tests::pricing_refresher_runs_with_the_gateway_disabled` failed once on
baseline and passed 4 of 4 on stage 2: an upstream flake, not a fix.

The first full workspace build (`cargo test --workspace --no-run`, debuginfo on)
filled the session disk at 892 s on the untouched baseline. That is why the scope is
the five touched crates.

## Not done / assumed

- **Assumed, not measured:** OpenVault accepts tool ids under `kind=runtime` and
  channel ids under `kind=service`, `id=channel.<type>`. Whether `/v1` needs a seat
  token, and whether it serves `/v1/models`, is not measured. No live OpenVault was on
  this box; the gate sends no seat token.
- **Not run:** workspace crates the patch does not touch (gateway, tools, memory,
  plugins, eval, apps), integration tests under `tests/`, `cargo clippy`, release and
  `ci` profiles, the web dashboard.
- **Not gated:** an operator-configured vendor provider with its own `api_key` still
  works; Codex and setup-token credentials already on disk are refused only at
  Quickstart; cron delivery and one-shot sends to a channel skip the leave-machine
  ask; memory backends, the ACP session store and logs can still hold conversation
  text.
- **Stage 3 renames left:** every crate, package and binary is still `zeroclaw*`, plus
  CLI help, `~/.zeroclaw`, `ZEROCLAW_*` env vars, the systemd unit and dashboard
  strings. Only the channel server banner changed.
- `scripts/test_sibling_patches.py` is red on base and on this branch: 9 of 10 today,
  measured on an untouched worktree of the base branch on 2026-10-29. F2 of
  `2026-10-05-ecosystem-lane.md` recorded 8 of 10; one more sibling moved since. Not
  touched, not skipped. Every other `make ci` gate is green on this branch.
- `scripts/secrets_scan.py` and its test changed in this branch (F5). Parallel wave 2
  sessions may touch the same file.

## Stage 3 increment (2026-10-29, `0003-stage3.patch`)

Resumed on the founder's "Dont stop ... ready to be lauch towmorrow". The other seven
wave 2 sessions were messaged with that instruction. Catalog stage stays 2: see F9.

### F6. Self-update would replace Crew Edge with upstream ZeroClaw

- **Expected:** a fork's update path installs the fork.
- **Actual:** `zeroclaw update` fetches `api.github.com/repos/zeroclaw-labs/zeroclaw/releases`
  and swaps the running binary. One operator command removes every Netie gate,
  including the subscription-login refusals.
- **Fix:** `commands::update::run` refuses with the gate message. Upstream's body is
  kept as a private function so the overlay rebases. `update --check` still reports
  upstream versions, and its help says installing is disabled.
- **Repro:** `zeroclaw update --force` on the built binary: exit 1, `Refused by Netie
  gate: self-update installs upstream ZeroClaw over Crew Edge ...`.
- **Root-cause class:** an upstream channel back into the vendor's release stream; a
  fork is only a fork until its updater runs.
- **Invariants:** assert the artifact the operator receives (the real binary run);
  a control that can be undone by one command is not a control.

### F7. Stored subscription credentials were refused only in Quickstart

- **Expected (stage 2 "Not done"):** a Codex or Claude setup-token credential already
  on disk is refused when a provider is built, not only at setup.
- **Fix:** the OpenAI factory refuses `requires_openai_auth`, the legacy `openai-codex`,
  `openai_codex` and `codex` spellings are refused, and the Anthropic factory refuses a
  resolved key starting `sk-ant-oat01-`. Console keys still build.
- **Root-cause class:** a gate at one entry point (setup) standing in for the choke
  point (construction).
- **Invariant:** fix the root-cause class, not the symptom.

### F8. Cron delivery and one-shot sends skipped the leave-machine ask

- **Fix:** `deliver_announcement` and `send_channel_message` ask OpenVault
  leave-machine (`kind=service`, `id=channel.<type>`) before sending; a refusal is the
  returned error. The test-harness transport also forwards asks whose child id holds the
  reserved `netie-gate-turn`, so the channels gate test reaches the real HTTP path.
- **Root-cause class:** same as F7: the stage 2 gate sat on startup, not on every
  outbound path.

### F9. Why the stage stays 2

- Stage 3 means shippable. Not provable here: no live OpenVault was available, so the
  crew gate kinds (`runtime`, `service`), the seat token and `/v1/models` are assumed.
  With no OpenVault answering, every tool call, non-CLI channel and delivery is refused
  by design, so Crew Edge does nothing useful until an OpenVault implementing
  `POST /api/crew/gate` runs at `NETIE_OPENVAULT_URL`.
- Crate, package and binary names are still `zeroclaw*`; the binary is `zeroclaw`.
- **Launch-readiness, measured vs assumed:** measured in this container: build, the
  six-crate suites, the real `--help`, `config --help`, `update` refusal and default
  session backend. Assumed: OpenVault's crew gate contract, any network path, any
  channel against a real service, and any vendor terms of service.

### F10. Brand strings live in Fluent, not in the clap literal

- **Expected:** editing `#[command(about = ...)]` changes `--help`.
- **Actual:** the first build still printed upstream's slogan: `cli-about` in
  `locales/en/cli.ftl` overrides the literal at runtime. Found only by running the binary.
- **Fix:** `cli-about` and 15 product-name messages renamed, keyed per message across
  all 5 locales (71 lines). A locale that phrases a message without the brand is left
  as translated and reported. The companion app, firmware, OpenClaw migration and the
  skill-audit and doctor messages keep upstream's name because they name real upstream
  artifacts.
- **Invariant:** assert the artifact the user receives; a unit test of the literal
  would have passed.

### Measured, stage 2 tree vs stage 3 tree

Same box and profile as above, plus the root `zeroclaw` crate (`--lib --bins`),
because the CLI rename and self-update gate live there.

| Measure | Stage 2 tree | Stage 3 tree |
|---|---|---|
| New gate cases (runtime 3, channels 2, update 1) | 0 of 6 pass, 6 ran | 6 of 6 pass |
| All gate cases (`netie_gate`, both crates) | 10 of 10 (runtime only) | 15 of 15 |
| zeroclaw-channels lib | 1966 pass, 1 fail | 1968 pass, same 1 fail (+2 gate) |
| zeroclaw-providers lib | 1920 pass, 6 fail | 1922 pass, same 6 fail (+2 unit) |
| zeroclaw-runtime lib | 5459 pass | 5462 pass (+3 gate) |
| zeroclaw-config, zeroclaw-infra lib | 1762, 312 pass | 1762, 312 pass |
| zeroclaw lib, main, acp-bridge | 278, 532, 19 pass | 279, 533, 19 pass (update test compiles into lib and main) |
| Ignored tests, by name (5 crates) | 14 | the same 14 |
| `cargo build -p zeroclaw` | exit 0, 0 warnings | exit 0, 211 s, 0 warnings |
| `zeroclaw --help` first line | `The fastest, smallest AI assistant.` | `Crew Edge: Netie's single-binary agent runtime. ...` |
| `zeroclaw status` title | `ZeroClaw Status` | `Crew Edge Status` |
| `zeroclaw update --force` | contacts GitHub releases | exit 1, `Refused by Netie gate: self-update ...` |
| Patch | | `0003-stage3.patch`, 75,681 bytes, 19 files |
| Replay of clone plus 0001, 0002, 0003 | | `git write-tree` `a2f24b4e9f22` on both checkouts |

12 more upstream tests were rewritten to assert the gated outcome: 7 that built a
provider from a Codex login and 5 that pinned the old brand in the renamed messages.
With the 11 in F4 that is 23 in total. None was deleted or ignored. The
daemon pricing-refresher flake failed once more on one stage 3 run and passed on the
final run; it is upstream's.
