# TAS-AIRGPT - AirGPT technical architecture

**Plane:** 4 (customer host shell) · **Repo:** `jian-hong/AirGPT` (this token: not found)
**Measured:** 2026-08-27 from OpenVault contracts and TAS-dated estate docs, **not** from an AirGPT checkout. Chunker claims below are UNVERIFIABLE until the repo is in this environment.

---

## 1. What it is

The customer host shell: chat, settings, pairing, apps hub, phone-PC sync, ClipDrop key ingest, optional FreeIDE on `:8765`. Thin client of OpenVault for custody and of Cortex for brains.

**Is not:** a second vault, a second `dag_runner`, or ChatGPT.

---

## 2. Entry points (from OpenVault evidence)

| Path | Role | Evidence |
|---|---|---|
| `:8765` | AirGPT + FreeIDE | OpenVault DR-0004 ports table |
| `FreeIDE/openvault_bridge.py` | ping/status/mesh/gate | DR-0004 |
| ClipDrop ingest | `POST /api/keys/ingest` on OpenVault | `CLIPDROP_CONTRACT.md` |
| `rag/ingest.py` | source ingest jobs | `ASKS_CLAUDE_QUEUES_RAG.md` Ask C/D |
| `rag/store.py` `ingest_jobs` | job store | same |
| `docs/who-does-what.md` | named, not fetched | same |

---

## 3. RAG / chunking - the founder's questions

Asked: regex-friendly on broken tables, repeated headers, keyword labels, multilingual embeddings, selectable models.

**What the OpenVault notes actually say:**

- Spaces exist; "Good Good" Space 5 must not cite `chat_*.md` after purge (`chats_as_evidence: false`).
- Fabrication scrub on chat-ingest is a *plan*, path `rag/ingest.py`.
- Ingest-time authority column: spec only.
- File-scoped retrieve on @-mention must not leak other spaces.
- Async create: `POST .../sources` returns `{ job_id }`; poll `pollRagIngestJob`.
- NVIDIA_RAG_EVAL is a *model catalog* (NIM 8B-70B), not a chunker.

**What we cannot claim:** regex vs semantic split, table reconstitution, embedding model picker, multilingual adaptive routing. Those need `rag/` on HEAD.

Portable corpus in this repo (AirGPT still 404): `scripts/airgpt_chunk.py`. Repeated headers are not extra rows, ragged short rows do not invent cells, extra cells are dropped (not a nameless column), `# warehouse:` labels stick to following rows. `retrieve_space` cites only complete chunks labeled for that Space; unlabeled and incomplete rows are not evidence; north cannot cite south; `chat_*.md` is not evidence (`chats_as_evidence` defaults false); file mention cannot pull another Space's file. `chunk_table(splitter="nvidia_rag_eval")` / `semantic` / `llamaindex` raises; retrieve with that embedder abstains. `cross_chat_memory` abstains. Retrieve over DitchContext 12k abstains (no silent drop). `python3 scripts/test_airgpt_chunk.py`. Not LlamaIndex; a splitter we own until HEAD is measured.

Closest licensed kits *after* measure, not before: LlamaIndex (MIT) or a small splitter we own. Do not paste ChatGPT.

---

## 4. Trust boundaries (from contracts)

| Boundary | Enforced? |
|---|---|
| No second vault | ClipDrop: secret in RAM only; fail closed if OpenVault down |
| Leave-machine | OpenVault gate; DR-0004 said gate closed offline |
| RAG isolation across Spaces | Required in Ask C; not verified here |

---

## 5. vs ChatGPT

ChatGPT is a hosted assistant with memory, tools, and a huge eval set. AirGPT is a *shell* that is supposed to show Cortex answers with sources. Distance without HEAD: **UNVERIFIABLE**. Historical size (619 files, 158 tests) is founder-stated, not cloned.

---

## 6. Verify

```
NEEDS-YOU TAS-AIRGPT  add jian-hong/AirGPT (or Netie-AI/AirGPT) to this environment
```

Then: pytest on `rag/` against this corpus, and a live Space-5 cite check with zero `chat_*.md`.
