# CLAUDE.md - Netie constitution repo

Law for this repo only. `NETIE.md` wins over everything here. Gate: `make ci`.

## Hard rules

Each names its enforcer. "None" means it is a wish, not a control.

1. **Laptop-ASCII in docs.** No em dash, en dash or curly quote. Enforcer: `scripts/check_docs.py`.
2. **No provider key in git.** Enforcer: `scripts/secrets_scan.py` via `scripts/test_secrets_scan.py`.
3. **Generated files are regenerated, never edited.** `ecosystem/ECOSYSTEM.md` comes from
   `ecosystem/catalog.json` via `python3 scripts/ecosystem.py render`. Enforcer:
   `test_table_is_current` in `scripts/test_ecosystem.py`.
4. **Fork and rebrand only a permissive upstream.** n8n, Dify, Open WebUI, NadirClaw and
   Routerly are not forkable. Enforcer: license-class gate in `scripts/ecosystem.py`,
   proved able to fail in `scripts/test_ecosystem.py`.
5. **Never edit an upstream LICENSE, NOTICE or copyright line.** Enforcer: the tool re-hashes
   the license file after a rebrand and refuses on drift. Same test file.
6. **No upstream tree in this repo, only patch series** in `ecosystem/overlays/<slug>/`.
   Enforcer: 2 MB file cap in `test_no_secrets_or_trees_in_ecosystem_dir`. Weak: it cannot
   see a tree split into small files.
7. **A stage number is a claim.** Stage 1 needs an overlay whose base matches the catalog
   pin (enforced). Stage 2 and 3 have no enforcer yet: do not raise them without a test.
8. **`STATUS.md` stays at 60 lines or fewer.** Enforcer: `scripts/check_docs.py`.
9. **Never push to a product repo from here, never commit `Keys.txt`.** Enforcer: none for
   push (token is 403 on products); `.gitignore` for keys.
10. **Say what is measured and what is assumed.** Enforcer: none. Review it.

## Commands

```
make ci                                    # compile + docs gate + every scripts/test_*.py
python3 scripts/ecosystem.py validate      # catalog gate
python3 scripts/ecosystem.py render        # rewrite ecosystem/ECOSYSTEM.md
python3 scripts/ecosystem.py drift         # network: re-hash every upstream license
python3 scripts/ecosystem.py clone SLUG DIR && python3 scripts/ecosystem.py apply SLUG DIR
python3 scripts/ecosystem.py rebrand SLUG DIR --overlay   # cut stage 1 from a pristine clone
```

## Map

`NETIE.md` what we are. `README.md` front door. `STATUS.md` state. `TAS/ESTATE-GAP.md`
distance to analogues. `ecosystem/` catalog, generated table, overlays. `docs/decisions/`
DRs. `docs/patches/` sibling-repo patches. `scripts/` portable contracts and gates.
