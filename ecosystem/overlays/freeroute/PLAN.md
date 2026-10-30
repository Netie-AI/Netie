# freeroute stage 2 plan: gate wired and tested, build not proven here

Upstream `diegosouzapw/OmniRoute` at `23a1148486` (MIT), mode fork-strip, product OpenVault.
Series: `0001-rebrand.patch` (stage 1, docs and attribution) then `0002-gate.patch` (this
stage). Replay is `python3 scripts/ecosystem.py clone freeroute DIR` then `apply freeroute DIR`.
Everything below is measured on 2026-10-05 in a Linux container with Node 22.22.0, unless
marked assumed or not done.

## What stage 2 means here

DR-0002 rule 5: stage 2 is "gate wired and tested". The gate this stage wires is the
refusal in the catalog row's `disable` list: providers that reuse an end user's Claude
Code, Codex, Copilot, Cursor or Antigravity subscription login, and any adapter that drives
another vendor's UI to dodge its meter. OpenVault key custody is NOT wired (section 4 is the
contract for it). Stage 2 is NOT set in the catalog (section 3, build). Stage 3 (shippable) is not claimed. Vendor terms of service for the
subscription-login providers are not counsel-reviewed.

## 1. Disabled by default

Each entry gives the upstream catalog file. The gate lives in one new module,
`open-sse/config/netieSubscriptionGate.ts`, and every section below reads it.

Subscription-login providers (9 ids, listed in the gate module with their aliases):

| id | alias | upstream file | why it is in the named class |
|---|---|---|---|
| claude | cc | `src/shared/constants/providers/oauth.ts`, `src/lib/oauth/providers/claude.ts` | Claude Code OAuth login |
| codex | cx | same, `src/lib/oauth/providers/codex.ts` | OpenAI Codex OAuth login |
| codex-app-server | cxa | `src/shared/constants/providers/noauth.ts` | drives the local Codex CLI app-server and its ChatGPT sign-in |
| github | gh | oauth.ts, `src/lib/oauth/providers/github.ts` | GitHub Copilot OAuth login |
| ghe-copilot | none | oauth.ts, `src/lib/oauth/providers/ghe-copilot.ts` | GitHub Enterprise Copilot OAuth login |
| cursor | cu | oauth.ts, `src/lib/oauth/providers/cursor.ts` | Cursor IDE OAuth login |
| cursor-api | cua | `src/shared/constants/providers/apikey/specialty-media.ts` | Cursor user key exchanged for an IDE session token, "bills to the Cursor plan" per its own authHint |
| antigravity | none | oauth.ts, `src/lib/oauth/providers/antigravity.ts` | Antigravity OAuth login |
| agy | none | oauth.ts, `src/lib/oauth/providers/agy.ts` | Antigravity CLI login import |

Adapters that drive another vendor's UI (33 ids, the whole web-cookie section):
`src/shared/constants/providers/web-cookie.ts`, every entry, including claude-web,
chatgpt-web, chatgpt-web-codex, copilot-web, copilot-m365-web, grok-web, gemini-web,
perplexity-web, deepseek-web, notion-web, poe-web and the token-based maxai and uc. The
class is "paste a browser session from a consumer web product and call its private
endpoints"; the section's own `riskNoticeVariant: "webCookie"` is the upstream's name for
it. Their executors in `open-sse/config/providers/registry/*` are dropped with them.

Where the gate bites (all in `0002-gate.patch`):

1. Catalog sections `OAUTH_PROVIDERS`, `NOAUTH_PROVIDERS`, `APIKEY_PROVIDERS`,
   `WEB_COOKIE_PROVIDERS` are filtered at module load, so `AI_PROVIDERS`,
   `getProviderById`, alias maps, canonical order and the dashboard catalog never see them.
2. Executor registry `REGISTRY` (`open-sse/config/providers/index.ts`) is filtered, so
   `PROVIDER_MODELS` and `GET /v1/models` carry none of their models and no executor can be
   dispatched.
3. OAuth flow map `src/lib/oauth/providers/index.ts` is filtered, so
   `/api/oauth/<provider>/<action>` answers "Unknown provider".
4. The upstream's own runtime retirement set (`src/shared/constants/providerRetirement.ts`,
   consumed by credential selection in `src/sse/services/auth.ts` and by
   `src/lib/db/providers.ts`) gains the 9 ids plus 6 aliases, so a stored connection row
   that predates the gate is refused before credential selection. Reused mechanism, no
   new one.

