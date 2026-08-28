# STATUS - Netie constitution repo

**Branch:** `cursor/ecosystem-scale-constructor-0d3c` · **PR:** https://github.com/Netie-AI/Netie/pull/11
**Local gate:** `make ci`. GitHub docs-ci never starts (Actions spending limit).

## Now

- Leak: `Keys.txt` gone; scan gate on. **Founder must revoke** keys (`docs/ACCESS.md` §5). History still has blobs.
- Constructor first on public `4896ddd`: 12 patches, `node --test` **29 passed**. Portable `constructor_ir.py` (+ listed object drop, Kahn emit, note leak, unknown action). `inspect-object` still drifted.
- Crew: `crew_durable.py` + `crew_skills.py` (skill kind needs a registry row). Cortex-Crew remote still 404.
- OpenVault: `freeroute_free_pool.py` + `openvault-free-pool.patch` (`pick_free_pool` / register help, no keys).
- DMS Palantir-next: `dms_ontology.py` (granted tables only). Pointer HEAD `8c0e6c2`: 15 catalog ids mapped in `pointer_hands.py`.
- Agent lanes: `TAS/ESTATE-GAP.md` section 6.

## Next (founder clicks in `docs/ACCESS.md`)

1. Revoke leaked keys. 2. Create `Netie-AI/Cortex-Crew`. 3. Pay Actions. 4. Write on OpenVault + constructor. 5. Wire dms `live_ask` off `demo_acl`.

## Later

HT1. AirGPT `rag/`. Palantir callers in dms. Do not mint Cortex #42. Do not clone Grok Bot reconstructed.
