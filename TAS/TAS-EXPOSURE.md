# TAS-EXPOSURE - Exposure pack technical architecture

**Plane:** 4 pack on plane 3 (Cortex-crew), not a new engine
**Path:** `exposure/` in `Netie-AI/Netie`
**Measured:** 2026-08-25. Claims below are about this pack, not Cortex internals.

---

## 1. What it is

A stdlib Python CLI plus a Cortex-crew YAML that:

1. Reads the public Netie.AI catalog (GitHub org + hire catalog + frozen facts)
2. Drafts channel posts (LinkedIn, Reddit, GitHub)
3. Tracks organic growth toward 100k LinkedIn followers
4. Refuses fake audience, scraping, and overclaim

**It is not:** a model server, a key vault, a second orchestrator, or a follower factory.

---

## 2. Entry points

| Path | Role |
|---|---|
| `exposure/src/netie_exposure/cli.py` | `python -m netie_exposure` |
| `exposure/crew.yaml` | Cortex-crew contract (Vanguard / Cortex / Closer + channel agents) |
| `exposure/github-profile/README.md` | paste into `Netie-AI/.github` profile README |
| `Software Blueprint/Exposure/PRD-002-organic-public-exposure.md` | product spec |
| `Internal/Agents/EXPOSURE.md` | agent prompts |

---

## 3. Layers

```
facts.json + GitHub API + hire/catalog.json
        |
        v
   catalog.py     (merge, no invented products)
        |
        v
   claims.py      (strip denylisted claims)
        |
        v
   drafts.py      (hooks / product / news / hire / invite / github)
        |
        v
   crew.py        (route to channel agent; posting OFF)
        |
        +-- channels/linkedin.py   draft; official API only if approved
        +-- channels/reddit.py     draft; official API only if approved
        +-- channels/github.py     profile README, release notes, star-ask copy
        |
        v
   growth.py      snapshots toward 100k (measure, do not manufacture)
```

Constructor mapping (do not invent a host): connector -> ontology -> insight -> foundry -> app
is catalog -> claims -> drafts -> crew -> channel outbox.

---

## 4. Trust boundaries

| Boundary | Enforced by |
|---|---|
| No fake followers / bought stars / scrape | `refuse.py` + `tests/test_refuse.py` |
| No post without approve | `cli.py` publish path; default `social_posting: off` in `crew.yaml` |
| No invented prices or customers | `claims.py` + `facts.json` hire offers only |
| Cortex is the only engine | `crew.yaml` `engine: cortex`; pack has no agent loop |
| Laptop-ASCII in drafts | `drafts.py` sanitizer + test |

---

## 5. Channel rules

**LinkedIn.** Drafts only. North star 100_000 followers. No follow, unfollow, invite-spam,
or unofficial clients. If `LINKEDIN_ACCESS_TOKEN` is set *and* `--approve <id>` was
passed, the stub may call LinkedIn's official UGC API. Otherwise write markdown.

**Reddit.** Drafts for allowlisted subs with self-promo rules in the draft footer.
Official Reddit API only after approve. No vote brigades.

**GitHub.** Earn stars: honest README, topics, release notes, Show-HN copy. No star
exchanges, no fake traffic. Org profile README is a first-class artifact.

---

## 6. What this pack will never do

Listed in `refuse.py` `REFUSALS`. Adding a new "growth tactic" that is not a public
post or a public repo improvement is a PRD amendment, not a ticket.
