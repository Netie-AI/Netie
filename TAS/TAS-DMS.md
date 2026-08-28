# TAS-DMS - DMS technical architecture

**Plane:** 4 (application) · **Repo:** `Netie-AI/dms` · `D:\DMS`
**Measured:** 2026-08-02 against `feat/grounding-promote-spaces-boundary`. Verified
against code, not documentation.

---

## 1. What it is

A FastAPI + React consumer app over the Cortex engine: Spaces, Studio ingest, governed
chat, audit, pipelines. It talks to Cortex over HTTP only and never imports `CortexOS`.

---

## 2. Entry points

| Path | Role |
|---|---|
| `apps/api/dms_api/app.py:100` | `create_app()`; `:136` module-level `app` |
| `apps/api/dms_api/app.py:64` | `lifespan()` - alembic migrations, demo tenant seed, Space store binding, `CortexClient` + `AskService` |
| `apps/ui/src/App.tsx:18-34` | React Router (Vite), 10 pages |
| `packages/ledger/dms_ledger/verify_cli.py` | `dms-verify-ledger` CLI |
| `deploy/compose/docker-compose.yml` | postgres + api + caddy; **Caddy on :8080 is the only published port** |

---

## 3. Layers

```
apps/ui          10 React pages: Chat Spaces Library Studio Ontology Amend Audit Trust Runs Admin
apps/api         FastAPI routes; may only reach executor via dms_api.wiring
packages/ledger  Cortex ledger append/verify
packages/executor  DuckDB, ingest, promote, manifest minting, envelope
packages/cortex_client  generated OpenAPI client
packages/core    domain types and the five ports
```

Import order is **enforced** by `.importlinter`: `dms_api > dms_ledger > dms_executor >
cortex_client > dms_core`, and none of the five may import `CortexOS`.

---

## 4. Trust boundaries

| Boundary | Enforced by |
|---|---|
| Compliance gate before mutations | **ENFORCED** - `gatekeeping.py:57 enforce()` refuses (403) on `gate_unavailable` / `gate_task_unknown` |
| Session manifest | **ENFORCED by Cortex**; minted and Ed25519-signed here at `executor/manifest.py:165` over `canonical_manifest_bytes` from the pinned wheel |
| Postgres tenant isolation | **ENFORCED** - RLS `ENABLE + FORCE` on all 13 tenant tables, policies on `current_setting('dms.tenant_id')` (alembic `0001:252-288`) |
| Answer envelope E1-E8 | **ENFORCED** - `envelope.py:195 assert_envelope_valid` on every construction path |
| Storage-durability honesty | **ENFORCED** - `store/binding.py` reports the binding that happened, not the configured intent |
| Warehouse browse allowlist | **ENFORCED** for demo tables (`warehouse_browse.py:18`); **NOT** for bronze (`:66-77`) |
| `chat.ask` gate | **PARTIAL** - `routes/chat.py:112-119` hand-rolls a soft allowance instead of calling `enforce()` |
| Hostile SQL pre-check | **ADVISORY ONLY** - `manifest.py:288` |
| **Space ACL** | **NOTHING ENFORCES IT** |
| **Caller identity / authn** | **NOTHING ENFORCES IT** |

### The two that matter

**Space ACL is decorative.** `Executor.live_ask` (`executor/__init__.py:213`) mints from
`demo_acl(...)`, which at `:140-151` sets `row_predicates = {t: 'TRUE'}` over all six
`DEMO_TABLES` **regardless of `space_id`**. Two different Spaces mint byte-identical
predicates. The correct functions - `resolve_session_acl`, `intersect_space_grants`,
`mint_manifest_for_session` - exist in `executor/acl.py`, are unit-tested, and have **zero
callers**. Scoping decided in DR-0002; wiring tracked at `Netie-AI/dms#2`.

**There is no authentication.** Every route is anonymous. `middleware_actor.py` trusts
`x-dms-tenant-id`, `x-dms-actor-id` and `x-dms-role` verbatim from the request, and its
own docstring says it is "not a security boundary for production." The compliance gate is
fail-closed but has nothing trustworthy to gate *on*.

---

## 5. Data stores

| Store | Where |
|---|---|
| Postgres schema `dms` | 13 tables, alembic `0001:39` |
| DuckDB serving warehouse | `D:\DMS\data\dms_demo.duckdb` (`DMS_WAREHOUSE_DB`) |
| Blob tier | `<warehouse>/blobs/sha256/<aa>/<bb>/<sha>` - the only `ObjectStorePort` implementation |
| `bronze._ingest_registry` | table_name PK, filename, sha256, ingest_id |

**Correction to `CLAUDE.md:71`.** It asserts "One Postgres, two schemas (`cortex`,
`dms`)". Only `dms` exists - `CREATE SCHEMA` appears exactly once in the tree, and zero
times under `D:\Cortex`. A doc claim with no implementation and no failing check.

