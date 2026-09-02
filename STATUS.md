# STATUS - Netie constitution repo

**Branch:** `cursor/kb-list-briefs-ca9b` · **PR:** (this) · **main:** `7a6860c` (docs-ci pending)
**Local gate:** `make ci`.

## Now

- KB `list_briefs` is the catalog (strips skill bodies). `lookup` still refuses a skill row that carries a body. GET `/index?kind=skill` and `kb_list(kind=skill)` return JSON briefs. Crew `register_index(list_briefs(rows))` is the dump path. Wrap stays **3/10**.
- Cortex `guard_observe` on observe tools. Pointer native observe stays DR-0005. Scores stay **4/10** Q&A, **2/10** governed computer-use.
- Founder apply-all: `python3 scripts/apply_product_patches.py --dry-run`. Product remotes clone-yes push-403. 404: AirGPT, Space, Cortex-Crew. Keys.txt gone; founder must revoke. C2/MIN_TESTS stand.

## Next (founder clicks)

1. Revoke leaked keys. 2. Contents write on product remotes + add those URLs to env e/eb1a4238-9fe4-11f1-b532-320a589b8025, then boot a new agent. 3. Create Cortex-Crew. 4. Run `apply_product_patches.py` on a write machine.

## Later

HT1. AirGPT `rag/`. Do not mint Cortex #42. Do not clone Grok Bot reconstructed.
