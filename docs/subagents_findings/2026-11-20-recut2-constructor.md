# 2026-11-20 - recut 2, constructor lane

Preflight: KB `D:\Netie-KB` absent in this cloud box. Read `CLAUDE.md`, the proposed DR
`docs/decisions/DR-PROPOSED-parked-patches-yield-to-sibling-tests.md` and
`2026-11-12-sibling-recut.md` (F3 was the hit: "constructor passes only because one patch flips
the sibling's script-order test"). PREFLIGHT: PARTIAL.

Shape: one session, no subagents. Pin `bfc7d3b7df8bc02c1729e48c7354032982f395ce` (branch
`landing-9-first-path`), not moved. The worktree was fast-forwarded to `claude/recut2` first
(the DR and the 2026-11-12 finding are not on `main`). The founder's constructor answer, "All
can ur compilers also can", is read as the DR reads it: either compiler is acceptable, ours
included. This cut prefers the repo's own `core/constructor.js`.

Outcome: re-cut. The 26-patch stack is now 3 patches. One behaviour could not be made the
default without editing a sibling-written test; it is written as a memo (D1), not decided.

## F1. A patch rewrote a test the constructor repo wrote

- **Expected:** no patch edits, reverses or deletes a test the sibling wrote (DR rule 1).
- **Actual:** `constructor-engine-order.patch` changed `tests/pages-honesty.test.js`: the test
  "index.html loads core then canvas then engine" became "core then engine then canvas", with
  `appAt < engineAt` flipped to `engineAt < appAt`. It moved `engine.js` before `app.js` because
  `app.js` called helpers (`listedOrEmpty`, `applyObjectType`) that only `engine.js` defined.
- **Repro:** apply the 26 old patches on the pin, `git diff --stat` shows
  `tests/pages-honesty.test.js | 6 +-` (measured on a clone).
- **Fix:** the helpers moved into `core/constructor.js`, which loads first. `app.js` reads them
  from `globalThis.NetieConstructorCore`. `index.html` is not touched; the page loads core,
  canvas, engine, which is the sibling's own order.
- **Root-cause class:** moved a script to satisfy a new dependency instead of moving the
  dependency to where the script order already allows it.
- **Invariant:** the gate now fails if any file the sibling wrote under `tests/` changes.

## F2. Two compilers

- **Expected:** one compiler (the DR's reading of the founder answer prefers `core/constructor.js`).
- **Actual:** the old stack put a strict `compileIR`, `topo`, `ghostWalk`, note and catalog
  checks in `engine.js` (1221 lines at the pin, 1703 patched) beside the sibling's
  `Core.compileIR` in `core/constructor.js`. `Core.compileIR` was no longer called by the page.
- **Repro:** old stack, `grep -c "function compileIR" engine.js core/constructor.js` gives 1 and 1.
- **Fix:** the strict checks are added to core behind `compileIR(state, { strict: true })`
  and `topo(state, { strict: true })`, plus `walkIR` and `cortexPayload`. `engine.js` has no
  compiler; it calls `Core.compileIR(canvasState(state), { strict: true })` and
  `Core.cortexPayload(canvasState(...))`. No strict check stays beside core: each fit in core.
  `engine.js` keeps only what is about the page (`canvasState` builds the canvas catalog,
  `compileIR` there adds the brain-panel digests, `bindWhenReady`).
- **Root-cause class:** a second implementation added next to the first because the first lived
  in a file that was awkward to change.
- **Invariant:** the gate asserts `WRITE_ACTIONS`, `NOTE_LEAK`, `compiledById`, `applyObjectType`,
  `cortexPayload` and `nodes: ir.nodes` are in `core/constructor.js` and none is in `engine.js`.

## F3. The stack was all-or-nothing

- **Expected:** a lane applies in layers a reader can stop at.
- **Actual:** 26 patches, each editing `engine.js`, in a fixed order; the README said "all 26 or
  nothing".
- **Fix:** 3 layers. Measured on clones at the pin: layer 1 alone (`constructor-core-strict-ir`)
  leaves the sibling's 118 unit tests, `check-laws.js` and the page unchanged. Layers 1+2 pass the
  same. Layer 2 without layer 1 applies but breaks the page (`pageerror: Core.walkIR is not a
  function`). Layer 3 needs both (it requires `engine.js`).
- **Root-cause class:** one defect per patch, with no layering between them.
- **Invariant:** `test_constructor_stack_order_core_first` pins the order.

## D1. Decision memo: strict compileIR as default, or as an option

Founder decision. Not settled here.

- **Behaviour A (the constructor repo's test):** `tests/constructor.test.js`, test "app IR is
  EMIT skin, ingest keeps the warehouse place" (starts at line 49), asserts `app.action_type === "emit"`
  from `Core.compileIR(state, { ghost: true })`. The repo's own `fdeSample()` sets
  `action_type: "emit"` on its app node.
- **Behaviour B (our spec):** `tests/compiler.test.cjs`, test "unlisted action_type on a non-tool
  node is dropped", compiles a lone `app` node with `action_type: "emit"` and asserts
  `action_type === null` and `requires_confirm === false`.
- **Evidence:** I made strict the default in a scratch clone and ran the sibling's 118 unit
  tests: 4 failed (this test, "trigger compiles as DOCUMENT_REF with webhook fields",
  "fdeSample encodes connector -> ontology ...", "compileIR stays cortex and can carry an RSF
  digest"). Passing `hop`, `skin`, `trigger_kind`, `source_kind`, `data_in`, `data_out`, `fde`
  and `rsf` through the strict IR fixed three. One failed, with `null !== 'emit'`. So one
  assertion is a true contradiction; the rest is additive work.
- **What this cut does:** strict is opt-in (`{ strict: true }`). Every Netie caller passes it:
  `engine.js`, `cortexPayload`, `walkIR`, the gate. Without it, `compileIR`, `topo` and
  `ghostWalk` are the pin's code. All 62 gate tests and all 118 sibling tests pass. Cost:
  anyone who calls `Core.compileIR(state)` bare still gets the lax compiler (invented `T0`,
  fake topo for a cycle, notes copied, unlisted values kept).
- **Options:**
  1. Keep it opt-in (this cut).
  2. Make strict the default and edit the one sibling assertion (or have the constructor repo
     decide `emit` is not an app action). Needs the pass-through fields for the other three
     tests, and strict then widens the Cortex POST with fields it does not list today (`skin`,
     `trigger_kind`, `source_kind`).
  3. Make strict the default and list `emit` as a non-write action allowed on `app` / `audit`
     nodes. The sibling keeps its assertion. Our test would need a different unlisted example
     (for instance `bash`); its intent (unlisted actions are dropped) holds. This edits our own
     spec, which the brief says not to weaken, so it is the founder's call.
- **Recommendation:** option 3. `emit` is the constructor repo's own marker for the EMIT node
  and carries no write, so keeping it loses nothing for Cortex; the behaviour that matters
  (a `bash` or `rm` action never reaches a node) stays tested. It ends the two-mode compiler
  without touching a sibling test.

## Gate assertions that moved or changed

In `test_constructor_compiler_tests_on_patched_head` (`scripts/test_sibling_patches.py`):

| Old assertion | Now |
|---|---|
| `WRITE_ACTIONS = [...]` in `engine.js` | same string in `core/constructor.js`; `engine.js` must not contain it |
| `NOTE_LEAK` in `engine.js` | in `core/constructor.js`; absent from `engine.js` |
| `function cortexPayload` in `engine.js` | in `core/constructor.js`; absent from `engine.js` |
| `nodes: ir.nodes` in `engine.js` | in `core/constructor.js` |
| `compiledById` in `engine.js` | in `core/constructor.js`; absent from `engine.js` |
| `function applyObjectType` in `engine.js` | in `core/constructor.js`; absent from `engine.js` |
| `function bindWhenReady` in `engine.js` | unchanged, still in `engine.js` |
| `app.js` lacks `Object.keys(OBJECTS[value].points)[0]`, has `applyObjectType(node, value, OBJECTS)` | unchanged |
| `engine.js` found, `app.js` after `engine.js` in `index.html` | `core/constructor.js` found, `app.js` after it, `engine.js` after `app.js` |

Added: the three patches apply in `CONSTRUCTOR_STACK` order; no file listed by `git ls-tree` under
`tests/` at the pin appears in `git diff --name-only`; `node --test tests/compiler.test.cjs` still
needs `pass 62`; the constructor repo's own `node --test tests/*.test.js tests/unit/*.test.js`
must report `fail 0`; `engine.js` must contain `Core.compileIR(canvasState(state), { strict: true })`
and `Core.cortexPayload(canvasState`.

In `tests/compiler.test.cjs` (our spec, new file at the pin): the 62 tests and every assertion
are unchanged. Only how they load changed: the header now takes `Core` from
`../core/constructor.js` and wraps `compileIR`, `topo` and `ghostWalk` as
`Core.compileIR(s, { strict: true })`, `Core.topo(s, { strict: true })` and `Core.walkIR`;
`bindWhenReady` still comes from `../engine.js`. One test changed its assertion because the
page order is a stated direction of this cut: "index.html loads engine.js before app.js" became
"index.html loads core, then app.js, then engine.js (the repo's own order)". Its old form is
the behaviour F1 retires; the new form asserts the intent that replaces it.

## Edits outside `docs/patches/constructor-*.patch`

- `scripts/apply_product_patches.py`: `CONSTRUCTOR_26` (26 names) became `CONSTRUCTOR_STACK`
  (3 names); docstring "26-stack" became "3-patch stack"; the `constructor` stack uses the new tuple.
- `scripts/test_apply_product_patches.py`: import renamed; `len(...) == 26` became `== 3`; new
  `test_constructor_stack_order_core_first` (exact order; the retired patch file is gone).
- `scripts/test_sibling_patches.py`: constructor lines of the module docstring and the one
  constructor test method, as in the table above; the import now also takes `CONSTRUCTOR_STACK`.
  Nothing else in the file. No existing assertion on another lane changed.
- `docs/patches/README.md`: the "## Constructor" section, and "(do not mix with the 26)" in the
  intro became "(do not mix with the 3)".
- Retired with `git rm` (25 files): `constructor-empty-graph`, `-ir-refuse`, `-ir-ids`,
  `-ghost-refuse`, `-ir-emit`, `-tool-action`, `-inspect-action`, `-inspect-object`,
  `-inspect-tier`, `-chat-object`, `-topo-leftover`, `-ir-entry`, `-ir-output`, `-ir-object`,
  `-ir-bind`, `-ir-action-allow`, `-ir-intake`, `-ir-hitl`, `-ir-connected`, `-ir-note`,
  `-ir-cortex-post`, `-object-pick`, `-engine-order`, `-ir-post`, `-ir-kahn-nodes` (all
  `constructor-*.patch`). `constructor-compiler-tests.patch` was rewritten in place.
  The two `4896ddd` extras are untouched.
- Stale text elsewhere, not edited (out of scope): `TAS/ESTATE-GAP.md` line 115,
  `TAS/TAS-CONSTRUCTOR.md` line 34, `Software Blueprint/Cortex/PRD-001-...md` row F14 and
  `docs/ACCESS.md` line 54 still name the retired patches.

## Measured

Fresh clones, pin `bfc7d3b7df8bc02c1729e48c7354032982f395ce`. "base" is the pin, "pat" is the pin
plus the 3 patches. Node 22.23.5.

| Check | base | pat |
|---|---|---|
| `node --test tests/compiler.test.cjs` | no such file | 62 pass, 0 fail |
| `node --test tests/*.test.js tests/unit/*.test.js` | 118 pass, 0 fail | 118 pass, 0 fail |
| `node scripts/check-laws.js` | exit 0, all laws pass | exit 0, all laws pass |
| Playwright `tests/e2e` (7 spec files) | 52 passed | 52 passed |

- Unit test names (spec reporter, durations stripped): identical lists, base vs pat. E2E test
  names: identical lists. `check-laws.js`: the only text difference is a count, "no ov_ key
  strings in 83 source files" vs "84" (the new test file).
- E2E command: `node /opt/node22/lib/node_modules/playwright/cli.js test --trace off --reporter=list`
  from the clone root. `@playwright/test` resolved through a scratch shim to the preinstalled
  Playwright 1.63.0 runner and Chromium 1243; `@axe-core/playwright@4.10.2` came from npm
  (`--ignore-scripts`). The repo pins `@playwright/test` 1.56.1; that version was not run.
- `git diff --name-only HEAD` on pat (plus untracked): `.github/workflows/test.yml`, `app.js`,
  `core/constructor.js`, `engine.js`, `tests/compiler.test.cjs` (new). `git diff --stat`:
  4 files changed, 467 insertions, 55 deletions, plus the new test file. The 20 files
  `git ls-tree -r HEAD tests/` lists at the pin: 0 of them changed.
- Gate: `python3 -m unittest scripts.test_sibling_patches.SiblingPatchTests.test_constructor_compiler_tests_on_patched_head -v`
  from the worktree root: ok (2.2 s). `make ci`: "ok 30 files, laptop-ASCII clean, 46 script
  tests passed" (before this finding was added; re-run after, see the commit).
- The gate can fail (run against the patched worktree, test module patched in memory):
  adding the retired `constructor-engine-order.patch` pages-honesty hunk to the stack makes the
  "no sibling test touched" assertion fail; dropping `constructor-core-strict-ir.patch` fails
  on the compiler tests (exit 1); dropping `constructor-engine-core.patch` fails with
  `ReferenceError: window is not defined`. The moved-string assertions are meaningful because the
  old stack's `engine.js` has `WRITE_ACTIONS` 2x, `NOTE_LEAK` 3x, `compiledById` 3x,
  `function applyObjectType` 1x, `function cortexPayload` 1x (grep counts) and the patched one 0x,
  so `assertNotIn(..., engine)` fails on the old tree.
- Browser smoke (scratch script, Chromium): base, old stack and pat all load without page
  errors; chat `ghost` answers "Ghost run (no writes). 8 steps." and `set point sku` answers
  "Data point sku." on all three. Serving the page under `/cortex/` with POSTs stubbed: on base
  the `ghost` and `run all` POST bodies are the raw canvas (keys `edges, nodes`; nodes carry
  `note`, `x`, `y`, `persona`); on pat they are the compiled IR (keys `edges, engine,
  entry_node_id, ghost, nodes, output_node_id, version`; no `note`), 8 nodes. That change is
  the intent of the lane.

## Not run

- The compiled-IR POST against a real Cortex `constructor-mount`. Whether Cortex's
  `/cortex/constructor/*` handlers accept IR-shaped nodes instead of canvas nodes is assumed,
  not measured. The stub only proves what the page sends.
- Playwright 1.56.1 (the repo's pin) and the repo's `npm test` wrapper (`npm run test:laws`,
  `test:unit`, `test:e2e` were run as their underlying commands).
- The sibling's GitHub Actions (`test.yml`, `ci.yml`, `pages.yml`).
- `constructor-ir-4896ddd.patch` and `constructor-inspect-4896ddd.patch`: not touched, not run.
- `scripts/constructor_ir.py` and `netie.route.compile_ir`: not touched, not compared with the
  new JS strict mode.

## Assumed

- The founder's answer "All can ur compilers also can" means either compiler is acceptable
  (the DR's reading, open to correction).
- A `strict` option on the sibling's compiler counts as "added to" it. If the founder wants the
  sibling's bare call to be strict, that is D1 option 2 or 3.

## Verified by T1 (independent agent, not the builder)

Replayed by a separate verifier agent on its own fresh clones at pin `bfc7d3b`, at Netie
commit `95ac504`. It edited nothing in this repo.

- Stack applies in order: confirmed. Changed files: `.github/workflows/test.yml`, `app.js`,
  `core/constructor.js`, `engine.js`, new `tests/compiler.test.cjs` (+467/-55). None of the
  pin's 20 files under `tests/` changed. `git diff -- index.html` is empty.
- `node --test tests/compiler.test.cjs`: 62 pass, 0 fail. The 62 test names equal the old
  26-patch stack's (rebuilt from `06f4599`). Only change besides the header wiring: the
  script-order test, now core < app.js < engine.js. No other assertion removed or weakened.
- Unit `node --test tests/*.test.js tests/unit/*.test.js`: base 118/0, patched 118/0.
  `node scripts/check-laws.js`: exit 0 both. Playwright e2e (1.63 via shim, `--trace off`):
  base 52 passed, patched 52 passed, identical name lists.
- Gate: `test_constructor_compiler_tests_on_patched_head` OK; `test_apply_product_patches.py`
  13 OK. Proved red in a mirror copy: dropping `constructor-core-strict-ir.patch` from the
  stack, and turning the disconnected-graph refusal into a pass, each fail the gate. Not seen
  red: the "no sibling test touched" assertion (no mutation tried).
- Gate assertions: the six moved strings are asserted in `core/constructor.js` and, for the
  key names, absent from `engine.js`. Nothing that still applies was dropped.
- D1: strict-by-default in core gave 114 pass, 4 fail on the sibling's 118 (the four tests
  named in D1). The claim that pass-through fields leave exactly the one `emit` failure was
  not run by the verifier (assumed from the builder).
- Gap checked by T1: `engine.js` keeps `function topo(state) { return Core.topo(state); }`
  without `strict`. That wrapper is the pin's own code (`engine.js:290` at `bfc7d3b`), the
  stack does not change it, and nothing in the page calls it (grep of all `.js` and `.html`
  outside `tests/` and core). So the old "leftover cyclic nodes" behaviour does not reach any
  caller through it. Not changed.
