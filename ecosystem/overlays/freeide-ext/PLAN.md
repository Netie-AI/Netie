# freeide-ext stage 2 plan: designed from code, not built or run here

Upstream `Kilo-Org/kilocode` at `a93088bfe2` (MIT, two copyright lines: Kilo Code and
opencode), mode fork-rebrand, product FreeIDE, Netie name "FreeIDE for VS Code". Scope is
`packages/kilo-vscode` only; the core stays on the `freeide` row. Series today:
`0001-rebrand.patch`. Planned: `0002-gate.patch`. Catalog stage stays 1.

## 0. Why this is a plan and not a patch

Session of 2026-10-29 (wave 2). Measured in this container: clone plus apply 7 s; local
baseline commit `c04d14f` on top of stage 1; `bun install --frozen-lockfile --ignore-scripts`
with bun 1.4.2 exit 0, 1873 packages, 9 s. Then auto mode refused, in order: `bun install`
with lifecycle scripts, `bun run test:unit`, and after that every shell command for the rest
of the session ("could not evaluate", not a judgment on the action). So nothing below was
compiled, tested, cut or replayed in this session. No `0002-gate.patch` is shipped: a patch
written by hand without `git diff` and a replay proof would break CLAUDE.md rule 3 and the
replay contract. A session with a shell picks this up at section 4.

Environment drift worth knowing: the box's bun is 1.4.4. With 1.4.4,
`bun install --frozen-lockfile` fails (`@ff-labs/fff-bun@0.9.4` patch hunk does not apply
to `src/ffi.ts`). Upstream pins `packageManager: bun@1.4.2`; `npm pack
@oven/bun-linux-x64@1.4.2` gives that binary and install is then green.

## 1. Read from code at the pin (file:line, not run)

Default route:

- `packages/kilo-vscode/package.json`: `kilo-code.new.model.providerID` default `kilo`,
  `kilo-code.new.model.modelID` default `kilo-auto/free` (about line 1001).
- `src/shared/provider-model.ts`: `KILO_AUTO = { providerID: "kilo", modelID:
  "kilo-auto/free" }`. Used by `src/provider-actions.ts` line 215 (`computeDefaultSelection`
  last fallback), `webview-ui/src/context/provider.tsx` line 43 (initial signal) and
  `webview-ui/src/context/session.tsx` line 470 (`fallback`). The webview bundles this file
  for the browser, so it must stay free of node imports.
