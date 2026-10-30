# STATUS - Netie constitution repo

**Branch:** `claude/netie-ecosystem-rebrand-uq9q3z` (from `8eb2d18`). **Gate:** `make ci`.

## Now

- Adoption lane built (DR-0002, **proposed**, not accepted): `ecosystem/catalog.json` holds 21 upstreams with licenses read from each LICENSE file on 2026-10-05, a license-class gate, a rebrand tool, and 13 stage 1 overlays. Overlay replay was byte-identical on 3 real upstreams (freeide, crew-desk, freeroute-core).
- **Nothing is sellable yet.** Stage 1 is docs, attribution and strips. No fork is renamed, gated or built. Product remotes are still clone-yes push-403.
- Not forkable for sale: n8n, Dify, Open WebUI, NadirClaw, Routerly. OpenWork `ee/` is stripped. OmniRoute and 9router must lose subscription-login providers before release.
- docs-ci on `main` is green (2026-09-02). Crew wrap stays 3/10, HT1 not done, score stays 2/10.
- `README.md`, `AGENTS.md`, and `CLAUDE.md` bind agents to `NETIE.md`: depend, port with notices, or reimplement. No vendored upstream trees.
- Founder apply-all: `python3 scripts/apply_product_patches.py --dry-run`. Product remotes clone-yes push-403. 404: AirGPT, Space, Cortex-Crew. Keys.txt gone; founder must revoke. C2/MIN_TESTS stand.
- Measured 2026-09-26: `test_sibling_patches.py` fails `git apply` on fresh public clones (constructor `test.yml` already present; Cortex, dms, OpenVault, Pointer, Control hunks rejected). Pre-existing. Do not claim those patches still apply.

## Next (founder clicks)

1. Merge or reject the DR-0002 PR. Merge also amends `NETIE.md` section 6.
2. Create private `Netie-AI` repos for the first forks (suggest freeide, freeroute, airgpt) and grant this agent write.
3. Revoke the leaked keys. Contents write on product remotes. Create Cortex-Crew.
4. Answer the two unresolved names in `ecosystem/ECOSYSTEM.md` (openwillow/zillow, Andrew Ng openwork).

## Later

Stage 2 per fork (gate wiring, package renames, a build that passes). Nightly `make drift` routine once this is on `main`. Counsel review of vendor terms for subscription-login providers. HT1. AirGPT `rag/`. Do not mint Cortex #42. Do not clone Grok Bot reconstructed.