---

## 6. Ingest: what works and where it stops

This is the demo-day path, so it is worth being precise.

**Works.** `POST /v1/studio/ingest-batch` accepts multi-file and folder upload, classifies
every sheet with openpyxl read-only, returns a per-file receipt naming a reason and a fix.
Bronze CSV ingest carries row provenance (`_src STRUCT(ref_id,row)[]`, `_ingest_id`) and
builds-beside-then-swaps so a parse failure cannot destroy the previous table.
`infer_contract` genuinely derives types, null rates and candidate keys from an unseen
table with no human input.

**Stops.** Only 2 of 5 `SheetClass` outcomes reach a queryable table. `MULTI_TABLE` and
`HEADERLESS` dead-end at `batch_ingest.py:80-84`. `UNSTRUCTURED` sets
`document_index = "pending"` - a literal string nothing reads.

**The bridge that does not exist.** `infer_contract` returns a `ContractProposal` over
HTTP; `POST /v1/pipelines/run` requires a `pipelines/*.yaml`. **Nothing converts one into
the other.** `pipelines/` holds exactly one hand-written YAML. So onboarding a customer
table is a human writing YAML.

**Two warehouses.** Studio writes bronze into `D:\DMS\data\dms_demo.duckdb`; Cortex
answers from `D:\Cortex\data\dms_demo.duckdb` (`CortexOS/execution/warehouse.py:16`).
Measured: 18 tables vs 6. An uploaded spreadsheet is unreachable by chat, silently.
Tracked at `Netie-AI/dms#4`, `#5`, `Netie-AI/Cortex#14`.

---

## 7. Scaffold - exists, no caller

- `executor/acl.py` in full
- Four of the five ports (`CatalogPort`, `ObjectStorePort`, `ModelProviderPort`,
  `SecretsPort`) - no implementer, no call site
- `dms.acl_grants` and `dms.source_ref` - no writer outside the migration
- `POST /v1/amend/proposals/{id}/confirm` - its own docstring says confirming moves a
  status "and that is the whole of it - no `call_action`"
- `document_index` for unstructured uploads
- `docs/ACTIVE.md` is a 4-line stub

---

## 8. Dependencies

| On | How |
|---|---|
| Cortex `:8010` | `/v1/contract/{submit,ask,drillthrough,ledger/append,ledger/verify}` plus the off-contract F5 gate |
| OpenVault `:5000` | `POST /keys/services` then `/keys/intermediate` for an Ed25519 key held **in RAM only** |
| `cortex-contract` | wheel pinned `>=1.2.0,<2`; `canonical_manifest_bytes` imported at `manifest.py:17` |
| Postgres | optional - absent falls back to an in-process store and a hardcoded 3-row source fixture |

---

## 9. Structure problems

1. `DEMO_TABLES` is three responsibilities in one tuple (`demo_warehouse.py:24-31`): seed
   list, chat manifest allowlist, and Library browse allowlist. Adding a customer table
   requires editing a literal.
2. `chat.ask` duplicates the gate logic `gatekeeping.py` exists to centralise - two copies
   of the same allowance list is the divergence class that docstring warns about.
3. Bronze preview has no allowlist while warehouse preview does. Same route family, two
   postures.
4. Duplicate demo-ask modules: `executor/demo_ask.py` (557 lines, real) and
   `apps/api/dms_api/scenarios/demo_ask.py` (9 lines, a `RuntimeError`).
5. Root holds `DMS_TECHNICAL_ARCHITECTURE.md` (41 KB) and `DMS_PRICING_AND_TIMELINE.md`
   (18 KB) beside the five governed files, and `STATUS.md` calls the former "north star" -
   which the five-file law does not allow. **This document supersedes it.**
6. `vendor/dbgate` is a vendored third-party tree polluting repo-wide greps.

---

## 10. Verify

```bash
python -m pytest tests/ -q
```

Measured 2026-08-02: **166 passed, 3 xfailed** in 58.73s. The 3 xfails are the strict
Space-ACL boundary suite and are correct until `#2` lands.

Portable contract in this repo (dms remote still 404): `scripts/dms_space_acl.py`.
Two Spaces, named warehouse bind, abstain outside ACL, abstain if Cortex DuckDB
is asked for a DMS-bound Space, abstain if the answer has no SQL, abstain if SQL
names a table the Space cannot read (JOIN punch), abstain if SQL omits the asked table,
abstain bronze/warehouse browse of an ungranted table, abstain `chat_mode=True`
(AnythingLLM overlay; warehouse answers need SQL).
`python3 scripts/test_dms_space_acl.py`.
Not a patch on dms; the production caller is still `demo_acl()` until that repo is writable.

```bash
lint-imports
```

Not `python -m importlinter.cli lint` - that exits 0 running nothing on Windows.