Opt-in: one environment flag, value exactly `1`, named only in the gate module and in the
test. It is absent from `.env.example`, `docs/reference/ENVIRONMENT.md` and every other
upstream doc; the module reads it through a constant so the upstream `check:env-doc-sync`
gate does not demand it be documented. Operators find it in this file: the Netie repo, not
the fork. Known limit: with the flag set, the server registers the providers but the
browser bundle is compiled without server env, so the dashboard catalog still hides them.
That limit is on the opt-in path only; the default-off path is what this stage proves.

Not gated, named so nobody assumes otherwise: the other `subscriptionRisk: true` entries
(kiro, qoder, kilocode, cline, clinepass, kimi-coding, grok-cli, zed-hosted, trae,
muse-code, codebuddy-cn, xai-oauth, devin-desktop, amazon-q, gitlab-duo, auggie, zcode,
xai, galadriel, predibase). They reuse some vendor's subscription too, but the catalog row
names five vendors and this stage does not widen it. Open: decide per vendor, or gate the
whole `subscriptionRisk` class. Also not gated: the MITM/TPROXY tooling under `src/mitm/`
that intercepts a local CLI's traffic to point it at this gateway. That is the consumer
direction (the user's CLI calls FreeRoute), not a provider, and is out of this stage.

## 2. Renamed where safe

Done: dashboard display name `APP_CONFIG.name` is FreeRoute; `freeroute` and
`freeroute-reset-password` added to `package.json` bin next to the upstream names; the CLI
program reports itself as `freeroute`.

Not done, with the reason:

- npm package name stays `omniroute`. `src/lib/system/autoUpdate.ts` runs
  `npm install -g omniroute@<latest>` and the update notifier checks the registry for the
  package's own name. Renaming to `freeroute` would point auto-update at whatever npm
  package carries that name. Not ours, so not safe until auto-update is disabled or
  repointed.
- Config directory stays `~/.omniroute`. It is hard-coded in four places that do not share
  a constant: `src/lib/dataPaths.ts`, `bin/cli/data-dir.mjs`, `electron/main.js` and
  `bin/omniroute.mjs` (lines 249 and 256). Changing one and missing another splits the CLI
  and the server onto different SQLite files. Stage 3 work: one constant, one migration.
- `@omniroute/open-sse` import path, `OMNIROUTE_*` env names, `bin/omniroute.mjs` file name:
  identifiers, DR-0002 rule 5 says those need a build to prove and this stage's build proof
  is partial (section 3).

## 3. Build and test evidence

Upstream test subset (16 files, chosen as the routing engine plus the provider registry and
the models listing, because the gate touches exactly those), run with the upstream command
`node --import tsx/esm ... --test` on each tree:

| tree | flag | files | tests | pass | fail | skipped |
|---|---|---|---|---|---|---|
| baseline (0001 applied) | absent | 16 | 294 | 294 | 0 | 0 |
| stage 2 | absent | 16 | 294 | 250 | 44 | 0 |
| stage 2 | set to 1 | 16 | 294 | 294 | 0 | 0 |

Files: routing-strategies, combo-routing-engine, circuit-breaker-failure-kind,
connection-circuit-breaker, settings-schema-routing-strategies, canonical-provider-order,
provider-alias-uniqueness, provider-alias-transitive-5918, provider-registry-models-guard,
passthrough-provider-aliases, provider-registry-github-copilot-targetformat,
cursor-apikey-provider, agy-provider, providers-page-utils, models-catalog-route,
models-catalog-model-exposure-list (all under `tests/unit/`).

The 44 default-mode failures are upstream tests that assert a gated provider is present
(agy, cursor-api, github targetFormat rows, claude and antigravity aliases in the models
catalog, the web-cookie taxonomy, and one combo SLA test whose candidate list names
`claude/`). None were skipped or edited. The same 294 pass with the flag, so the gate is
the only behavioural change. Open: upstream CI for this fork should run the
provider-presence tests under the flag and the gate test without it, as two jobs.

New test in the patch, `tests/unit/netie-subscription-login-gate.test.ts`, 4 tests:
listing in a child process without the flag, listing with the flag (and with a non-`1`
value), `GET /v1/models` with a stored `github` and `openai` connection, and credential
selection for `github`, `gh`, `claude`, `cursor-api`. Baseline tree: 0 of 4 pass. Stage 2
tree: 4 of 4 pass. The test registers all four before any top-level await because the
upstream runner uses `--test-force-exit`.

Typecheck: `tsc -p tsconfig.typecheck-core.json` exit 0 on baseline and on stage 2;
`check:open-sse-typecheck` 0 errors on stage 2.

Build: the full `npm run build` (Next.js 16 with Turbopack) was OOM-killed in this
container on the baseline tree at about 11.6 GB resident, before any file of this stage
was touched. The upstream's lighter documented profile, `build:backend` (dashboard pages stubbed,
standalone assembly skipped), was OOM-killed the same way on the baseline tree. So the
upstream build did not run here, before or after the change. Per the stage rule this stage
stops at a PLAN: the catalog row stays at stage 1, the patch, the test and this contract are
in the overlay, and the typecheck is the only compile evidence. Stage 2 is claimed when
`npm run build` passes on both trees in a box with more than 12 GB for the build process.

