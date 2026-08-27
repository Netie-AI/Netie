# TAS-CORTEX - Cortex technical architecture

**Plane:** 3 (reasoning and governance) · **Repo:** `Netie-AI/Cortex` · `D:\Cortex`
**Measured:** 2026-08-02. Route counts were obtained by **building the app**, not by
reading source.

---

## 1. What it is

The governed execution engine: a FastAPI app that turns a question or goal into an answer
or action **carrying its own evidence** - the SQL that ran, the rows behind it, the signed
manifest that authorised the read, the ledger entry for the write - and refuses when it
cannot prove the work stayed inside what was granted.

**It is not an inference server.** There is no serving runtime: no batching, no KV cache,
no CUDA path. `grep "chat/completions"` across `CortexOS` returns nothing. Tokens are
bought through litellm (self-hosted vLLM default `http://127.0.0.1:8000/v1`) or via
OpenVault FreeRoute. See `NETIE.md` section 2 for why that is a deliberate decline.

Portable path check in this constitution repo (Cortex still 404 here):
`scripts/cortex_path.py` / `python3 scripts/test_cortex_path.py`. JEPA and gen-cFSM are
refused as route candidates. A tool that skips `tool_runner` is refused.

---

## 2. Entry points

| Path | Role |
|---|---|
| `CortexOS/api/app.py:10` | `create_app()` - the single app factory |
| `CortexOS/api/main.py:5` | `app = create_app()`; uvicorn target `CortexOS.api.main:app` |
| `scripts/start_cortex_engine.ps1:126` | uvicorn on port 8010 (default) |
| `Dockerfile.core:33` / `Dockerfile.full:34` | `CMD uvicorn ... --host 0.0.0.0 --port 8010` |

Two traps worth knowing:

- **`CortexOS/cli.py` is 0 bytes** and tracked (git empty blob), with zero importers.
  `pyproject.toml` declares no `[project.scripts]`, so **there is no CLI**, despite typer
  and rich being hard dependencies.
- **`netie.*` is an import alias, not a directory.** `netie/__init__.py:15` installs a
  `sys.meta_path` finder resolving every `netie.*` import to the same module object as
  `CortexOS.*`. Half the router imports in `app.py` spell it `netie.api.*`. **Grepping one
  spelling undercounts.**

---

## 3. HTTP surface - measured

| Pack | Paths |
|---|---|
| `PACK=dms` | **174** |
| default pack | **90** |

The 84-path delta is all `/dms/*` plus `/a2a/messages`, registered only inside
`if pack.name == "dms"` (`app.py:100-149`). **The shipped default is the smaller one.**

```powershell
cd D:\Cortex; $env:PACK='dms'
.venv\Scripts\python.exe -c "from CortexOS.api.app import create_app; import json; print(len(create_app().openapi()['paths']))"
```

Groups: `/v1/contract` (7) · `/api/engine` (17) · `/api/workflows` (10) ·
`/api/routines` (11) · `/api/apps` (10) · `/api/goals` (5) · `/api/commitments` (4) ·
`/api/discovery` (9) · `/api/memory` (3) · `/api/context` (4) · `/mcp` (2) · `/run` ·
`/search` · `/health` (3) · and 83 `/dms/*`.

Optional route modules register as **HTTP 501 stubs** rather than vanishing when an extra
is missing (`feature_stubs.py:28`) - so the route table is stable across profiles.

---

## 4. Trust boundaries

| Boundary | Enforced by | Bypass |
|---|---|---|
| Manifest-enforced reads | `execution/manifest.py`, wired via `submit.py:189` | **`POST /dms/query` - `verified` is optional on `answer_engine.answer`** |
| Hash-chained ledger | `packs/dms/audit/ledger` | one ledger, consumers append through Cortex |
| Governed tool call | `execution/tool_runner.py:136` - allowlist, agent denial, path escape, sanitize, compliance, ledger on both verdicts | `agent_task.default_broker:90` checks web tools **before** falling through to F8, so `web_search`/`web_fetch` reach the network ungoverned |
| RBAC | `require_role` in ~10 route modules | **absent from `app_routes`, `dag_run`, `dms_query`, `chat_routes`** - the modules that execute code and run SQL |
| C2 pack boundary | `.importlinter` + `tests/contract/test_import_boundaries.py` | **false green** - see below |
| WASM sandbox | nothing | modules are 0-byte; `wasm_isolate.py` has zero production callers |

### The C2 false green

