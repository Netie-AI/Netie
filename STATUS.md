# STATUS - Netie constitution repo

**Branch:** `cursor/agents-readme-law-16cc` | **main:** `8eb2d18` (docs-ci green on that tip, measured 2026-09-02)

**Local gate:** `make ci` (same command as GitHub `docs-ci`).

## Now

- `README.md`, `AGENTS.md`, and `CLAUDE.md` bind agents to `NETIE.md`: depend, port with notices, or reimplement. No vendored upstream trees.
- GitHub `docs-ci` on `main` is green (measured 2026-09-02, 2 checks). Older 1-5s red X jobs were billing, not a code ticket.
- Crew wrap leave-machine POSTs are on main. Wrap stays **3/10**. HT1 not done. Score stays **2/10**.
- Founder apply-all: `python3 scripts/apply_product_patches.py --dry-run`. Product remotes clone-yes push-403. 404: AirGPT, Space, Cortex-Crew. Keys.txt gone; founder must revoke. C2/MIN_TESTS stand.
- Measured 2026-09-26: `test_sibling_patches.py` fails `git apply` on fresh public clones (constructor `test.yml` already present; Cortex, dms, OpenVault, Pointer, Control hunks rejected). Pre-existing. Do not claim those patches still apply.

## Next (founder clicks)

1. Revoke leaked keys. 2. Contents write on product remotes + add those URLs to env e/eb1a4238-9fe4-11f1-b532-320a589b8025, then boot a new agent. 3. Create Cortex-Crew. 4. Run `apply_product_patches.py` on a write machine.

## Later

HT1. AirGPT `rag/`. Do not mint Cortex #42. Do not clone Grok Bot reconstructed.