Not run: the upstream's bun-only checks (`check:provider-consistency`,
`check:known-symbols`), the full 5380-file unit suite, e2e, Electron. Assumed, not
measured: the Docker images build.

## 4. OpenVault key custody: integration contract

What `TAS/TAS-OPENVAULT.md` says (measured there on 2026-08-27, clone HEAD `62bb1c7`):

- FreeRoute in the Netie estate is OpenVault `:5000/v1`, not a process on `:20128`;
  "OmniRoute remaining as an external optional" (section 4).
- Keys: "One vault. `env.local` elsewhere is cache." Trust boundary enforced by the vault
  store; custody reopen #13 is still open in OpenVault STATUS (section 3).
- FreeRoute identity: metering on issued `ov_` keys, not spoofable headers, tests in
  `test_freeroute_metering.py` (section 3).
- Leave-machine and deploy: `/api/gate/check` and `ship/gate.py`, HUMAN_STOP on live
  HT1-HT5 (section 3). `POST /api/crew/gate` with skill ids is NOT on OpenVault main
  (PR #44 plus `docs/patches/openvault-crew-gate.patch`) (section 8).
- Circuit breaker in `route/breaker.py` trips on 408/500/502/503/504 (section 3).
- Vault SQLite is sealed; Redis is optional for FreeRoute buckets (section 6).
- `NETIE.md` section 3: OpenVault is consented custody; secrets enter because a human put
  them in and granted the call. There is exactly one key vault.

Contract derived from that, no API invented:

1. This fork holds no provider key of its own in production. Its upstream key store
   (`provider_connections.apiKey`, encrypted columns, `~/.omniroute/storage.sqlite`) is
   left alone in this stage and is to be treated as the `env.local` cache the TAS allows:
   filled from OpenVault, never the source of truth.
2. Every call that leaves the machine carries an issued `ov_` key as its identity and is
   metered by OpenVault, not by this fork's own usage tables.
3. A leave-machine call passes the OpenVault gate first. Today that is `/api/gate/check`
   on main; `POST /api/crew/gate` with skill ids is the target once OpenVault PR #44 lands.
4. Subscription-login providers stay off. A key that OpenVault issues is a provider API key
   the human put into the vault, never a replayed consumer session.

Open, in order:

- How this fork fetches a cached key from OpenVault (pull on connection test, push on
  grant, or `env.local` sync). TAS-OPENVAULT names the cache, not the sync protocol.
- Whether this fork runs at all, or whether its routing ideas (19 strategy names,
  auto-combo, quota-share) are ported into `OpenMW/openmw/openvault/route/` as the TAS and
  `TAS/ESTATE-GAP.md` already do for 15 sorts. The TAS keeps OmniRoute "external optional".
- Which OpenVault endpoint answers "may this provider key be used by this caller"; nothing
  in the TAS names one beyond the two gates above.
- Mapping this fork's `ov_`-less management auth (`requireManagementAuth`) to OpenVault
  seats.

## 5. What would make this stage 3

Config directory and package rename behind one constant with a migration; the full Next
build green in a box with enough memory; the Docker image built and started with the flag
absent and `GET /v1/models` checked on the running container; the custody sync protocol
decided and tested against an OpenVault clone; counsel review of the five vendors' terms.
