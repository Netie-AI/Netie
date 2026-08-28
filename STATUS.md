# STATUS - Netie constitution repo

**Branch:** `cursor/ecosystem-scale-constructor-0d3c` · **PR:** https://github.com/Netie-AI/Netie/pull/11
**Local gate:** `make ci`. GitHub docs-ci never starts (Actions spending limit).

## Now

- Leak: `Keys.txt` gone; scan gate on. **Founder must revoke** keys (`docs/ACCESS.md` §5). History still has blobs.
- Constructor first on public `4896ddd`: 13 patches, `node --test` **31 passed** (inspect `(pick)` for object/point/tier). Original `inspect-object` still drifted. Portable `constructor_ir.py`.
- Crew: `crew_durable.py` + `crew_skills.py` (skill kind needs a registry row). Cortex-Crew remote still 404.
- OpenVault: `freeroute_free_pool.py` + `openvault-free-pool.patch` + `openvault-free-pool-route.patch` (`POST /api/route/free`). Memory: `scripts/ov_memory.py` (Graphiti/zep/graphify refuse).
- DMS Palantir-next: `dms_ontology.py` + `dms-demo-acl-resolve.patch` (`demo_acl` returns `resolve_session_acl`). Pointer HEAD `8c0e6c2`: 15 catalog ids in `pointer_hands.py`.
- Agent lanes: `TAS/ESTATE-GAP.md` section 6. Other org repos: section 7 (not product path).

## Next (founder clicks in `docs/ACCESS.md`)

1. Revoke leaked keys. 2. Create `Netie-AI/Cortex-Crew`. 3. Pay Actions. 4. Write on OpenVault + constructor. 5. Land dms resolve patch; `from netie.dms import mint_object`.

## Later

HT1. AirGPT `rag/`. Palantir callers in dms. Do not mint Cortex #42. Do not clone Grok Bot reconstructed.
