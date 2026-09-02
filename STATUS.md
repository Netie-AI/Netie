# STATUS - Netie constitution repo

**Branch:** `cursor/ship-claim-ov-ca9b` · **PR:** (this) · **main:** `dbc812f` (docs-ci green)

**Local gate:** `make ci`.

## Now

- `claim_deploy(ov=)` forwards to `report_deploy` which POSTs skill ids. Live engine and `/api/ship/engine` pass the gate when `parent_run_id` is set. No run ids: parse only, no POST. Simulated is still not HT1. Score stays **2/10**.
- Founder apply-all: `python3 scripts/apply_product_patches.py --dry-run`. Product remotes clone-yes push-403. 404: AirGPT, Space, Cortex-Crew. Keys.txt gone; founder must revoke. C2/MIN_TESTS stand.

## Next (founder clicks)

1. Revoke leaked keys. 2. Contents write on product remotes + add those URLs to env e/eb1a4238-9fe4-11f1-b532-320a589b8025, then boot a new agent. 3. Create Cortex-Crew. 4. Run `apply_product_patches.py` on a write machine.

## Later

HT1. AirGPT `rag/`. Do not mint Cortex #42. Do not clone Grok Bot reconstructed.
