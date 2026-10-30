# 2026-10-05 - freeide stage 2 (OpenVault gate on anomalyco/opencode)

Preflight: KB `D:\Netie-KB` absent in this cloud box. `docs/subagents_findings/INDEX.md`
read: one prior finding (ecosystem lane). PREFLIGHT: PARTIAL (F3 there warned that synthetic
fixtures miss what real trees show, which held again here). No subagents spawned; everything
below was run directly on the real upstream tree at the pinned commit.

Branch `claude/stage2-freeide`, base `claude/netie-ecosystem-rebrand-uq9q3z` (PR #43).
Deliverable: `ecosystem/overlays/freeide/0002-gate.patch`, catalog row `freeide` stage 1 -> 2.

## Measured (this container, Linux x64, bun 1.3.14, node 22.22.0, python 3.11)

| Step | Command (in the applied upstream tree) | Result |
|---|---|---|
| baseline typecheck | `bun run typecheck` in packages/opencode | green, 39 s |
| baseline suite | `bun test --timeout 30000` in packages/opencode | 3619 pass, 22 skip, 1 todo, 2 fail, 256 files, 18 min |
| gate test on baseline | `bun test test/netie/openvault-gate.test.ts` | 8 fail, 1 pass (the pass is the `enabled_providers: []` guard, expected on both) |
| gate test after | same | 9 pass |
| typecheck after | packages/opencode, packages/core, packages/tui | all green |
| binary build after | `bun run build --single --skip-install --skip-embed-web-ui` | `dist/freeide-linux-x64/bin/freeide --version` smoke test passed; `--help` says `freeide`; XDG config dir created as `freeide` |
| suite after | `bun test --timeout 30000` | 3627 pass, 22 skip, 1 todo, 3 fail, 257 files, 21 min |
| delta | after minus baseline | +9 tests (the gate file), +8 pass, +1 fail (`models` smoke, see below), 0 new skips |
| replay | `ecosystem.py clone` + `apply` into a fresh dir, `diff -r` against the working tree | identical; LICENSE sha256 unchanged |

Test changes carried in the patch, all because the fork renames things on purpose:
`test/cli/help/__snapshots__` regenerated with `--update-snapshots` (34 entries, names and
wordmark only), `test/cli/error.test.ts` expects the `freeide models` hint,
`test/cli/mcp-add.test.ts` reads `.config/freeide/`, `test/provider/provider.test.ts` expects
no Zen provider without a key, `test/preload.ts` starts the fake gate. During the first
after-change run `plugin.openai.ws-pool > prunes idle websocket connections` failed once and
passed 31 of 31 when the file ran alone; it is not in the diff and passed in the final run.

The third final failure, `opencode read-only commands (smoke) > models: exits 0 and lists the
test model`, also fails on an untouched baseline worktree run alone: this box's env keys make
`freeide models` print about 250 lines and the captured stdout stops short at a moving point,
so `test/test-model` (printed last) is missing. It passed once in the baseline full run, so it
is timing-bound, not caused by the patch. Not fixed: it is the harness and the box, not the
fork.

The 2 baseline failures are `tool.write > throws error when OS denies write access` and
`continues loading tui config when legacy source cannot be stripped`. Both chmod a file and
expect a write to fail; the suite runs as root here, so the write succeeds. Not touched.

## F1. "Open source default config" still had a vendor endpoint switched on

- **Expected:** after pointing the default provider at OpenVault `/v1`, no direct vendor
  endpoint is on without the user's own key.
- **Actual:** `Provider.list()` still returned `opencode` (Zen, `https://opencode.ai/zen/v1`)
  with 6 free models and `apiKey: "public"`. Upstream's custom loader keeps the free tier on
  with no key, no auth login and no config. Found only by listing providers on the real tree;
  nothing in the catalog JSON says so.
- **Repro:** on the stage 1 tree, `Provider.use.list()` in any `it.instance` test, print each
  provider's `source` and first model `api.url`.
- **Fix:** loader returns `autoload: false` without a key, auth or config; two upstream tests
  that asserted "no key gives 0 paid models" now assert "no key gives no Zen provider".
- **Root-cause class:** a default that is on by the vendor's choice, invisible in config.
- **Invariant:** assert the artifact the customer receives (the live provider list), not the
  config file.

## F2. The box's own environment switches vendors on

- **Expected:** a clean test box has only OpenVault active.
- **Actual:** this container exports `NVIDIA_API_KEY`, `GEMINI_API_KEY`, `GH_TOKEN` and
  `GITHUB_TOKEN`, so google, nvidia, github-models and github-copilot came on as source
  `env`. That is the user's own key path and stays legal in the fork, but a naive test
  ("every active provider is OpenVault") fails on such a box.
- **Fix in the test:** every non-OpenVault provider must have source `env`, `api` or
  `config`, never `custom` (keyless autoload).
- **Root-cause class:** environment leakage into a measurement.
- **Invariant:** separate verified fact (keys in env) from assumption (clean box).
- **Open:** DR-0002 rule 6 says subscription-login providers (Copilot, OAuth plugins) are
  off in any fork. Not done in this patch; listed in NETIE-ATTRIBUTION.md as stage 3.

## F3. `bun install` cannot resolve a GitHub tarball dependency through this egress

- **Expected:** `bun install --frozen-lockfile` works on the pinned tree.
- **Actual:** `ghostty-web` (packages/app) is pinned as `github:anomalyco/ghostty-web#<sha>`;
  bun fetches it from `api.github.com/.../tarball`, which this session's egress policy answers
  with 403. Plain `git fetch` of github.com works. `git+https://` specifiers are rewritten to
  the same tarball URL by bun.
- **Workaround (install only, not in the patch):** fetch the pinned commit with git into
  `/tmp/ghostty-web` (it ships `dist/`), set the dependency to `file:/tmp/ghostty-web`, run
  `bun install`, then `git checkout -- bun.lock packages/app/package.json`. The tree is clean
  afterwards; node_modules stays.
- **Root-cause class:** a dependency pinned to a host the environment cannot reach.
- **Invariant:** silent fallback is a lie, so the workaround is written down here, and the
  patch does not carry it.

## Assumed, not measured

- `openvault/auto` context 128k and output 32k are placeholders in the catalog row.
- OpenVault `POST /api/crew/gate` is not on OpenVault main (TAS-OPENVAULT section 8). The
  body shape follows `scripts/crew_ov_gate.py` (GateAsk fields, ids only). No live OpenVault
  was reached from here; the proof uses a fake that records the request.
- `bun.lock` and the workspace package name `opencode` are untouched on purpose: renaming the
  package would need a lockfile regeneration this box cannot do cleanly (F3).

## Not done

- Cortex tool_runner is not wired. Stage 3 (shippable) is not claimed.
- `scripts/test_sibling_patches.py` stays red on base (8 of 10); not touched.
