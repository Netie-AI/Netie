# freeroute-core stage 2 plan: gate wired and tested in the patch, build not proven here

Upstream `MiXaiLL76/auto_ai_router` at `4f8597503a` (Apache-2.0, Go), mode fork-rebrand,
product OpenVault, Netie name FreeRoute Core. Series: `0001-rebrand.patch` (stage 1, docs
and attribution) then `0002-gate.patch` (this stage). Replay is
`python3 scripts/ecosystem.py clone freeroute-core DIR` then `apply freeroute-core DIR`.
Everything below is measured on 2026-10-28 in a Linux container unless marked assumed or
not run. Catalog stage stays 1 (section 3).

## 1. What stage 2 means here

DR-0002 rule 5: stage 2 is "gate wired and tested". The catalog gate for this row reads
"Credentials are issued by OpenVault. The router holds no key of its own." The patch
wires that gate at the one place a key can enter the router, the config loader, and tests
it at the artifact the operator receives: the shipped example config, what `config.Load`
does with a config file, and which `Authorization` header the real proxy sends upstream.

Gate, all in `0002-gate.patch`:

1. `internal/config/openvault.go` (new). A `credential_source` block
   (`openvault_url`, `seat`, both `os.environ/` aware) and `applyNetieCustody`, called by
   `Load` after parse and before `Validate`:
   - every credential carrying `api_key`, `credentials_json` or `credentials_file`, literal
     or resolved from the environment, is refused with
     `credential <name>: inline <field> refused: FreeRoute Core holds no key of its own`;
   - a credential that needs a secret (every type except `proxy`, `air`, `vllm`, mirroring
     upstream `Validate`) with no source configured is refused with an error that names
     `NETIE_OPENVAULT_URL`;
   - with a source, the loader does `GET {openvault_url}/api/freeroute/credentials` with
     `Authorization: Bearer <seat>` (10 s timeout, 1 MB body cap), matches the returned
     entries to `credentials:` by name, and writes `api_key` / `credentials_json` into the
     pool. Unreachable, non-200, unparseable, or "issued nothing for a credential that needs
     a secret" each stop the router. It never starts half-keyed.
   - `NETIE_OPENVAULT_URL` alone, with no block in the file, is accepted (containers).
2. Dev override `NETIE_DEV_ALLOW_INLINE_KEYS=1` (exact value). Needed because the upstream
   `internal/config` tests write inline keys to temp files by design (36 `Load` calls in 3
   files). `netie_testmain_test.go` sets it for that package; every accepted key is logged
   at WARN with the credential name and the override's name; the gate tests clear it per
   case and prove the refusal without it. Not documented anywhere except
   `docs/getting-started/configuration.md` under "Local development only".
