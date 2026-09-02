# STATUS - Netie constitution repo

**Branch:** `cursor/switchyard-leave-skill-ids-ca9b` · **PR:** (this) · **main:** `2cb4606` (docs-ci in flight)
**Local gate:** `make ci`.

## Now

- `host_switchyard(ov=)` POSTs `/api/crew/gate` with skill ids. Boolean `ov_leave` stays the stand-in. Score stays **2/10**.
- Pointer / Space / Crew leave do the same. Session lists skill ids. Wrap stays **3/10**.
- Founder apply-all: `python3 scripts/apply_product_patches.py --dry-run`. Product remotes clone-yes push-403. 404: AirGPT, Space, Cortex-Crew. Keys.txt gone; founder must revoke. C2/MIN_TESTS stand.

## Next (founder clicks)

1. Revoke leaked keys. 2. Contents write on product remotes + add those URLs to env e/eb1a4238-9fe4-11f1-b532-320a589b8025, then boot a new agent. 3. Create Cortex-Crew. 4. Run `apply_product_patches.py` on a write machine.

## Later

HT1. AirGPT `rag/`. Do not mint Cortex #42. Do not clone Grok Bot reconstructed.
