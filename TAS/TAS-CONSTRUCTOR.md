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

`npm i @xyflow/react` only if the canvas must *feel* like React Flow. Do not replace `compileIR`. Portable `scripts/constructor_honesty.py` refuses `@xyflow/react` as the compiler.

---

## 3. Compiler (this VM)

HEAD `engine.js` compiled IR for Cortex kinds. Ranking mixed foundry-boost into `rankApproaches` (DOM-only). This VM extracted `rankForKinds` + `compileIR` export and added `tests/compiler.test.cjs`.

```
node --test tests/compiler.test.cjs
```

**62 passed** on this VM 2026-08-28 after `constructor-ir-kahn-nodes.patch`: verify-rank, ghost false, empty graph / unknown kind / cycle / dangling edge / missing id / duplicate id invent no Cortex nodes; `ghostWalk` refuses those instead of walking a fake order; `topo()` does not append leftover cyclic nodes; `compileIR` entry is the Kahn source not `nodes[0]`; `compileIR` output is the Kahn sink app (or unique Kahn sink when no app/audit) not array-last; disconnected graphs refuse (two workflows are not one IR); a fork with no app refuses (`ambiguous output`; a join still emits the app); canvas notes do not ride into Cortex IR (a `skill_body` / prompt / transcript note refuses; notes over DitchContext 12k refuse); ghost/run/fetch/recommend POST compiled IR (`cortexPayload` body is `compileIR` in Kahn order, not canvas array order; unlisted `hr_notes` / `salary` / canvas `x` do not leave; leaked or disconnected graphs do not leave the machine); `compileIR` drops unlisted `object_type` (`hr_notes` / `Insight` are not Cortex ontology); `fetch_from` must name this node's listed object (not `warehouse.hr_notes` or `warehouse.suppliers` on inventory); `data_point` must be on that object (not `salary` on inventory); `tool_call` unknown action (`bash`) refuses; unlisted action on a non-tool node is dropped; `export_pptx` / `item.intake` / `amend.apply` / `call_action` on foundry set `requires_confirm` (`agent.checked` stays an event); connector-only graphs do not invent `EMIT` (app/audit output still does); unlabeled `tool_call` does not invent `export_pptx` (compileIR refuses; inspect shows `(pick)`); unlabeled object does not invent `inventory`; unlabeled tier does not invent `T0` (compileIR emits null; inspect shows `(pick)`); unlabeled `set point` does not invent `inventory`; picking `object_type` does not invent the first `data_point` (`sku`; inspect stays `(pick)`); `index.html` loads `engine.js` before `app.js` so those inspect gates exist on first paint (`bindWhenReady` waits for `window.Constructor`).

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