**C2 pack boundary** and **MIN_TESTS** stand as measured. This Netie branch does not mint Cortex issues (no #42) and does not edit Cortex PRs. The C2 false green stays a Cortex-repo fact (`Cortex#9`).

---

## 5. The decision core, honestly

**One live automatic selector**, not three: `race_router.auto_route` behind
`POST /api/engine/auto`. Requires cosine >= 0.80 against a family centroid **and** a
stored winner with >= 3 runs; otherwise probes the top 3 concurrently, scores
predicates-over-judge, re-runs the winner at scale. Plus `workflow_recognizer.recognize`
choosing a workflow template.

**Code-only, no request path:**

- `osr.route` - the known/near/open band gate. `POST /api/engine/osr` is classify-only by
  its own docstring.
- `gen_cfsm` - no HTTP entry, and cannot enter a race pool because `COLD_START_ORDER` is
  `minimal|sequential|dag` and `auto_route` never passes candidates.

**JEPA is a name, not an artefact.** The family gate is a sha256 feature-hash into 64
buckets; `action_value.py:4-5` says so.

**C7 shipped as a fallback behind the cascade, not as a replacement.** `route_to_metric`
runs first (39 `re.search`, 37 `return MetricPlan`); the L2 block starts at `:1513` gated
on `DMS_L2_ENABLED` (off) plus an OpenVault ping plus the leave-machine gate. Measured on
with the corpus: **17 confidently wrong against a floor of 0.** Tracked at
`Netie-AI/Cortex#12`, deferred until a real user exists.

**The action registry has 25 entries and 1 is invocable** - `export_pptx`. "Actions are
the only write path" describes a path with one action.

---

## 6. Data stores

| Store | Where |
|---|---|
| DuckDB serving warehouse | `data/dms_demo.duckdb` - `execution/warehouse.py:16`. **Different file from DMS's.** |
| SQLite ops DB | `packs/data/dms_ops.db` - ontology, ledger, skills |
| DuckLake bronze/silver/gold | `data/lakehouse/` |
| Qdrant | in `docker-compose.yml`; the RAG that actually runs is `rag/lexical.py`, dependency-free TF-cosine, in-memory |
| Per-device key | `CortexOS/data/` - **gitignored, never commit** |

All runtime state is gitignored and regenerated.

---

## 7. Contract

`packages/cortex_contract/` - models and Protocols only, zero `CortexOS` imports.
Frozen specs in `contract/`: `openapi-1.0.0`, `1.1.0`, `1.2.0` plus `.sha256` sidecars.
Engine version `2.5.0` and contract version `1.2.0` are **independent lines**, asserted by
`scripts/check_versions.py`.

`canonical_manifest_bytes()` is the most dangerous function here - DMS signs those exact
bytes and Cortex verifies them. As of 2026-08-02 the spec generator writes with
`newline="\n"` so the sidecar matches its own file on every platform; before that fix the
gate could not pass on Linux.

**Open defect:** `cortex_contract` and `packages.cortex_contract` resolve as two module
identities of one file. Tracked at `Netie-AI/Cortex#5` - must land before any wheel.

---

## 8. Structure problems

1. `CortexOS/AirGPT/` and `CortexOS/Vertex/` are untracked working mirrors sitting inside
   the engine package - gitignored, not importable, but a footgun for recursive tools.
2. `demo/dms-ui/` duplicates `D:\DMS\apps\ui` - two UIs for one product.
3. `activeflow/activepieces` is a vendored tree; gitignored, 0 tracked files, safe to
   delete per `PARKING_LOT` P4.
4. Root clutter beside the five governed files.
5. `netie.pth` puts `D:/Cortex` on the path of **every** Python process on the machine.
6. Undeclared reverse edge: `bench/corpus.py:210` and `bench/live_probe.py:29` import
   `dms_executor` (Cortex -> DMS), which `CLAUDE.md` does not mention.

---

## 9. Verify

```bash
ruff check CortexOS packages/cortex_contract scripts tests/packaging tests/contract
mypy
lint-imports
python scripts/check_versions.py
python scripts/export_openapi.py --check
python -m pytest tests/ -q
```

Two Windows traps:

- **`lint-imports`, never `python -m importlinter.cli lint`** - the latter exits 0 running
  nothing.
- **`DMS_READ_ONLY_QUERIES=1`** to run the suite while the engine holds the DuckDB file.
  Without it the same run reports 32 failed / 45 errors of pure lock noise instead of
  1310 passed.

CI status 2026-08-02: **green** (`853950b`) - CI, RLS Proof, Secrets Scan all passing.
