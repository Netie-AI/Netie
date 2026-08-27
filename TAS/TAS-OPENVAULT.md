# TAS-OPENVAULT - OpenVault technical architecture

**Plane:** 2 (custody and routing) · **Repo:** `Netie-AI/OpenVault` (public)
**Measured:** 2026-08-27 against clone HEAD `62bb1c7` (GitHub `main`, CI green).
This cloud environment does not vendor OpenVault; measurements are from a throwaway clone under `/tmp/netie-measure/OpenVault`.

---

## 1. What it is

The custody and routing plane: encrypted keys, leave-machine / deploy gate, FreeRoute OpenAI-compatible gateway on the same process as `:5000`, FreeBuild ship adapters, local mesh to Cortex.

**Is not:** an agent loop, OmniRoute, Vercel, or a second Cortex.

---

## 2. Entry points

| Path | Role |
|---|---|
| `OpenMW/` uv app | Custody API `:5000` |
| `apps/web/` Next 16 | UI `:3010`, wired only to `:5000` (DR-0003) |
| `apps/shell/` Electron | Desktop shell |
| `nvme_sentinel/` | NVMe HAL library (own uv root) |
| `Profiler/` | PathTrace library (own uv root) |
| `OpenMW/openmw/openvault/route/` | FreeRoute strategies, breaker, rotator |
| `OpenMW/openmw/openvault/ship/` | Detect / build / host adapters |
| `OpenMW/openmw/openvault/vault/` | Keys, proxy, metering |

---

## 3. Trust boundaries

| Boundary | Enforced by | Note |
|---|---|---|
| Keys | vault store; STATUS still has custody reopen #13 | One vault. `env.local` elsewhere is cache. |
| Leave-machine / deploy | `/api/gate/check`, `ship/gate.py` | HUMAN_STOP on live HT1-HT5 |
| FreeRoute identity | metering: issued `ov_` keys, not spoofable headers | tests in `test_freeroute_metering.py` |
| Circuit breaker | `route/breaker.py` | 408/500/502/503/504 trip |
| Ship honesty | `SHIPPING_MODEL.md`: never report success not observed | Pages adapter real; simulated host is a loud fail |

---

## 4. FreeRoute vs OmniRoute vs NVIDIA (short)

FreeRoute is **OpenVault `:5000/v1`**, not a process on `:20128`. OmniRoute remaining as an external optional.

Shipped strategies on **main** (8): priority, weighted, fill-first, round-robin, p2c, random, least-used, cost-optimized.

This VM patches (not on main, push 403): `strict-random` (9th), `lkgp` (10th), `context-optimized` (11th), `headroom` (12th). Context sort uses caller-supplied `context_window`, not OmniRoute's model catalog. Headroom uses caller-supplied util_5h/util_7d, not a provider quota fetch.

Not shipped vs OmniRoute: provider catalog at OmniRoute scale, token compression, MCP/A2A, the remaining 7 user-facing strategies, Electron Next-on-20128.

Not the same job as NVIDIA llm-router (trained task/complexity classifier on Triton).

---

## 5. FreeBuild vs Vercel (short)

Design: user machine builds, user cloud hosts, OpenVault is the button. Cloudflare Pages via wrangler is the first real adapter. STATUS: no live box has completed HT1. This is not a Vercel replacement until HT1 is green on a stranger's token.

---

## 6. Data stores

Vault SQLite (sealed), optional Redis for FreeRoute buckets, `openvault.local.json`. Master-key plaintext backup is a named DR (DR-0010) - treat as dangerous.

---

## 7. Shipped vs scaffold

**Shipped enough to test:** vault, gate refuse paths, FreeRoute metering/tests, 8 strategies on `main` (9th-12th in `docs/patches/`, 16 strategy tests passed here, push 403), Pages adapter code, Next UI, Electron shell, NVMe library, CI.

**Local evidence 2026-08-27** (clone HEAD `3030cad`, this VM):

- `uv run pytest tests -q` after replacing D:\\ tree skips with tmp_path fixtures -> **840 passed, 4 skipped** (Windows DPAPI only)
- Push of that patch to `Netie-AI/OpenVault` returned **403** (cursor[bot] cannot write sibling repos). Patch lives on local clone branch `cursor/detect-stacks-no-skip-ca9b` until a token with OpenVault write lands it.

**Not shipped as a buyer claim:** live deploy (HT1), pricing, "better than Vercel", OmniRoute-complete routing, NVMe product as the thing we sell (library, not the SKU).

STATUS.md 2026-08-25: **~75%**, HUMAN_STOP on #18.

---

## 8. Verify (in the OpenVault repo, not here)

```bash
uv sync && uv run ruff check . && uv run pytest tests/unit tests/integration -q
cd OpenMW && uv sync && uv run pytest tests -q --cov=openmw.openvault --cov-fail-under=75
```

**GitHub CI on default `main`:** last push (docs/status #45, 2026-08-27 15:12 UTC) **success**. `POST /api/crew/gate` is **not** on main (OpenVault PR #44 plus focused `docs/patches/openvault-crew-gate.patch`: unknown `skill` kind refuses, no skill body). HT1-HT5 HUMAN_STOP. STATUS ~78%.
