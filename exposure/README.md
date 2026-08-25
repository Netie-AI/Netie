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
python -m netie_exposure queue --offline
python -m netie_exposure crew
python -m netie_exposure growth --followers 0
pytest
```

`queue` writes paste-ready markdown under `outbox/`. Nothing is posted.

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

Prompts: `../Internal/Agents/EXPOSURE.md`

| Role | Does | Publishes? |
|------|------|------------|
| vanguard | catalog + growth | no |
| cortex | day's mix | no |
| closer | outbox markdown | no |
| linkedin / reddit / github | channel copy | no |
| news | Cassandra-shaped, cited | no |
| hire | catalog.json prices only | no |
| invite | waitlist + constructor + suite | no |

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

Unlock: founder yes, this README standing alone, tests green on CI.
Suggested name: `Netie-AI/exposure`. Until then this folder is the public-shaped
source inside `Netie-AI/Netie`.
