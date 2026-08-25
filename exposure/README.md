# Exposure - public Cortex-crew marketing pack

Apache-2.0. Clone it, star it, swap `facts.json` for your own org.

**This is not a follower bot.** The north star is 100,000 LinkedIn followers,
earned with public posts a human approves. GitHub stars are earned the same way.
Reddit is discussion with affiliation disclosed. Cortex is the only engine.

```
Vanguard watches  ->  Cortex picks the mix  ->  Closer writes the outbox
        |                      |                        |
   GitHub org            claims denylist          you run approve
   hire catalog          no Suite-film proof      posting stays OFF
   AI news seeds
```

Constructor mapping: connector -> ontology -> insight -> foundry -> app
is catalog -> claims -> drafts -> crew -> channel outbox.

## Quick start

```bash
cd exposure
pip install -e ".[dev]"
python -m netie_exposure catalog --offline
python -m netie_exposure run --offline
python -m netie_exposure growth --followers 0
pytest
```

`run` is the crew: Vanguard -> Cortex -> LinkedIn/Reddit/GitHub/news/hire/invite
-> Closer -> marketing kit. `queue` is the mix only. Nothing is posted.

Agent prompts: `AGENTS.md` (this folder). Cortex-crew contract: `crew.yaml`.

## What it reads

| Source | Why |
|--------|-----|
| `src/netie_exposure/data/facts.json` | frozen products, hire SKUs, cool parts |
| `https://api.github.com/orgs/Netie-AI` | live stars + descriptions (optional) |
| `https://netie.ai/hire/catalog.json` | live hire offers (optional) |
| `crew.yaml` | Cortex-crew contract |

Org profile (paste into GitHub org settings / `.github` README):
`github-profile/README.md` and `github-profile/SETTINGS.md`.

## Agents

Prompts: `AGENTS.md` (standalone; this pack does not need the private Netie repo)

| Role | Does | Publishes? |
|------|------|------------|
| vanguard | catalog + growth | no |
| cortex | day's mix | no |
| closer | outbox markdown | no |
| linkedin | hook <=210, body <=1300 | no |
| reddit | allowlisted sub + affiliation | no |
| github | org PROFILE.md + Show HN | no |
| news | HN or seeds, cited URL | no |
| hire | catalog.json prices only | no |
| invite | waitlist + constructor + suite | no |
| marketing | combines channels after the crew | no |

Scale: fan out **channel specialists only**, on Cursor Grok 4.5 high / Composer 2.5
or Claude Code Sonnet. Never a second orchestrator.

## Refusals (load-bearing)

```bash
python -m netie_exposure refuse "generate followers until 100k"
python -m netie_exposure refuse "buy github stars"
python -m netie_exposure refuse "scrape linkedin"
```

Each prints a named code. The pack will not write an outbox file for those tactics.

## Approve

```bash
python -m netie_exposure approve 2026-08-25-hook-........
```

Still a dry-run. Wire LinkedIn/Reddit **official** APIs later. No unofficial clients.

## Extract to a public repo

This folder is the public-shaped source. Copy it out:

```bash
git subtree split -P exposure -b exposure-public
```

Then create public `Netie-AI/exposure` from that branch. Tests and `AGENTS.md`
travel with it. Until that repo exists, stars cannot land on this private parent.

