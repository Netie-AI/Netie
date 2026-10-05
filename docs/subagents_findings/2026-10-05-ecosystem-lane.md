# 2026-10-05 - ecosystem lane (DR-0002)

Preflight: KB `D:\Netie-KB` absent in this cloud box and `docs/subagents_findings/INDEX.md`
did not exist. PREFLIGHT: MISS, so this was first-principles research. No subagents were
spawned for this part; everything below was read or run directly.

## F1. "Open source" was assumed to mean "rebrandable and sellable"

- **Expected:** all 21 named projects could be cloned, rebranded and sold.
- **Actual** (read from each LICENSE at HEAD): 15 MIT or Apache-2.0, 1 MIT with an
  enterprise-licensed `ee/` (OpenWork), 5 not forkable for sale: n8n (Sustainable Use
  License), Dify (no multi-tenant, logo locked), Open WebUI (branding clause above 50
  users), NadirClaw (PolyForm Noncommercial), Routerly (AGPL-3.0).
- **Repro:** `python3 scripts/ecosystem.py drift` re-hashes every license file.
- **Root-cause class:** a category word ("open source") standing in for a license check.
- **Invariants:** separate verified fact from assumption; a control that blocks legitimate
  work is a failure (so the gate is per license class, not a blanket "no forks").
- **Not verified:** vendor terms of service for the subscription-login providers in
  OmniRoute and 9router, and counsel review of everything here.

## F2. Sibling patch gate is red on the base commit

- **Expected:** `make ci` green, as `STATUS.md` claimed on 2026-09-02.
- **Actual:** `scripts/test_sibling_patches.py` fails 8 of 10 on an untouched worktree of
  `8eb2d18` today. Example: `pointer-netie-hands.patch: package.json:7 patch does not apply`.
- **Repro:** `cd scripts && python3 test_sibling_patches.py`, or the same inside
  `git worktree add <dir> 8eb2d18`.
- **Root-cause class:** a gate asserted against the moving HEAD of an external repo, so it
  decays whenever the sibling moves and a "green" reading has a shelf life.
- **Invariants:** a skipped test is a failing test (so it was not skipped); fix the
  root-cause class (pin each sibling to the SHA its patches were measured on, rebase the
  patches that no longer apply) rather than the one failing patch.
- **Status:** not fixed here, out of scope. Fix is pin plus rebase, estimate 60 to 90 minutes.

## F3. Four tool bugs that synthetic fixtures could not see

Three found by running the rebrand tool on real clones, one by code review. Each fixed and covered by a test:

| Bug | Seen on | Test added |
|---|---|---|
| Banner read "Netie Netie Wiki" | netie-wiki | `test_banner_does_not_double_the_netie_prefix` |
| Rewriting a CRLF file would flip every line ending | code review only, no real tree showed it | `test_rebrand_preserves_crlf` |
| 100 MB patch: about 8,800 translated docs rewritten | OmniRoute | `test_translations_notices_and_changelogs_are_left_alone`, `test_too_many_docs_refuses` |
| Catalog commit pin stale: 5 upstreams moved between probe and overlay | five rows | `pin_catalog`, and `validate` compares overlay base to the pin |

- **Root-cause class:** fixtures sized for the happy path miss scale and drift.
- **Invariant:** assert the artifact the customer actually receives (the real tree).
- **Gate proved able to fail:** mutating the license-class table made 2 tests fail.
