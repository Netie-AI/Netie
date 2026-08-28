# TAS-CONSTRUCTOR - Constructor technical architecture

**Plane:** 4 (consumer canvas) · **Repo:** `Netie-AI/constructor` (public)
**Measured:** 2026-08-28 against clone default `landing-9-first-path` HEAD `4896ddd`. This token cannot push (403). GitHub HEAD has no `tests/compiler.test.cjs`. Netie 12 patches that fit that HEAD: **29 passed**. The 26-patch / 62-pass stack was refreshed for unpushed `eebff20` and does not apply (`constructor-inspect-object.patch` fails on `app.js`). Portable `constructor_ir.py` is the Python import for Crew/Cortex.

---

## 1. What it is

A ChatGPT-style box that compiles a canvas graph into Cortex IR: connector -> ontology -> insight -> foundry -> app. Ghost mode dry-runs. Ranks three Cortex coordination patterns and applies the winner.

**Is not:** n8n, Activepieces, React Flow, or a second `dag_runner`. README forbids cloning n8n/Activepieces. Engine stays Cortex. `E:\\Cortex\\myactiveflow` / `myactivepieces` are study notes for piece catalogs, not trees to copy.

Portable import for Crew/Cortex agents (this repo):

```
python3 scripts/test_constructor_ir.py
```

`scripts/constructor_ir.py` fail-closes empty/unknown/cycle/dangling/missing ids, Kahn entry/sink, unlabeled object/action, assumed chat `inventory` / `export_pptx` / `T0`. `scripts/constructor_action_bind.py` binds a label to Cortex `WRITE_ACTIONS`. Unknown piece refuses. Do not rebuild the 26 JS patches here.

---

## 2. vs `@xyflow/react` (MIT)

xyflow is a node editor. Constructor is 11 files (custom canvas in `app.js` / `engine.js` / `index.html`). Score: **2 / 10** as an editor, **4 / 10** as a Cortex IR compiler.

`npm i @xyflow/react` only if the canvas must *feel* like React Flow. Do not replace `compileIR`. Portable `scripts/constructor_honesty.py` refuses `@xyflow/react` as the compiler.

---

## 3. Compiler (this VM)

HEAD `engine.js` compiled IR for Cortex kinds. Ranking mixed foundry-boost into `rankApproaches` (DOM-only). This VM extracted `rankForKinds` + `compileIR` export and added `tests/compiler.test.cjs`.

```
node --test tests/compiler.test.cjs
```

**62 passed** was measured on unpushed `eebff20`. Public `4896ddd` after the 12 fitting patches: **29 passed** (`constructor-ir-4896ddd.patch` adds listed-object drop, no invented `T0`, Kahn emit, unknown action, `NOTE_LEAK`, `cortexPayload`, engine-before-app). `inspect-object` and later patches stay for a write token.

Patches: `docs/patches/constructor-compiler-tests.patch` then `docs/patches/constructor-empty-graph.patch` then `docs/patches/constructor-ir-refuse.patch` then `docs/patches/constructor-ir-ids.patch` then `docs/patches/constructor-ghost-refuse.patch` then `docs/patches/constructor-ir-emit.patch` then `docs/patches/constructor-tool-action.patch` then `docs/patches/constructor-inspect-action.patch` then `docs/patches/constructor-inspect-object.patch` then `docs/patches/constructor-inspect-tier.patch` then `docs/patches/constructor-chat-object.patch` then `docs/patches/constructor-topo-leftover.patch` then `docs/patches/constructor-ir-entry.patch` then `docs/patches/constructor-ir-output.patch` then `docs/patches/constructor-ir-object.patch` then `docs/patches/constructor-ir-bind.patch` then `docs/patches/constructor-ir-action-allow.patch` then `docs/patches/constructor-ir-intake.patch` then `docs/patches/constructor-ir-hitl.patch` then `docs/patches/constructor-ir-connected.patch` then `docs/patches/constructor-ir-note.patch` then `docs/patches/constructor-ir-cortex-post.patch` then `docs/patches/constructor-object-pick.patch` then `docs/patches/constructor-engine-order.patch` then `docs/patches/constructor-ir-post.patch` then `docs/patches/constructor-ir-kahn-nodes.patch` (also a `test.yml` workflow). Push 403.

GitHub on default `landing-9-first-path`: **pages.yml** is green. There is **no unit-test workflow** on HEAD until that patch lands.

---

## 4. Trust boundaries

| Boundary | Today |
|---|---|
| Ghost dry-run | `ghostWalk` uses `compileIR`; refuse means empty log, no leftover cycle walk. `topo()` returns only the Kahn prefix; leftover cyclic nodes are omitted. `compileIR` entry is Kahn source; output is Kahn sink app (or unique Kahn sink when no app/audit). Disconnected graphs and forks with no app refuse. Canvas notes stay off compiled IR. Cortex ghost/run/fetch/recommend POST compiled IR in Kahn order (not canvas array order; compileIR refuse means no post). Unlisted `object_type` / `data_point` / mismatched `fetch_from` are dropped (POST body matches IR). Unknown `tool_call` action refuses. `export_pptx` and `item.intake` set `requires_confirm` even on foundry; `agent.checked` does not |
| Writes | Cortex, not Constructor |
| Keys | none in this tree; engine URL is Cortex |

---

## 5. Verify

```
NEEDS-YOU TAS-CONSTRUCTOR  grant write on Netie-AI/constructor and land the compiler-test patch
```

Then: GitHub `test` workflow green on `node --test tests/compiler.test.cjs`. Do not add xyflow until a buyer needs the editor feel.
