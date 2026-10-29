# 2026-10-22 - FreeBuild stage 2 (openship gate wired and tested)

Preflight: KB `D:\Netie-KB` absent in this cloud box. `docs/subagents_findings/INDEX.md`
read: two rows (ecosystem lane, wave 1 sessions), plus the three wave 1 stage 2 findings on
their branches. PREFLIGHT: PARTIAL. Work ran 2026-10-22 (clone, install, mapping) and
2026-10-28 (everything else) in one session with three parallel subagents, each owning a
disjoint file set in one shared upstream checkout; the baseline was measured in a separate
git worktree of the same clone with hardlinked node_modules.

Branch `claude/stage2-freebuild`, base `claude/netie-ecosystem-rebrand-uq9q3z` (PR #43).
Upstream oblien/openship at 3d33f5d31e (Apache-2.0), overlay
`ecosystem/overlays/freebuild/0002-gate.patch`.

## Session shape

| Count | Lens | Model | Why |
|---|---|---|---|
| 1 | claim_deploy gate: lifecycle, API presenter, dashboard pill, 21 gate cases | Opus, medium | needs tracing where the deploy URL comes from across three pipelines |
| 1 | vendor assets: cdn.oblien.com and Gellix strip, built-asset gate test | Sonnet | mechanical, 120 known references |
| 1 | safe renames: dashboard brand constant and copy, CLI help, attribution file | Sonnet | mechanical, bounded by an explicit do-not-touch list |
| parent | baseline and after measurements, .env.example vendor key, integration, patch cut, replay, docs | Fable | owns the numbers and the claim |

Shared context: one working tree, so each lane saw the others' edits and two cross-lane
misses surfaced in the full dashboard suite (a copy test tracking packages/core, a
grammar slip "an FreeBuild"), both fixed by the parent.

## F1. No upstream path observes a deploy URL, so nothing can honestly be live

- **Expected (catalog gate, `scripts/freebuild_honesty.py`):** the fork shows "live" only
  after claim_deploy succeeds on an observed URL; a simulated or constructed URL is never
  live.
- **Actual on the stage 1 tree:** every successful deploy writes status `ready` and the
  dashboard turns any active deployment into the green "Live" pill
  (`apps/dashboard/src/utils/project-status.ts`). The URL the lifecycle records is never
  probed: docker and bare runtimes return no URL; cloud builds `https://${customDomain}`
  (`packages/adapters/src/.../cloud.ts:2064`) or passes the vendor API's answer through
  unprobed; compose builds `https://${route.hostname}`
  (`compose/deploy.service.ts:3397`). The readiness probe and portCheck test the
  container port, not the public URL.
- **Fix:** `netie-claim.ts` mirrors report_deploy rule for rule with the same denial
  strings; `onSuccess` computes the verdict and writes it with the `ready` outcome as
  `meta.netieClaim` (one write, so the upstream write-count assertions still hold); the
  API presenter adds `live` and `netieClaim`; the project payload adds
  `activeDeploymentLive`; the pill reads "Deployed, unclaimed" (new `ProjectStatus`
  `unclaimed`, nine locales) until a LIVE claim exists. With `NETIE_OPENVAULT_URL` set the
  claim also POSTs `/api/crew/gate` (kind service, id freebuild, intent leave) and fails
  closed on anything but `allowed: true`; unset, the verdict says `gate: "none"`.
- **Consequence, stated plainly:** on this patch no deploy is ever shown live. That is the
  Netie posture (refuse rather than guess) and the first stage 3 item: an observation step
  that probes the routed URL and passes it as `observedUrl`.
- **Repro:** `clone freebuild D && apply freebuild D`, then the five gate files in
  `overlay.json` `stage2.gate_test`. Stage 1 tree: 21 cases, 20 fail (module missing,
  `live` undefined, pill green without claim), 1 passes trivially (old code calls every
  active deployment live). Stage 2 tree: 21 of 21 pass.
- **Root-cause class:** a deploy platform's "ready" is "the container started", and the UI
  promoted that to "live" with no observation in between.
- **Invariants:** assert the artifact the customer receives (the API JSON and the pill, not
  the lifecycle internals); silent fallback is a lie (gate none vs openvault is on the
  verdict); prove the gate can fail (baseline run recorded red).

## F2. Vendor fonts and CDN were in 120 places, two of them vendored binaries

- **Expected:** stage 1 strip list already empty of them (`stripped: []`), so a few CSS
  lines.
- **Actual:** 120 matches: four `fonts.css` and `globals.css` files (dashboard, web,
  email), CDN preconnect tags in the web layout, the desktop loading screen importing two
  vendored `Gellix-*.woff2` files (40 KB each, tracked in git), `CLOUD_ICON_BASE_URL`
  pointing icons at `cdn.oblien.com/static/png-icons` for cloud mode, a screenshot script
  fetching the font at run time, and a docs HTML file with three base64-embedded woff2
  faces.
- **Fix:** system font stack everywhere, binaries deleted, `CLOUD_ICON_BASE_URL` equals the
  local `/icons` path (export kept so upstream imports compile), docs rewritten. Gate test
  `apps/dashboard/src/netie-no-vendor-assets.test.ts`: zero matches in tracked text files
  (NETIE-ATTRIBUTION.md and CHANGELOG.md exempt), zero Gellix binaries tracked, zero
  matches in `.next/static` css and js; the third case throws "dashboard not built" rather
  than skipping. Baseline: 3 of 3 fail. After edits, before the build: 2 pass, 1 fails
  loudly. After the build: see the table.
- **Not fixed:** `docs/screenshots/ship-sdk/ship-sdk.png` is a tracked image rendered in
  Gellix; it needs a browser run to regenerate. Nobody has looked at the new system-font
  rendering.
- **Root-cause class:** assets delivered outside the code grant, wired in at the CSS and
  constant layer where a license scan of the tree never looks.
- **Invariant:** assert the built artifact, not the source grep alone.

## F3. Default config shipped a vendor credential; the platform makes no model call

- **Expected:** every model or vendor call routed to OpenVault `/v1`, no provider key field
  in default config.
- **Actual (measured by grep over apps and packages, tests excluded):** no model or LLM
  call exists in openship; the only vendor credential is `OBLIEN_CLIENT_ID` and
  `OBLIEN_CLIENT_SECRET` in `apps/api/.env.example`, read only when `CLOUD_MODE` is set
  (`packages/platform/src/engine/lib/oblien-client.ts`), which the self-hosted default
  never sets.
- **Fix:** the two lines replaced by a comment; nothing routes to `/v1` because there is
  nothing to route. Said so in `NETIE-ATTRIBUTION.md` rather than inventing a wiring.
- **Invariant:** say what is measured and what is assumed.

## F4. Renames that were safe, and the ones that were not

- Done: the dashboard brand constant (`i18n/locales/*/brand.json`, drives the HTML title
  and every `useBrandName()`), user-visible copy in nine locale trees and in hardcoded
  dashboard strings, CLI help, prompts and spinner text, compose header comments, the mail
  test mailbox display name, one host-channel impact line in packages/core.
- Left for stage 3 with the reason recorded in `NETIE-ATTRIBUTION.md`: container, image
  and compose project names (the CLI, the API and edge detection look them up by name),
  the `openship` binary and service identities (uninstall must find them), the self-app
  sentinel `appTemplateId === "openship"` (its slug is derived from the name), every
  identifier, env name, package name and URL, and strings naming services only upstream
  operates (Openship Cloud, the Openship GitHub App).
- Upstream tests re-pointed, none deleted or skipped: nine dashboard files hardcoding the
  brand word, `i18n-parity` baseline for `brand` 40 to 45 (the checker counts a
  one-string namespace per character), four `project-status` cases and one project-card
  case that asserted green without a claim.
- **Root-cause class:** a stage 1 prose rewrite leaves articles behind ("an Openship" to
  "an FreeBuild"); 11 of those were in the tree, fixed here, and the tool's `_prose`
  does not handle it. Not fixed in the tool: out of scope for this lane, listed.

## F5. Environment facts that shaped the run

- `bun install --frozen-lockfile` fails here: the proxy returns 403 on GitHub tarballs and
  `@electron/node-gyp` is pinned to one. `--filter '!@repo/desktop'` installs everything
  but the Electron app, which is not built or tested in this stage. Reported, not worked
  around further.
- The harness exports `BUN_OPTIONS=--smol` into every shell; it applied to both the before
  and the after runs equally. Vitest runs under node, so the effect is on `bun run`
  itself only.
- `cat /sys/fs/cgroup/memory.peak` reads 0 in this container, so peak build memory was
  not measured; the full `bun run build` (api tsup plus dashboard `next build --webpack`)
  completed without an OOM kill on 4 cores and 15 GB.
- One CLI test fails on the untouched baseline and identically after
  (`test/unit/compose-env-preserve.test.ts`, "warns about root ops when the dialed
  session's own sudo is refused": expected "no route to it", got ""). This sandbox runs
  as uid 0. Pre-existing, reproduced on both trees, not touched.

## Measured before and after

Same box, same commands, baseline in a worktree of the stage 1 tree, after in the edited
tree. BEFORE_AFTER_TABLE

## Patch replay

REPLAY_SECTION

## Not done / assumed

- Not run: `apps/api` `test:e2e` (needs a Docker daemon driving real containers),
  `apps/web` build, `apps/email`, `apps/desktop`, `packages/sdk` and `apps/edge` suites,
  `bun run lint` across the workspace beyond the three typechecks named above, Docker
  image builds. Assumed, not measured: Postgres accepts the claim inside the jsonb meta
  (it passes `sanitizeStorableStrings` like the rest of meta).
- Not measured: any live OpenVault. The gate POST was exercised against a mocked fetch
  only; `parent_run_id` and `child_id` have no source in the upstream yet, so with
  `NETIE_OPENVAULT_URL` set every claim is UNCLAIMED "leave-machine needs parent and
  child run ids" until a caller supplies them.
- Not done: `netieClaim` on the terminal SSE `complete` event (clients get it from the API
  on refresh); `live` and `netieClaim` in the `packages/contracts` TypeScript type (the
  schema does not reject extra fields, so the JSON passes); a re-claim or verify action
  from the unclaimed state; native-speaker review of the eight non-English "Deployed,
  unclaimed" labels and of the machine-swapped brand word in translated locale values.
- `scripts/test_sibling_patches.py` is red on base and on this branch: today 9 of 10 fail
  (was 8 of 10 on 2026-10-05; the siblings moved again), same class as F2 of
  `2026-10-05-ecosystem-lane.md`. `scripts/check_docs.py` runs every `scripts/test_*.py`,
  so it fails for that one reason only. Not touched, not skipped.