3. Default config and examples carry no provider key: `config.yaml.example` (every
   `api_key` and the `credentials_file` removed, `credential_source` added),
   `docs/getting-started/configuration.md` (full example, new "Credential source
   (OpenVault)" section, 9 snippet key lines removed), `docker-compose.yml` and
   `docker-compose.chain.yml` (inline `air` master keys and `${OPENAI_API_KEY}` removed,
   `NETIE_OPENVAULT_URL` env added), `examples/chain_mock/` (19 inline `sk-mock` and
   `sk-alpha/beta/gamma` keys removed from four configs; the demo's nginx mock now also
   answers `/api/freeroute/credentials` with the same inert keys for those 19 names, so the
   playground still runs with `NETIE_OPENVAULT_URL=http://mock:9100`).
4. Round-robin, priorities, fallback, rate limits and fail2ban are untouched: they read the
   same `CredentialConfig` values; only the origin of the secret changed.

Renamed where safe (user-visible, no identifier cascade): binary `freeroute-core`
(Makefile `BINARY_NAME`, Dockerfile, README quick start), Docker image `freeroute-core`
(Makefile, both compose files, chain_mock), compose service `freeroute-core`, the
`-config` flag help, the start-up log line, the `proxy_usage_format` migration error, the
"points to an Auto AI Router upstream" warning (and its two test assertions, pointed at
the new text), example OTEL `service_name` and `User-Agent` comment.

Not renamed, with the reason: Go module path `github.com/mixaill76/auto_ai_router` (531
files import it; needs a build to prove), Prometheus metric names `auto_ai_router_*`
(dashboards in `examples/grafana*.json` read them), Kafka `client_id` and OTEL
`service_name` code defaults and the otelhttp handler name (wire contracts to consumers),
`.github/workflows/release.yml` artifact name (publishes to upstream's registry; not ours
to run), `docs/logo.svg` (upstream's logo). Stage 3 list, also in `NETIE-ATTRIBUTION.md`.

## 2. Gate tests

`internal/config/netie_gate_test.go`, package `config`, 8 top-level cases (14 with
subtests), all using string literals so the file compiles on the upstream tree:

| case | asserts | expected on stage 1 tree | expected after 0002 |
|---|---|---|---|
| ExampleConfigCarriesNoProviderKey | no `api_key` / `credentials_file` / `credentials_json` under any credential of `config.yaml.example`; `credential_source.openvault_url` names `NETIE_OPENVAULT_URL` | fail (5 keys present, no source) | pass |
| LoaderRefusesInlineProviderKey (4 subtests) | `Load` errors on literal `api_key`, `os.environ/` `api_key`, `credentials_file`, `credentials_json`; error names field, refusal and `NETIE_OPENVAULT_URL` | fail x4 (loads fine) | pass |
| NoKeyAndNoSourceNamesOpenVault | error text `no key and no credential_source` plus env name | fail (upstream says `api_key is required`) | pass |
| KeysReachThePoolOnlyFromOpenVault | issue endpoint path and `Bearer ov_test_seat` seen by the stub vault; `api_key` and `credentials_json` land on the named credentials; rpm/tpm untouched; `air` credential stays keyless | fail (block ignored, `api_key is required`) | pass |
| EnvironmentAlonePointsAtOpenVault | no block, trailing slash on URL, no seat header sent | fail | pass |
| OpenVaultIssuesNothingOrIsDown (3 subtests) | `issued no key for it`, `OpenVault refused ... HTTP 403`, `OpenVault unreachable` | fail x3 | pass |
| DevOverrideIsLoud | with `=1` an inline key loads and WARN carries `NETIE DEV OVERRIDE`, `credential=dev_only`, `override=NETIE_DEV_ALLOW_INLINE_KEYS` | fail (loads, no log) | pass |
| DevOverrideNeedsExactValue | `=true` is not an override | fail (loads) | pass |

`internal/proxy/netie_gate_test.go`, package `proxy`, 2 cases on the real `Proxy` built by
the upstream's own `NewTestProxyBuilder` from a config `Load` filled from a stub vault:

| case | asserts | expected on stage 1 tree | expected after 0002 |
|---|---|---|---|
| RouterSendsOnlyOpenVaultIssuedKeys | 6 chat calls answer 200; the upstream saw only `Bearer issued-a` / `Bearer issued-b`; both used (round-robin) | fail (`Load` refuses the keyless file with `api_key is required`) | pass |
| Fail2BanAndFallbackOnIssuedCredentials | primary (issued key, answers 401) tried at most 3 times then banned; fallback (issued key) answers all 5 calls 200 | fail (same `Load` refusal) | pass |

Expected counts, not measured: 0 of 16 cases pass on the stage 1 tree, 16 of 16 after.
The two tables are a prediction from reading the code. Section 3 says why.

## 3. Build and test evidence: not run here

Measured: `go version` on the box is `go1.24.7 linux/amd64`; `go.mod` says `go 1.27.0`
and `GOTOOLCHAIN=auto` downloaded `go1.27.0` through the proxy (the toolchain is in the
module cache). Clone of the pin, `apply` of 0001, and the local baseline commit took under
2 seconds.

Not run, twice refused, on the untouched baseline tree before any file of this stage was
touched: `go build ./...` on 2026-10-22 was rejected by the operator mid-call, and the
same `go build ./...` on 2026-10-28 was denied by the session's auto-mode permission
classifier ("Code from External": compiling or running code from a downloaded tree). The
rule was not worked around: no `go vet`, no `go test`, no build of any package of the
upstream tree. `gofmt -l -e` on the four new and three edited Go files is clean (syntax
only; `gofmt` does not type-check). Every Go identifier the new code uses was read from the
upstream source (`resolveEnvString`, the `ProviderType*` constants, `CredentialConfig`
fields, `NewTestProxyBuilder`, `WithCredentials`, `WithMasterKey`, `ProxyRequest`,
`newIPv4Server`, `fail2ban.New(3, 0, ...)` with 0 meaning permanent).

Per the stage rule this stage stops at a PLAN: the catalog row stays at stage 1, the patch,
the tests and this contract are in the overlay. Stage 2 is claimed when, on a box that may
build the upstream tree, `go build ./...` and `go test ./...` pass on the baseline, the
gate tests fail there (16 cases), and both pass after 0002 with every baseline pass still
passing. Estimated 20 to 40 minutes once the build is allowed; the Go 1.27 toolchain is
already cached. Expected upstream deltas after 0002: none in `go build`; in `go test`, the
`internal/config` package runs under the TestMain override, and the two renamed warning
assertions in `internal/startup/validators_test.go` are pointed at the new text.

Assumed, not measured: the Docker image builds (`Dockerfile` only renames the output
binary), and the chain_mock playground starts with its nginx vault stand-in.

## 4. OpenVault key custody: integration contract

What the Netie repo says (read, not invented): `TAS/TAS-OPENVAULT.md` section 3, FreeRoute
identity is metering on issued `ov_` keys, not spoofable headers; section 4, FreeRoute is
OpenVault `:5000/v1`; `NETIE.md` section 3, exactly one key vault, any `env.local`
elsewhere is a cache synced from OpenVault; `scripts/crew_ov_gate.py`, the only OpenVault
endpoint contract in this repo, is `POST /api/crew/gate` (fail closed, never a skill body);
`netie/route.py` and the `scripts/freeroute_*.py` modules carry routing honesty
(execution shapes, free pool, headroom) and no credential-issue call. The custody contract
in `ecosystem/overlays/freeroute/PLAN.md` section 4 is reused as is: this fork holds no
provider key of its own in production; every leave-machine call carries an issued `ov_`
identity; subscription-login providers stay off (this upstream has none).

Not found in those files, therefore assumed and defined here as the minimal interface this
fork needs:

    GET {NETIE_OPENVAULT_URL}/api/freeroute/credentials
    Authorization: Bearer <ov_ seat issued to this router>      (optional on loopback)
    -> 200 {"credentials": [{"name": "<credential name>", "api_key": "...",
                              "credentials_json": "..."}]}
    -> anything else: the router does not start

Semantics the patch relies on: entries are matched by the credential `name` in the
router's config file, so the config file (routing policy) and OpenVault (secrets) can be
owned by different people; OpenVault decides which names a seat may receive; a name with
no entry is a refusal for types that need a secret and a no-op for `proxy`, `air`, `vllm`.
Open: whether OpenVault serves this on `:5000` next to `/v1` or on the management port;
rotation (this fork fetches once at start-up; a refresh interval or SIGHUP reload is not
wired); whether `server.master_key`, the router's own client-facing secret, should also be
issued; and the leave-machine gate (`/api/gate/check` today, `POST /api/crew/gate` once
OpenVault PR #44 lands) for calls this router makes, which the upstream data plane does
not call and this stage did not add.

## 5. What would make this stage 3

Build and tests green on both trees (section 3); the OpenVault endpoint above implemented
and this fork started against a live OpenVault with `NETIE_OPENVAULT_URL` set and a chat
call observed end to end; module path and metric names renamed behind one rebase plan with
the Grafana examples updated; rotation wired; the upstream logo replaced; counsel review
not needed for Apache-2.0 but the NOTICE obligation re-checked if upstream adds one.
