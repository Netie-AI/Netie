# 2026-10-22 - freeide-ext stage 2 (OpenVault gate on Kilo-Org/kilocode VS Code extension)

Filed 2026-10-29 by the wave 2 session that took over the lane (file name kept from the
hand-off). Preflight: KB `D:\Netie-KB` absent in this cloud box. `docs/subagents_findings/
INDEX.md` and its findings read. PREFLIGHT: PARTIAL (the freeide worked example and its F1
vendor-default class applied directly). No subagents spawned.

Branch `claude/stage2-freeide-ext`, base `claude/netie-ecosystem-rebrand-uq9q3z`.
Deliverable: `ecosystem/overlays/freeide-ext/PLAN.md`. Catalog row stays at stage 1.

## Measured before and after

| Step | Before (2026-10-22 session) | This session (2026-10-29) |
|---|---|---|
| clone + apply | 6 s | 7 s |
| bun | 1.4.2 | box has 1.4.4; 1.4.2 fetched with `npm pack` |
| `bun install --frozen-lockfile` | exit 0, 10 s | 1.4.4: exit 1 (fff-bun patch); 1.4.2 with `--ignore-scripts`: exit 0, 9 s |
| `bun run test:unit` | 6682 tests, 6657 pass, 24 skip, 1 fail | refused by auto mode, not run |
| typecheck, lint, bundle | green | not run |
| `prepare:cli-binary` | fail (no zig, bwrap 403) | not run |
| 0002 patch cut and replay | not done | not done (no shell) |

## F1. The extension's backend loads a gate plugin that can vanish silently

- **Expected:** if the OpenVault gate plugin cannot load, tools do not run.
- **Actual (read from code, not run):** `packages/opencode/src/plugin/index.ts` reports a
  plugin load failure with `publishPluginError` and keeps serving with the hooks it has. A
  missing `dist/netie-openvault-gate.js` would mean every tool runs ungated.
- **Repro:** start the backend with `KILO_CONFIG_CONTENT` naming a `file://` plugin that does
  not exist; a `bash` tool call still runs. (Not run here.)
- **Fix in the plan:** the extension checks the bundle exists before it builds the env and
  refuses to start the backend otherwise; test case 5 in PLAN.md.
- **Root-cause class:** a control whose absence degrades to allow.
- **Invariant:** silent fallback is a lie; prove a gate can fail before trusting it green.

## F2. A gate keyed on a list of risky tool names fails open on the next tool

- **Expected:** every leave-machine tool asks OpenVault.
- **Actual:** `tool.execute.before` fires for native, MCP, plugin and code-mode tools
  (`session/tools.ts` five sites, `prompt.ts`, `code-mode.ts`), whose ids are not known in
  advance (`repo_clone`, `generate_image`, `kilo_memory_*`, `<server>_<tool>`). A list of
  bash, edit, write, webfetch misses them.
- **Fix in the plan:** deny by default; only a short local read-only allowlist skips the gate.
- **Root-cause class:** allowlisting the dangerous instead of the safe.
- **Invariant:** fix the root-cause class, not the symptom in front of you.

## F3. The toolchain the lane was measured with drifted under it

- **Expected:** the 2026-10-22 install command still works.
- **Actual:** the box's bun moved 1.4.2 to 1.4.4; `--frozen-lockfile` then fails on a
  `patchedDependencies` hunk. Upstream pins `packageManager: bun@1.4.2`.
- **Repro:** `bun --version` (1.4.4), `bun install --frozen-lockfile` at the upstream root.
- **Fix:** run the pinned bun (`npm pack @oven/bun-linux-x64@1.4.2`).
- **Root-cause class:** an unpinned tool in the measuring box.
- **Invariant:** separate verified fact from assumption: a measurement names its toolchain.

## F4. Auto mode refuses upstream code execution, then the whole shell

- **Expected:** a lane that builds and tests an upstream tree can run its tests.
- **Actual:** `bun install` with lifecycle scripts and `bun run test:unit` were refused as
  code from external, then every shell command was refused for the rest of the session. The
  same block stopped the original freeide-ext session.
- **Root-cause class:** a control that blocks legitimate work.
- **Invariant:** a control that blocks legitimate work is itself a failure. This lane needs
  a session outside auto mode, or a permission rule for `bun` in the upstream clone.

## Also found

- `NETIE-ATTRIBUTION.md` from `0001-rebrand.patch` names `831805118a`, not the pin
  `a93088bfe2`. Not fixed: it belongs inside `0002-gate.patch`, which was not cut.
- `scripts/test_sibling_patches.py` is red on base, 9 of 10 per the coordinator. Not run or
  touched here.
- Repo gate (`ecosystem.py validate`, `render --check`, `check_docs.py`, `test_ecosystem.py`,
  `secrets_scan.py`) not run in this session: no shell. Both files pushed are ASCII by
  construction; that is assumed until a session runs `check_docs.py`.

## Not done, assumed

See PLAN.md sections 4 and 5. Nothing is built, tested, cut or replayed.

## Launch readiness

Not launchable. Stage 1 docs only. Stage 2 needs one session with a shell that may run bun
in the upstream clone; the design and test spec are in PLAN.md, about 2 to 3 hours of work
plus a 200 s suite run per pass.
