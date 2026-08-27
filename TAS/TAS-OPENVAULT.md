# TAS-OPENVAULT - OpenVault technical architecture

**Plane:** 2 (custody and routing) · **Repo:** `Netie-AI/OpenVault` (public)
**Measured:** 2026-08-27 against clone HEAD `3030cad78e319fa5867310c406662cb3171abdc1`.
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

Shipped strategies (8): priority, weighted, fill-first, round-robin, p2c, random, least-used, cost-optimized.

Not shipped vs OmniRoute: provider catalog at OmniRoute scale, token compression, MCP/A2A, 10 strategies, Electron Next-on-20128.

Not the same job as NVIDIA llm-router (trained task/complexity classifier on Triton).

---

## 5. FreeBuild vs Vercel (short)

Design: user machine builds, user cloud hosts, OpenVault is the button. Cloudflare Pages via wrangler is the first real adapter. STATUS: no live box has completed HT1. This is not a Vercel replacement until HT1 is green on a stranger's token.

---

## 6. Data stores

Vault SQLite (sealed), optional Redis for FreeRoute buckets, `openvault.local.json`. Master-key plaintext backup is a named DR (DR-0010) - treat as dangerous.

---

## 7. Shipped vs scaffold

**Shipped enough to test:** vault, gate refuse paths, FreeRoute metering/tests, 8 strategies, Pages adapter code, Next UI, Electron shell, NVMe library, CI (`ruff` + `mypy nvme_sentinel` + OpenMW pytest cov-fail-under 75).

**Local evidence 2026-08-27** (clone HEAD `3030cad`, this VM):

- `uv run pytest tests/test_contract.py tests/test_freeroute_metering.py tests/test_streaming_v1.py tests/test_attempt_policy.py -q` -> **78 passed** in 5.51s
- `uv run pytest tests -q` -> **837 passed, 7 skipped** in 50.53s

R-0002 in the constitution says a skipped test is a failing test. Those 7 skips are OpenVault HEAD's problem, not this docs repo. GitHub Actions on OpenVault recently succeeded on a PR branch (`cursor/account-key-tenant-custody-37d7`).

**Not shipped as a buyer claim:** live deploy (HT1), pricing, "better than Vercel", OmniRoute-complete routing, NVMe product as the thing we sell (library, not the SKU).

STATUS.md 2026-08-25: **~75%**, HUMAN_STOP on #18.

---

## 8. Verify (in the OpenVault repo, not here)

```bash
uv sync && uv run ruff check . && uv run pytest tests/unit tests/integration -q
cd OpenMW && uv sync && uv run pytest tests -q --cov=openmw.openvault --cov-fail-under=75
```

This Netie docs repo does not run those commands as its own CI.
