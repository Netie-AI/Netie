# STATUS - Netie constitution repo

**Branch:** `cursor/branch-build-scale-ca9b` · **PR:** (this) · **main:** `f6c1512`
**Local gate:** `make ci`. GitHub docs-ci on `f6c1512` ran ~33s then failed (`python -m pytest` missing). This branch drops that invoke.

## Now

- Keys: `Keys.txt` untracked; OpenROuter sample uses `$OPENROUTER_API_KEY`. Scan gate on. **Founder must revoke** (`docs/ACCESS.md` §5). History still has blobs.
- Portable callers (scores stay): Crew `persist`/`resume`/`register_skill`; DMS `mint_object`; Pointer `bind_pointer_skill` (15 HEAD ids); route `compile_ir`/`assist_free_pool`/`remember`. Cortex `run_question` needs `role` on write/tool. Cortex stamp still `CortexOS.constitution` (do not `uv add` Netie.git).
- Constructor sibling stays **26 patches / 62 passed**. `constructor-*-4896ddd.patch` is a thinner alternate; do not mix. OpenVault + free-pool. dms + `dms-demo-acl-resolve.patch`. C2/MIN_TESTS stand.
- HEADs unchanged (clone yes, push 403): Cortex `bf4ecee`, dms `3f9a9be`, Pointer `8c0e6c2`, control `82ab1ae`, OpenVault `62bb1c7`, constructor `4896ddd`, KB `10356e5`. 404: AirGPT, Space, Cortex-Crew.
- Open Netie PRs left: #11 (CONFLICTING scale, this PR supersedes), #10 (redact, folded here), #8, #6, drafts #5-#2, #1. Merged: #13 #12 #9 #7.

## Next (founder clicks in `docs/ACCESS.md`)

1. Revoke leaked keys. 2. Pay https://github.com/organizations/Netie-AI/settings/billing
3. Contents write on product remotes. 4. Land product patches. 5. Create Cortex-Crew.

## Later

HT1. AirGPT `rag/`. Do not mint Cortex #42. Do not clone Grok Bot reconstructed.
