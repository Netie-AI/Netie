# STATUS - Netie constitution repo

**Branch:** `cursor/pin-sibling-shas-ca9b` · **PR:** https://github.com/Netie-AI/Netie/pull/57 · **main:** `f712d22` (hustle proof follow-up)

**Local gate:** `make ci` (same as GitHub `docs-ci`). `make drift` is network, not ci.

## Now

- GitHub `docs-ci` on `main` was green through `8eb2d18`. `a8e895b` through `f712d22` failed ~28s (real): sibling clones hit live HEAD that drifted past the patches. Tests and `apply_product_patches.py` pin measured SHAs: constructor `4896ddd`, OpenVault `62bb1c7`, Cortex `bf4ecee`, dms `3f9a9be`, Pointer `8c0e6c2`, control `82ab1ae`, KB `10356e5`. Live HEAD 2026-10-30: constructor `bfc7d3b`, OpenVault `3ba51cd`, Cortex `2deb09c`, dms `1411323`, Pointer `b42b98d`, control `93959c6` (KB still `10356e5`). Push 403. Do not claim those patches apply on live HEAD.
- DR-0002 is on main (**proposed**): `ecosystem/catalog.json` 21 upstreams, 13 stage 1 overlays. Overlay replay byte-identical on 3 upstreams. Nothing sellable yet. n8n / Dify / Open WebUI / NadirClaw / Routerly not forkable. OpenWork `ee/` stripped.
- `README.md` / `AGENTS.md` / `CLAUDE.md` bind agents to `NETIE.md`. Crew wrap stays **3/10**. HT1 not done. Score stays **2/10**. C2/MIN_TESTS stand.

## Next (founder clicks)

1. Revoke leaked keys. 2. Contents write on product remotes + env URLs, then boot a new agent. 3. Create Cortex-Crew. 4. Private Netie-AI repos for first forks (freeide, freeroute, airgpt) and grant write. 5. Unresolved names in `ecosystem/ECOSYSTEM.md`.

## Later

Stage 2 per fork. Nightly `make drift`. Counsel on vendor terms. HT1. AirGPT `rag/`. Do not mint Cortex #42. Do not clone Grok Bot reconstructed.
