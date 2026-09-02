# STATUS - Netie constitution repo

**Branch:** `cursor/crew-gate-skill-ids-ca9b` · **PR:** (this) · **main:** `b42db8d` (docs-ci pending)
**Local gate:** `make ci`.

## Now

- OpenVault `/api/crew/gate` `kind=skill` is ok only when the POST carries ids-only `skill_ids`. Crew `allow` sends those ids from the registry. Bodies still refuse. Wrap stays **3/10**.
- Control `board_index` stitches graph + Factory + skills. Persist keeps skill ids. KB `list_briefs` + `register_index` stay the dump path.
- Founder apply-all: `python3 scripts/apply_product_patches.py --dry-run`. Product remotes clone-yes push-403. 404: AirGPT, Space, Cortex-Crew. Keys.txt gone; founder must revoke. C2/MIN_TESTS stand.

## Next (founder clicks)

1. Revoke leaked keys. 2. Contents write on product remotes + add those URLs to env e/eb1a4238-9fe4-11f1-b532-320a589b8025, then boot a new agent. 3. Create Cortex-Crew. 4. Run `apply_product_patches.py` on a write machine.

## Later

HT1. AirGPT `rag/`. Do not mint Cortex #42. Do not clone Grok Bot reconstructed.
