# STATUS - Netie constitution repo

**Branch:** `cursor/crew-leave-skill-ids-ca9b` · **PR:** (this) · **main:** `94a17b9` (docs-ci in flight)
**Local gate:** `make ci`.

## Now

- `execute_capability(ov=)` POSTs `/api/crew/gate` with skill ids. Boolean `ov_allowed` stays the stand-in. Bodies still refuse. Wrap stays **3/10**.
- Session lists skill ids. Ticket-runner `board_from_runs` goes through `board_index`. `summarise` counts skill ids.
- Founder apply-all: `python3 scripts/apply_product_patches.py --dry-run`. Product remotes clone-yes push-403. 404: AirGPT, Space, Cortex-Crew. Keys.txt gone; founder must revoke. C2/MIN_TESTS stand.

## Next (founder clicks)

1. Revoke leaked keys. 2. Contents write on product remotes + add those URLs to env e/eb1a4238-9fe4-11f1-b532-320a589b8025, then boot a new agent. 3. Create Cortex-Crew. 4. Run `apply_product_patches.py` on a write machine.

## Later

HT1. AirGPT `rag/`. Do not mint Cortex #42. Do not clone Grok Bot reconstructed.
