# TAS-CONSTRUCTOR - Constructor technical architecture

**Plane:** 4 (consumer canvas) · **Repo:** `Netie-AI/constructor` (public)
**Measured:** 2026-08-27 against clone default `landing-9-first-path`. This token cannot push (403).

---

## 1. What it is

A ChatGPT-style box that compiles a canvas graph into Cortex IR: connector -> ontology -> insight -> foundry -> app. Ghost mode dry-runs. Ranks three Cortex coordination patterns and applies the winner.

**Is not:** n8n, Activepieces, React Flow, or a second `dag_runner`. README forbids cloning n8n/Activepieces. Engine stays Cortex.

---

## 2. vs `@xyflow/react` (MIT)

xyflow is a node editor. Constructor is 11 files (custom canvas in `app.js` / `engine.js` / `index.html`). Score: **2 / 10** as an editor, **4 / 10** as a Cortex IR compiler.

`npm i @xyflow/react` only if the canvas must *feel* like React Flow. Do not replace `compileIR`.

---

## 3. Compiler (this VM)

HEAD `engine.js` compiled IR for Cortex kinds. Ranking mixed foundry-boost into `rankApproaches` (DOM-only). This VM extracted `rankForKinds` + `compileIR` export and added `tests/compiler.test.cjs`.

```
node --test tests/compiler.test.cjs
```

**19 passed** on this VM 2026-08-27 after `constructor-tool-action.patch`: verify-rank, ghost false, empty graph / unknown kind / cycle / dangling edge / missing id / duplicate id invent no Cortex nodes; `ghostWalk` refuses those instead of walking `topo()` leftovers; connector-only graphs do not invent `EMIT` (app/audit output still does); unlabeled `tool_call` does not invent `export_pptx`.

Patches: `docs/patches/constructor-compiler-tests.patch` then `docs/patches/constructor-empty-graph.patch` then `docs/patches/constructor-ir-refuse.patch` then `docs/patches/constructor-ir-ids.patch` then `docs/patches/constructor-ghost-refuse.patch` then `docs/patches/constructor-ir-emit.patch` then `docs/patches/constructor-tool-action.patch` (also a `test.yml` workflow). Push 403.

GitHub on default `landing-9-first-path`: **pages.yml** is green. There is **no unit-test workflow** on HEAD until that patch lands.

---

## 4. Trust boundaries

| Boundary | Today |
|---|---|
| Ghost dry-run | `ghostWalk` uses `compileIR`; refuse means empty log, no leftover cycle walk. `topo()` still appends leftovers for the UI |
| Writes | Cortex, not Constructor |
| Keys | none in this tree; engine URL is Cortex |

---

## 5. Verify

```
NEEDS-YOU TAS-CONSTRUCTOR  grant write on Netie-AI/constructor and land the compiler-test patch
```

Then: GitHub `test` workflow green on `node --test tests/compiler.test.cjs`. Do not add xyflow until a buyer needs the editor feel.