- `computeDefaultSelection` order: backend `config.model`, then the two VS Code settings,
  then `KILO_AUTO`. So the plan does NOT put `model` in `KILO_CONFIG_CONTENT` (that would
  override a user's own `kilo.json` model); it changes the package.json defaults and the
  fallback constant instead.
- `src/provider-actions.ts` lines 91 to 107 drop the `kilo` provider and its default only
  when the Kilo auth-status request itself fails, not when the user is logged out.

Backend env and config:

- `src/services/cli-backend/server-manager.ts` spawn (about line 131) builds the env from
  `process.env` plus fixed vars plus `extraEnv` (only browser broker vars today, from
  `connection-service.ts` line 163). Nothing Netie-specific.
- `packages/opencode/src/config/config.ts` line 900: `KILO_CONFIG_CONTENT` is loaded after
  every project dir, as source `KILO_CONFIG_CONTENT`, scope `local`, trusted (so `{env:}` and
  `{file:}` tokens expand). Managed and account config still merge after it. Arrays such as
  `plugin` concatenate (`mergeConfigConcatArrays`). Virtual sources skip
  `resolveLoadedPlugins`, so a plugin spec there must be an absolute `file://` URL.
- `packages/opencode/src/kilocode/process/env.ts` line 12 deletes `KILO_CONFIG_CONTENT` from
  child-process env, so tools do not inherit it.
- `packages/opencode/src/kilocode/config/plugin-deps.ts`: the `@kilocode/plugin` npm install
  fires only for `file://` plugins found in config directories (the dir loop before line
  900), not for `KILO_CONFIG_CONTENT`. A self-contained bundle needs no install.
- Schema to assert against: `@opencode-ai/core/v1/config/config` `ConfigV1.Info` (workspace
  dependency of kilo-vscode, exports `./*`), `plugin` is `ConfigPluginV1.Spec[]` (string or
  `[string, options]`), `provider` is a record of `ConfigProviderV1.Info` (`npm`, `name`,
  `options` with `baseURL`, `models` with `limit.context` and `limit.output` required
  together, `tool_call`).

Hooks and plugin loading:

- `packages/plugin/src/index.ts` line 268: `tool.execute.before(input: { tool, sessionID,
  callID }, output: { args })`.
- It fires in `packages/opencode/src/session/tools.ts` lines 198, 268, 348, 425, 493 (native,
  MCP resource and MCP tools), `session/prompt.ts` line 433 and `tool/code-mode.ts` line 145,
  each before execute.
- `packages/opencode/src/plugin/index.ts` line 304: `trigger` runs each hook through
  `Effect.promise`, so a rejected hook is a defect that aborts the tool before execute.
  Assumed, not proven: the defect reaches the model and the UI as a tool error with the
  message intact. The end-to-end case in section 3 is what proves it.
- `plugin/shared.ts` `readV1Plugin` with `mode: "detect"`: a default export object with
  `id` and `server()` is the V1 shape; otherwise named function exports are used.
- Fail-open risk found by reading: a plugin that fails to load is reported via
  `publishPluginError` and the server keeps going without it. So the extension must refuse
  to start the backend if the bundled gate file is missing, or tools run ungated.

Autocomplete:

- `packages/kilo-gateway/src/autocomplete.ts` line 110 defaults to provider `kilo`;
  `kilo-code.new.autocomplete.enableAutoTrigger` default `true` (package.json about line
  1045, read in `src/services/autocomplete/settings.ts` line 27 with fallback `true`). The FIM
  handler (`packages/opencode/src/kilocode/server/httpapi/handlers/kilo-gateway.ts` line 124)
  answers 401 without a Kilo login.

## 2. Design for `0002-gate.patch` (all in `packages/kilo-vscode`)

1. Default selection `openvault/auto`. package.json defaults become `openvault` and `auto`.
   `provider-model.ts` gains `OPENVAULT_PROVIDER_ID = "openvault"` and `NETIE_DEFAULT =
   { providerID: "openvault", modelID: "auto" }`; the three `KILO_AUTO` call sites use it.
   `KILO_AUTO` is then unused, so it is deleted (knip fails on unused exports); the two
   upstream tests that define their own local `KILO_AUTO` constant are untouched.
2. `src/netie/openvault.ts` (node side only):
   - `url()` from `NETIE_OPENVAULT_URL`, default `http://127.0.0.1:5000` (TAS-OPENVAULT),
     trailing slashes trimmed; `modelsURL()` is `${url}/v1`; `gateURL()` is
     `${url}/api/crew/gate`.
   - `providerBlock()`: `{ name: "OpenVault FreeRoute", npm: "@ai-sdk/openai-compatible",
     options: { baseURL: modelsURL() }, models: { auto: { name: "OpenVault auto", tool_call:
     true, limit: { context: 128000, output: 32000 } } } }`. Limits are assumed.
   - `gatePluginPath(extensionPath)` is `dist/netie-openvault-gate.js`; throws a visible
     error if the file is missing (closes the fail-open risk in section 1).
   - `buildConfigContent(userValue, pluginPath)`: base `{ provider: { openvault }, plugin:
     [pathToFileURL(pluginPath).href] }`, deep-merged with a user-set `KILO_CONFIG_CONTENT`
     (user keys win, except `plugin` which is concatenated so the gate stays). Bad user JSON
     is not dropped silently: the user value is ignored, `vscode.window.showWarningMessage`
     names it, and the log says so.
   - `openVaultEnv(env, extensionPath)` returns `{ NETIE_OPENVAULT_URL, KILO_CONFIG_CONTENT }`.
     ServerManager spreads it after `extraEnv`, built from `{ ...process.env, ...extraEnv }`,
     so both the extension and the backend plugin see one URL.
3. `src/netie/openvault-gate-plugin.ts`, bundled by a new esbuild entry (ESM, platform node,
   no externals) to `dist/netie-openvault-gate.js`. `.vscodeignore` already ships
   `!dist/**`. Default export `{ id: "netie-openvault-gate", server }`; `server` returns
   `{ "tool.execute.before": ask }`. `ask` posts `{ kind: "service", id: input.tool, intent:
   "leave", parent_run_id: input.sessionID, child_id: input.callID, deficit: "" }` (GateAsk in
   `scripts/crew_ov_gate.py`), ids only, never `output.args`. 5 s timeout. Unreachable,
   non-JSON, or `allowed !== true` throws `OpenVault refused <tool>: <reason>` or
   `OpenVault gate unreachable at <url> ... <tool> was not run`.
   Which tools: deny by default. Ungated is a short local allowlist: `read`, `glob`, `grep`,
   `list`, `lsp`, `todowrite`, `todoread`, `question`, `skill`, `task`, `plan_exit`,
   `open_plan`, `invalid`, `get_context_info`, `kilo_local_recall`. Everything else is gated,
   which covers the named ones (`bash`, `edit`, `write`, `apply_patch`, `webfetch`,
   `websearch`, `codesearch`) plus `repo_clone`, `generate_image`, `semantic_search`,
   `kilo_memory_*`, code-mode `execute`, every MCP tool and every plugin tool. Recorded
   decisions: `task` is not gated because each tool its subagent calls passes the same hook;
   `edit` and `write` are local but gated as asked (they change the user's tree). Why deny by
   default: MCP and plugin tool ids are not known in advance, so an allowlist of risky ids
   fails open on the next new tool. That is the root-cause class, not the five names.
4. Autocomplete: `enableAutoTrigger` default `false` in package.json and in the
   `settings.ts` fallback. Reason: its only default route is the Kilo account, which is a
   vendor route outside OpenVault and 401s for a logged-out user anyway. Repointing FIM at
   OpenVault needs a FIM endpoint OpenVault does not document; stage 3.
5. Rename user-visible strings to "FreeIDE for VS Code": `EXTENSION_DISPLAY_NAME` in
   `src/constants.ts`, package.json `displayName`, activity bar container title, view name,
   command `category`. Point `tests/unit/native-tab-title.test.ts` and
   `tests/unit/extension-arch.test.ts` (lines 206 to 210) at the constant. Not renamed
   (stage 3): package `name` `kilo-code`, `publisher` `kilocode`, `kilo-code.new.*` command
   ids and setting keys (renaming breaks every user's settings), the logo, and the anonymous
   `kilo` autoload in core (`packages/opencode/src/kilocode/provider/provider.ts` lines 203
   to 235).
6. `NETIE-ATTRIBUTION.md` inside the patch: fix the base commit it names (`831805118a`, a
   probe-time commit) to the catalog pin `a93088bfe2`; add a stage 2 section and "Not done yet
   (stage 3)". `overlay.json`: `series` gains `0002-gate.patch`, plus `files_changed_stage2`
   as on the `freeide` row.

## 3. Gate test spec

`packages/kilo-vscode/tests/unit/netie-openvault-gate.test.ts`, `bun test` (bunfig preloads
the vscode mock). Every new module is imported inside the test body, so on the baseline tree
every case fails instead of the file failing to load; record that count.

1. Parsed package.json: model defaults `openvault` and `auto`; `enableAutoTrigger` false;
   `displayName` is "FreeIDE for VS Code".
2. `computeDefaultSelection(null, "", "")` is `openvault/auto`; a user `config.model` still wins.
3. Env the real `ServerManager` passes to a fake CLI (a script that writes its env as JSON
   and prints the port line): `NETIE_OPENVAULT_URL` present; `KILO_CONFIG_CONTENT` decodes
   with `ConfigV1.Info` from `@opencode-ai/core/v1/config/config`, has `provider.openvault`
   with `baseURL` `${url}/v1`, and a `file://` plugin that exists on disk.
4. Merge: a user `KILO_CONFIG_CONTENT` keeps its keys and its plugins; bad JSON gives a
   visible warning and the gate still loads.
5. Missing gate bundle: the backend does not start and the error names the file.
6. Plugin, against a fake OpenVault on `127.0.0.1:0`: refused throws and the tool body did
   not run; unreachable throws (fail closed); allowed returns; the recorded body has exactly
   the six GateAsk keys and no argument value; an allowlisted tool sends no request.
7. End to end, if it runs here: real backend from source with the env from case 3, fake
   OpenVault serving `/v1/chat/completions` (one streamed `bash` tool call) and
   `/api/crew/gate`. Refused: the command's marker file is absent and the tool error carries
   the reason. Allowed: the marker file exists.

## 4. Commands for the session that builds it

In a box where these may run (bun 1.4.2, see section 0):

```
python3 scripts/ecosystem.py clone freeide-ext W && python3 scripts/ecosystem.py apply freeide-ext W
cd W && git add -A && git commit -m baseline && bun install --frozen-lockfile
cd packages/kilo-vscode && bun run test:unit   # baseline, expect 1 fail (orphan-size, root)
# implement section 2 and 3, then:
bun test tests/unit/netie-openvault-gate.test.ts
bun run test:unit && bun run typecheck && bun run lint && bun run format:check
bun run knip && bun run check-kilocode-change && bun run bundle
KILO_SKIP_BUNDLED_BWRAP=1 bun run prepare:cli-binary   # needs zig 0.14.0; binary then needs system bwrap
cd ../.. && git add -A && git diff --binary --cached baseline > 0002-gate.patch
```

Then replay in a fresh dir (`clone`, `apply` with both patches) and compare `git write-tree`;
check LICENSE sha256 stays `8a088af74e19c37e62906321b1072f593113058ed9eae507d899d41e6e5e5bb4`.
`local-bin.ts` writes a source wrapper at `bin/kilo` when the compiled build fails; that is
not a compiled binary. If URLs in docs changed, run `bun run script/extract-source-links.ts`
at the upstream root (generated file). Set catalog stage 2 and render only when test, build
and replay all held.

## 5. Assumed, not measured

- OpenVault serving `/v1/models` and `/v1/chat/completions` for `auto`, and whether it needs a
  seat token (no `apiKey` is sent in this design).
- `POST /api/crew/gate` is not on OpenVault main (TAS-OPENVAULT section 8); body shape from
  `scripts/crew_ov_gate.py`.
- Limits 128k context and 32k output for `openvault/auto`.
- The webview lists a config-sourced provider as connected without a key.
- A hook rejection shows to the user as a tool error (section 3 case 7 proves or refutes it).
- `NETIE_OPENVAULT_URL` reaches the extension host only when VS Code is started from a shell
  that has it; a setting for it is stage 3.

## 6. What would make this stage 3

Package name, publisher, command ids and setting keys renamed with a settings migration;
logo; the anonymous `kilo` autoload in core off; autocomplete routed through OpenVault;
subscription-login providers off (DR-0002 rule 6); a vsix built and installed in VS Code
with the gate refusing a real `bash` call against a real OpenVault.
