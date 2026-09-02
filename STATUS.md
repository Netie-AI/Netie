# STATUS - Netie constitution repo

**Branch:** `cursor/persist-ov-registry-ca9b` · **PR:** (this) · **main:** `e6a2910` (docs-ci green)
**Local gate:** `make ci`.

## Now

- `persist` / `resume` default to `graph.ov.registry`. Callers do not pass the registry a third time. Bodies still refuse. Wrap stays **3/10**.
- OpenVault gate POST carries `skill_ids`. Control `board_index` stitches graph + Factory + skills. KB `list_briefs` + `register_index` stay the dump path.
- Founder apply-all: `python3 scripts/apply_product_patches.py --dry-run`. Product remotes clone-yes push-403. 404: AirGPT, Space, Cortex-Crew. Keys.txt gone; founder must revoke. C2/MIN_TESTS stand.

## Next (founder clicks)

1. Revoke leaked keys. 2. Contents write on product remotes + add those URLs to env e/eb1a4238-9fe4-11f1-b532-320a589b8025, then boot a new agent. 3. Create Cortex-Crew. 4. Run `apply_product_patches.py` on a write machine.

## Later

HT1. AirGPT `rag/`. Do not mint Cortex #42. Do not clone Grok Bot reconstructed.
