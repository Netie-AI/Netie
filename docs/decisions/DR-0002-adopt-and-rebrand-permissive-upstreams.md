---
status: proposed
date: 2026-10-05
decision-makers: founder
---

# DR-0002 - Adopt and rebrand permissive upstreams

## Context and Problem Statement

The estate has depended on, ported from, or reimplemented open-source work, and the license
law in `TAS/ESTATE-GAP.md` read: "we do not vendor a tree, strip the license, or slap a
Netie logo on someone else's product." That is slow. Five weeks in (docs dated 2026-08-01 to
2026-09-02), `TAS/ESTATE-GAP.md` scores most products 0 to 4 out of 10 (best: Space, 6 as a
preview app), and `docs/patches/` holds 70 patches that the product repos cannot receive yet
because push is 403.

On 2026-10-05 the founder directed: take the open-source projects, rebrand them, and build
the Netie concept on top, instead of distilling.

Measured the same day, from each upstream's LICENSE file at HEAD, across the 21 named
projects: 15 are plainly MIT or Apache-2.0 and permit a rebrand if license and notices are
kept. One (OpenWork) is MIT with an enterprise-licensed `ee/` directory. Five are not
forkable for sale: n8n (Sustainable Use License, internal or non-commercial use only), Dify
(no multi-tenant operation, frontend logo locked), Open WebUI (branding clause above 50
users), NadirClaw (PolyForm Noncommercial) and Routerly (AGPL-3.0). See
`ecosystem/ECOSYSTEM.md`. So the question is which to fork and how, not whether.

## Considered Options

1. Keep distilling (status quo).
2. Fork and rebrand everything the founder named, as asked.
3. Fork and rebrand only permissive upstreams with license and notices intact, depend on
   libraries, host or block the rest, and put the Netie gate on top.

## Decision Outcome

Option 3. Option 2 would ship products whose licenses forbid sale, which makes the estate
unsellable and invites a takedown.

Rules:

1. **Class gates the mode.** `scripts/ecosystem.py` maps license class to the modes it may
   take. Forking needs `permissive` (or `permissive-carveout` with the carve-out stripped).
   Copyleft, source-available, branding-locked and noncommercial rows can only be hosted
   unmodified or blocked.
2. **LICENSE, NOTICE and every upstream copyright line are never edited.** The tool
   re-hashes the license file after a rebrand. A fork carries `NETIE-ATTRIBUTION.md` and a
   non-endorsement line.
3. **Overlays, not trees.** A fork is an upstream commit plus an ordered patch series in
   `ecosystem/overlays/<slug>/`. No upstream tree enters this repo. Replay is
   `ecosystem.py clone` then `ecosystem.py apply`.
4. **Libraries are depended on.** deepagents, haystack, mem0 gain nothing from a fork and
   cost a permanent rebase.
5. **Stages are claims.** 0 catalogued, 1 overlay patch exists, 2 gate wired and tested,
   3 shippable. Stage 1 is documentation, attribution and strips only. It does not rename
   packages, binaries or identifiers, because that needs a build to prove.
6. **A fork never grows its own vault or orchestrator.** Provider keys come from OpenVault
   and tool execution goes through Cortex, or the fork is not shipped. Providers that reuse
   an end user's Claude Code, Codex, Copilot or Cursor login are disabled in any fork.
7. **Amends** `NETIE.md` section 6 (new adoption lane) and the license law in
   `TAS/ESTATE-GAP.md`. Unchanged: the safe path (section 4), no second Cortex, no second
   key vault, no inference server, and Grok Bot reconstructed stays refused.

## Consequences

Positive: a Netie-branded app per surface can exist in days instead of quarters, license
risk is checked by a gate that can fail, and upstream license changes are caught by the
`drift` command before a release.

Negative: every fork carries a rebase and CVE-watch tax. Naming a dozen forks risks the
"zoo" this estate was warned about, so each is mapped to an existing product in the catalog.
Vendor terms of service for subscription-login providers and counsel review of all of this
are not done. A stage 1 fork still says upstream's name in its package, binary and UI.

## Confirmation

`scripts/test_ecosystem.py` (exists, run by `make ci`). It proves the gate refuses
noncommercial, copyleft, branding-locked and library forks, that a rebrand leaves LICENSE and
NOTICE byte-identical, that license drift refuses, and that `ecosystem/ECOSYSTEM.md` is
regenerated from `ecosystem/catalog.json`. The network check is
`python3 scripts/ecosystem.py drift`.
