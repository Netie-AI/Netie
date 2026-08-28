# STATUS - Netie constitution repo

**Branch:** `cursor/ecosystem-scale-constructor-0d3c` · **PR:** https://github.com/Netie-AI/Netie/pull/11
**Local gate:** `make ci` (compileall + `python3 scripts/check_docs.py`). GitHub docs-ci: red X, job never starts (Actions spending limit). Not a test fail.

## Now

- GitGuardian leak: `Keys.txt` dump removed in this branch; scan gate on. **Founder must revoke** OpenRouter plus the six other keys (`docs/ACCESS.md` section 5). History still has the blobs.
- Constructor first: 26 JS patches already on main (**62 passed**). Added portable `constructor_ir.py` + `constructor_action_bind.py` (chat must not assume inventory/`export_pptx`/`T0`; unknown piece refuses). Do not vendor Activeflow.
- Crew durable resume `crew_durable.py` plus OpenVault `freeroute_free_pool.py` (empty free pool is 503 + register help). `Netie-AI/Cortex-Crew` still missing. Handwritten map: `TAS/ESTATE-GAP.md` section 6.

## Next (blocked on founder clicks in `docs/ACCESS.md`)

1. Revoke leaked provider keys (ACCESS.md section 5). OpenRouter first.
2. GitHub App select private repos. Create `Netie-AI/Cortex-Crew`.
3. Pay / raise https://github.com/organizations/Netie-AI/settings/billing
4. Write on OpenVault + constructor.
5. Wire contracts into product callers (PRD-001 in dms; PRD-002 `from netie.crew import bind_deep_agent, crew_harness_profile`).

## Later

OpenVault HT1. AirGPT `rag/` vs corpus. Pointer vs UACC on HEAD. Palantir-class DMS after Space ACL callers.

C2/MIN_TESTS stand. Do not mint Cortex #42. Do not touch Cortex PRs #4 #41 #43 #44.

Do not clone `b-nnett/grok-bot-0.18-reconstructed`. Do not take account passwords.
