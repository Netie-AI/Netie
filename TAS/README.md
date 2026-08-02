# Technical Architecture Specifications (TAS)

Tier 4 living docs per [`Internal/Rules/DOCUMENT_SYSTEM.md`](../Internal/Rules/DOCUMENT_SYSTEM.md).
One file per product. Updated when architecture changes - not a plan (plans are Tier 6).

**Required sections in each TAS:** purpose (one line) · plane · HTTP/library surface ·
dependencies (in and out) · data stores · trust boundaries · shipped vs scaffold · verify
commands.

Constitution and plane law: [`NETIE.md`](../NETIE.md) section 2.

---

## Index

| TAS | Plane | Repo | Local path |
|---|---|---|---|
| [TAS-OPENVAULT](TAS-OPENVAULT.md) | 2 - custody and routing | `Netie-AI/OpenVault` | `D:\OpenVault` |
| [TAS-CORTEX](TAS-CORTEX.md) | 3 - reasoning and governance | `Netie-AI/Cortex` | `D:\Cortex` |
| [TAS-DMS](TAS-DMS.md) | 4 - application | `Netie-AI/dms` | `D:\DMS` |
| [TAS-SPACE](TAS-SPACE.md) | 4 - application (desktop) | `Netie-AI/Space` | `D:\Space` |
| [TAS-AIRGPT](TAS-AIRGPT.md) | 4 - application (host shell) | `jian-hong/AirGPT` | `D:\AirGPT` |
| [TAS-POINTER](TAS-POINTER.md) | 4 - application (computer control) | `Netie-AI/Pointer` | `D:\Pointer` |

PRD stubs (Tier 3): [`Software Blueprint/`](../Software%20Blueprint/) - each product folder
has `PRD-001-*.md`.

---

## Planes (from NETIE.md section 2)

| # | Plane | What lives there | Netie product |
|---|---|---|---|
| 0 | Silicon | GPUs, CPUs, RAM, datacenter, laptop | **No** - rent or use customer hardware |
| 1 | Inference serving | vLLM, Ollama, provider APIs, KV cache, tokens/sec | **No** - buy tokens; OpenVault may proxy |
| 2 | Custody and routing | Keys, model route, leave-machine gate, deploy gate | **OpenVault** |
| 3 | Reasoning and governance | Work shape, evidence, manifest reads, ledger writes | **Cortex** |
| 4 | Applications | What a human sees and clicks | **DMS**, **Netie Space**, **AirGPT**, **Pointer**, FreeIDE |

Cortex is **not** plane 1. There is no serving runtime in Cortex - it calls plane 1 through
litellm or OpenVault FreeRoute.

**Name collision:** DMS "Spaces" (ACL-scoped warehouse sandboxes) and **Netie Space**
(Windows Quick Look desktop app) share a word only. See TAS-DMS and TAS-SPACE.

---

## Custody graph (who calls whom)

```
                    plane 2
                 OpenVault :5000
                 keys / gate / FreeRoute
                      |
        +-------------+-------------+
        |             |             |
   plane 3        plane 4       plane 4
 Cortex :8010    DMS :8080     AirGPT :8765
        |             |             |
        +------+------+------+------+
               |             |
          Pointer         Netie Space
        (outbound)      (plugin + keys)
```

All plane-4 apps should treat OpenVault as the single key vault. `env.local` anywhere is a
cache, not a second source of truth (`NETIE.md` section 3).
