---
name: scroll-craft-landing
description: Build a premium scroll-driven landing page for a Netie buyer using nateherkai/scroll-craft. Use when the owner or a paying buyer wants a real landing page, scrollytelling, Apple-style scroll, or a site that should not look like a template. Do not use for Coming Soon fill-in HTML.
---

# Scroll-craft landing (Netie)

Upstream: https://github.com/nateherkai/scroll-craft (MIT, Nate Herk). Plugin skill lives at `plugins/nateherk-design/skills/scrollcraft/SKILL.md` in that repo.

This file is the Netie load point. When this skill matches, clone or refresh the repo if it is not already on disk, then follow the upstream SKILL.md. Local copy of the upstream procedure: `upstream-SKILL.md` in this folder.

## When to load

- Paid landing page after RM 500 first-draft unlock, or after the owner approved a build.
- Buyer asked for a better site, not a one-block Coming Soon rewrite.
- Owner said use scroll-craft.

## Netie constraints

1. Interview the owner or the buyer before generating. Do not invent a vibe from the company name.
2. Use their published facts, photos, and copy. Do not invent testimonials, SSM, streets, or stats.
3. Show the owner the page before anyone else sees it. Cite `.cursor/skills/show-before-send/SKILL.md`.
4. Do not edit the scroll-craft engine per project. Theme tokens and semantic HTML only.
5. Prefer the buyer's own photos over generated video unless they asked to spend on generated clips.
6. Pair craft with `.cursor/skills/mengto-frontend/SKILL.md` for layout, type, and conversion structure.

## First run

```bash
git clone --depth 1 https://github.com/nateherkai/scroll-craft.git
# then read plugins/nateherk-design/skills/scrollcraft/SKILL.md
```

Install as a Claude/Cursor plugin only if the owner asked: `/plugin marketplace add nateherkai/scroll-craft`

## Honest limit

scroll-craft is opinionated. A Malaysian factory landing can stay quieter than Orrery or PERKFORM. Pick the grammar from the interview, not from the demo reel.
