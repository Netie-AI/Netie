# 2026-10-22 - freeroute-core stage 2 (Auto AI Router custody gate; build not run)

Preflight: KB `D:\Netie-KB` absent in this cloud box. `docs/subagents_findings/INDEX.md`
read (2 rows) plus the three wave 1 findings and overlays on their branches (airgpt,
freeide, freeroute). PREFLIGHT: PARTIAL. No subagents spawned; one session read, edited,
cut and replayed directly. Started 2026-10-22, halted by the operator mid-build, resumed
2026-10-28 on a relayed founder instruction (crew-agent session). Everything measured
below is from 2026-10-28 unless dated.

Branch `claude/stage2-freeroute-core`, base `claude/netie-ecosystem-rebrand-uq9q3z`
(PR #43). Upstream MiXaiLL76/auto_ai_router at 4f8597503a (Apache-2.0, Go), overlay
`ecosystem/overlays/freeroute-core/0002-gate.patch`, plan
`ecosystem/overlays/freeroute-core/PLAN.md`. Catalog stage stays 1.

## F1. The upstream's only credential source is the config file

- **Expected (catalog gate):** "Credentials are issued by OpenVault. The router holds no
  key of its own."
- **Actual on the stage 1 tree:** `config.CredentialConfig` has `api_key`,
  `credentials_file` and `credentials_json`; `Load` resolves `os.environ/` and `Validate`
  demands a key for every type but `proxy`, `air`, `vllm`. `config.yaml.example` ships one
  literal OpenAI-shaped placeholder, three `os.environ/` keys, one service-account path
  and one `air` master key; `docker-compose.chain.yml` ships three inline `air` keys and
  `${OPENAI_API_KEY}` three times; `examples/chain_mock` ships 19 inline keys.
- **Fix:** `internal/config/openvault.go`: `credential_source` block, inline keys
  refused by `Load` (literal or env, all three fields), pool filled from
  `GET {NETIE_OPENVAULT_URL}/api/freeroute/credentials` matched by name, start refused on
  unreachable, non-200, or nothing issued. Every example and doc snippet stripped of keys;
  the chain_mock nginx mock doubles as the demo vault. Dev override
  `NETIE_DEV_ALLOW_INLINE_KEYS=1` logs every accepted key at WARN; it exists because 36
  upstream `Load` tests write inline keys.
- **Repro:** `python3 scripts/ecosystem.py clone freeroute-core D && apply freeroute-core D`,
  then `go test ./internal/config/ ./internal/proxy/ -run TestNetieGate -v`. Predicted
  (not measured, F3): 0 of 16 cases pass on the stage 1 tree, 16 of 16 after.
- **Root-cause class:** a single-process product's "bring your own key" default standing
  in for a custody decision. No label to gate on here; the gate sits on the one code path
  a secret can enter (the loader) and on what the proxy sends upstream.
- **Invariants:** assert the artifact the customer receives (example config parsed by the
  real loader; the `Authorization` header the real `Proxy` sends); fix the root-cause
  class (all three secret fields, literal and env, not just `api_key`).

## F2. Stage 1 attribution carried the wrong pin

- **Expected:** `NETIE-ATTRIBUTION.md` names the catalog pin `4f8597503a`.
- **Actual:** it said `175a300c62`, the upstream HEAD when the rebrand tool probed, not
  the pin `ecosystem.py clone` checks out. `overlay.json` and the catalog agree on
  `4f8597503a`; only the prose was wrong.
- **Fix:** corrected inside `0002-gate.patch` with the old value noted.
- **Repro:** `grep pinned ecosystem/overlays/freeroute-core/0001-rebrand.patch`.
- **Root-cause class:** two sources of truth for one fact (`pin_catalog` moved the pin
  after the attribution text was rendered). Likely shared by other stage 1 overlays
  written in the same run; not checked here.
- **Invariant:** never hand-author a generated artifact; the fix for the class is for the
  rebrand tool to render the pin from `overlay.json`, not from the probe.

## F3. The upstream could not be built or tested in this box

- **Expected:** `go build ./...` and `go test ./...` before and after, as the brief asks.
- **Actual:** `go build ./...` on the untouched baseline was rejected by the operator on
  2026-10-22 and denied by the auto-mode permission classifier ("Code from External") on
  2026-10-28. Not worked around: no `go vet`, no `go test`, no partial build. `gofmt -l -e`
  on every new and edited Go file is clean (syntax only). The Go 1.27.0 toolchain the
  module asks for did download (`GOTOOLCHAIN=auto`, box has 1.24.7), so a permitted run
  needs no network.
- **Measured elsewhere (2026-10-29):** the crew-agent session
  (`session_018ZvvmbN2JWHKQt8j1cdxfY`) built head 39de8ee in its own container, read-only:
  `go build -p 2 ./...` exit 0 on the stage 1 tree (167.3 s cold) and on the series tree
  (21.3 s warm); `go vet` exit 0 with the gate files on both trees; replay hash and LICENSE
  sha256 equal to F4. `go test` was denied there by the same classifier. Logs stay in that
  container; cited, not reproduced.
- **Consequence:** stage stays 1, exactly as freeroute did on its OOM. The 16 gate cases
  and the "every baseline pass still passes" claim are predictions from reading the code,
  listed per case in PLAN.md section 2.
- **Root-cause class:** environment policy, not code; measured before any change.
- **Invariants:** say what is measured and what is assumed; do not weaken or route around
  a control; adversary is not the verifier (the parent replays on a box that may build).

## F4. Replay held

- `0002-gate.patch`: `git diff --binary` against the local baseline commit, 66,194 bytes,
  23 files, 876 insertions, 91 deletions. Fresh `clone` plus `apply` (0001 then 0002)
  gives `git write-tree` `087eeeab3c3606853b7c2581428fba3e834d907b` on both checkouts.
  LICENSE sha256 `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`,
  equal to the catalog. No NOTICE upstream. Zero em dashes, en dashes or curly quotes on
  added lines (two inherited ones on edited lines were rewritten).
- **Invariant:** never hand-author a generated artifact; the overlay is cut by git.

## Measured before / after

| item | before (stage 1 tree) | after (0002 applied) |
|---|---|---|
| `go build ./...` | denied here; exit 0 measured by crew-agent session (167.3 s) | denied here; exit 0 measured by crew-agent session (21.3 s) |
| `go test ./...` | not run (denied) | not run (denied) |
| gate cases (`TestNetieGate*`) | predicted 0 of 16 pass | predicted 16 of 16 pass |
| `gofmt -l` on touched Go files | n/a | clean |
| `go vet` with the gate files | exit 0 (crew-agent session) | exit 0 (crew-agent session) |
| credentials with an inline key in `config.yaml.example` | 5 of 6 | 0 of 6 |
| inline keys in `docker-compose.chain.yml` + `examples/chain_mock` | 6 + 19 | 0 + 0 |
| replay tree hash | n/a | equal on both checkouts |
| LICENSE sha256 | catalog value | unchanged |
| `scripts/ecosystem.py validate` / `render --check` / `test_ecosystem.py` / `secrets_scan.py` | ok | ok (22 tests) |
| `scripts/test_sibling_patches.py` | 10 tests, 9 failures | 10 tests, 9 failures |

## Launch readiness (what an operator needs for FreeRoute Core to serve a request)

| need | status |
|---|---|
| A built `freeroute-core` binary or the `freeroute-core:latest` image (`make build`, `make docker-build`) | build measured green by the crew-agent session on head 39de8ee; image build assumed |
| `config.yaml` with `server.master_key`, credentials as routing policy (name, type, base_url, rpm, tpm), no keys | shipped as `config.yaml.example`; parsed by the real loader in gate case 1 (predicted, `go test` unmeasured) |
| An OpenVault reachable at `NETIE_OPENVAULT_URL` that answers `GET /api/freeroute/credentials` with a JSON list keyed by credential name | ASSUMED: OpenVault does not serve this endpoint today (nothing in `TAS/TAS-OPENVAULT.md` or `scripts/crew_ov_gate.py` names it). Without it the router refuses to start, by design. Until OpenVault ships it, the only way to run the fork is the loudly logged dev override, which is not a launch posture |
| `NETIE_OPENVAULT_SEAT`, the router's own `ov_` identity | optional in the patch; whether OpenVault requires it is OpenVault's call, not measured |
| Provider accounts whose keys the human has put into OpenVault | outside this fork; NETIE.md section 3 (consented custody) |
| Optional Redis (`redis:` block) for shared rate-limit buckets, LiteLLM DB, Kafka, OTEL | upstream features untouched; not needed for a single instance |

Verdict: not launchable tomorrow as a product. The fork is build-green and key-free, but its
one credential source is an OpenVault endpoint that does not exist yet, and its gate tests are
unmeasured. The shortest path to a working product is (1) OpenVault implements the endpoint
above, about one route plus a seat check, (2) `go test` is allowed on this fork once, (3) one
end-to-end chat call through OpenVault `/v1` to this router to a real provider, observed.

## Not done / assumed

- Not done: the upstream build and test suite (F3); catalog stage not raised; `INDEX.md`
  and `STATUS.md` not edited (parent aggregates); `go.mod` module path, metric names,
  telemetry defaults, release workflow, upstream logo (stage 3 list in the attribution).
- Assumed: the OpenVault issue endpoint `GET /api/freeroute/credentials` with a bearer
  seat and a JSON list. Nothing in `TAS/TAS-OPENVAULT.md`, `scripts/crew_ov_gate.py`,
  `netie/route.py` or the `scripts/freeroute_*.py` modules names a credential-issue
  endpoint; PLAN.md section 4 defines the minimum and marks it assumed.
- Assumed: the Docker image and the chain_mock playground build and start after the
  rename and the key strip.
- Reported, not touched: `scripts/test_sibling_patches.py` is red on the base and on this
  branch alike, 9 of 10 today (8 of 10 on 2026-10-05; the sibling HEADs moved again). F2
  of `2026-10-05-ecosystem-lane.md` stands.
