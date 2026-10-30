# PRD-002 - Organic public exposure (LinkedIn, Reddit, GitHub)

**Product:** Exposure (Cortex-crew marketing pack)
**Owner:** founder + marketing specialist
**Status:** draft - first slice shipped as public OSS pack in this repo
**Repos in scope:** `Netie-AI/Netie` (pack lives at `exposure/`); Cortex consumes `exposure/crew.yaml`
**Created:** 2026-08-25

---

## 1. Press release

### One public crew. Real posts. No fake followers.

**Netie Exposure is the open-source Cortex crew that turns the GitHub org, the product
site, Hire, and AI news into channel-ready drafts - LinkedIn, Reddit, and GitHub - and
refuses anything that manufactures audience.**

The org already has the raw material: [github.com/Netie-AI](https://github.com/Netie-AI)
(profile: "Building the foundational infrastructure for the next era of digital and
physical interaction."), [netie.ai](https://netie.ai/) (AirGPT, Space, Cortex, Suite),
[netie.ai/hire](https://netie.ai/hire/) (Penang scoped work), Cassandra (AI news
sentiment), OpenHBM (23 stars), Constructor, OpenVault. What it does not have is a
repeatable, honest distribution loop.

Exposure is not a second orchestrator. Cortex is the engine. Vanguard watches the
catalog and the numbers. Cortex picks the day's mix. Closer proposes the post. A human
approves. Social posting stays **off** until that gate fires - the same switch already
drawn on the Suite admin film.

The north star is **100,000 LinkedIn followers, earned**. The pack tracks the number. It
does not buy it, scrape it, or simulate it.

> "I can paste a week's posts from one command, each line traces to a public URL, and
> nothing ships until I say yes." - *founder, first week of use*

Apache-2.0. Clone it, star it, run it on your own org by swapping `facts.json`.

---

## 2. FAQ

### External

**Is this a LinkedIn growth hack / follower bot?**
No. It drafts posts and tracks an organic goal. It refuses fake accounts, purchased
followers, follow/unfollow bots, engagement pods, and scraping. LinkedIn publish, if
ever wired, goes through LinkedIn's official API after a human approve flag.

**Will this get me 100k followers this month?**
No, and claiming that would be the WASM-in-the-README class of lie. 100k is a target
the dashboard holds. Cadence is one approved post per channel per day unless you raise
it. The honest path is years of public work, not a week of automation.

**What is the source of truth for "our products"?**
The GitHub org profile and public repos, plus `netie.ai` / `netie.ai/hire/catalog.json`,
plus the frozen facts file in the pack. Live fetch overlays stars and descriptions. If
a claim is not in those sources, it does not go in a post.

**Can I post customer wins?**
Only with a source URL that is not a Suite demo film. "TechCorp $45k" on the Suite page
is a film, not a named-client case study. The pack strips that class of claim.

**How does this combine with Cortex-crew?**
`exposure/crew.yaml` is the crew contract: Vanguard / Cortex / Closer plus channel
specialists (linkedin, reddit, github, news, hire, invite). Constructor's default graph
is connector -> ontology -> insight -> foundry -> app. Exposure is that graph for
distribution. Cortex remains the only engine.

### Internal - the questions we cannot answer yet

**Q: Do we have a LinkedIn company page with API access?**
Unknown. The pack ships draft-only. Official publish is a stub behind `--approve` plus
token. Until a token exists, the customer artifact is the markdown outbox.

**Q: Is Cortex in this GitHub org?**
Not as a public repo on 2026-08-25. The website and NETIE.md name it. Posts may name
Cortex as the crew engine and link `https://netie.ai/` and Constructor. They must not
link a GitHub repo that does not exist.

**Q: Should Exposure become its own public repo for stars?**
Yes, later. This slice lives in `Netie-AI/Netie` so the estate can review it. Extract
to `Netie-AI/exposure` when the README can stand alone (unlock: founder yes + Apache
header + passing tests on a green CI job).

---

## 3. Success assertion (customer seat)

WHEN a stranger clones `exposure/` and runs `python -m netie_exposure queue --offline`
THE SYSTEM SHALL print a dated mix of drafts (hooks, products, AI news, hire, invite,
GitHub cool parts), each draft carrying at least one public source URL, and SHALL refuse
to emit a publish payload unless `--approve <id>` was passed.

WHEN asked to generate fake followers, buy GitHub stars, or scrape LinkedIn
THE SYSTEM SHALL refuse with a named refusal code and write nothing to the outbox.

---

## 4. Out of scope

- Fake or purchased followers, likes, stars, or comments
- LinkedIn/Reddit scraping, unofficial clients, or follow/unfollow automation
- A new orchestrator (no n8n clone, no second Cortex)
- Invented prices, invented customers, or Suite-film metrics as proof
- Auto-trading or Cassandra as a trade signal (Cassandra stays a research report)
- Changing NETIE.md product boundaries
- Posting to channels without a human approve gate

---

## 5. Slice (irreversibility)

1. **FOUNDATION** - catalog + claims denylist + crew contract (`facts.json`, refusals)
2. **BOUNDARY** - publish off by default; named refusals; claim stripper
3. **CAPABILITY** - draft queue from live/offline catalog
4. **SURFACE** - CLI (`catalog`, `draft`, `queue`, `growth`, `approve`)
5. **DEMO** - first week of real posts in `exposure/outbox/seed/`

---

## Feedback ledger

| # | Date | Raised in | Feedback | Routed to | Outcome |
|---|------|-----------|----------|-----------|---------|
| F1 | 2026-08-25 | cloud agent | Exposure Agent: LinkedIn to 100k, hooks, products, AI news, hire, invite, GitHub org profile, public OSS, Reddit + LinkedIn + GitHub agents, scale with Cortex-crew then marketing agents | this PRD | pack in `exposure/` |
