# STATUS - Netie constitution repo

**Branch:** `cursor/space-leave-skill-ids-ca9b` · **PR:** (this) · **main:** `d2ea2b4` (docs-ci in flight)
**Local gate:** `make ci`.

## Now

- Space `chat_preview(ov=)` / `ocr_cloud(ov=)` POST `/api/crew/gate` with skill ids. Boolean `ov_allowed` stays the stand-in. Governed stays **2/10**.
- Crew leave `execute_capability(ov=)` does the same. Session lists skill ids. Wrap stays **3/10**.
- Founder apply-all: `python3 scripts/apply_product_patches.py --dry-run`. Product remotes clone-yes push-403. 404: AirGPT, Space, Cortex-Crew. Keys.txt gone; founder must revoke. C2/MIN_TESTS stand.

## Next (founder clicks)

1. Revoke leaked keys. 2. Contents write on product remotes + add those URLs to env e/eb1a4238-9fe4-11f1-b532-320a589b8025, then boot a new agent. 3. Create Cortex-Crew. 4. Run `apply_product_patches.py` on a write machine.

## Later

HT1. AirGPT `rag/`. Do not mint Cortex #42. Do not clone Grok Bot reconstructed.
