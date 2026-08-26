---
name: consulting-proposal
description: When a buyer replies, write a clear proposal document with figures, not only an email. SCR storyline, action titles, fee table, live proof. Show the owner before send.
---

# Consulting proposal (client reply)

Owner 26 Aug 2026: a client reply is not answered by another short email only. Write a proposal they can open like Word or slides. Research Goldman / Accenture / McKinsey shape. Be precise about the service.

Gemini account and Playwright MCP are optional later. This VPS has no Gemini MCP and no Playwright MCP. Ship a self-contained HTML pitch plus a markdown memo. Do not wait on a login. Do not store Gemini passwords in the repo.

## When to write one

A buyer asked what you are selling, asked for a price, or replied that they do not understand. Toon at Advanced Inkjet is the live case (`thread 1a03642393b091d6`).

Do not send until the owner says send. Cite `.cursor/skills/show-before-send/SKILL.md`. Do not `update_draft` a reply holding pen.

## Storyline (SCR)

Keep Situation and Complication short. Weight the document toward Resolution.

1. Situation: one published fact from their live site.
2. Complication: a visitor cannot tell the offer or cannot convert.
3. Resolution: we build a better landing page and the marketing around it first. Then agents, OCR, and a system-level database. We already ship this class of IT.

Action title on every slide or section: a full sentence that is the point. One point per slide. Source line under every figure.

## Shape (keep it short)

Cover. One-page executive summary that stands alone. Body. Fees and workplan. Live proof. Ask. Appendix only if needed. Aim for 8 to 12 slides or 4 to 8 pages, not 30.

Files:

- `docs/proposals/<slug>-proposal.md` -- Word-like memo
- `docs/proposals/<slug>-proposal.html` -- print-to-PDF / slide view

## Figures that are allowed

Use Netie prices and their published facts only. Do not invent conversion rates, traffic, or client case studies.

| Item | Figure | Source |
|---|---|---|
| First draft unlock | RM 500 | hire brief, Stripe product already live |
| Full landing after they see the draft | RM 1,000 to RM 5,000 | hire / outreach-tone |
| Engineering / records / docs | RM 1,000 to RM 5,000 after looking | hire |
| Internal operations | RM 20,000 after written scope | hire |
| Checkout test (optional) | `https://buy.stripe.com/3cIcN54OO6SnaA4g5u9ws07` | existing product. Say test, not buy now |

## Precise offer (say this)

We are not only rewriting a Coming Soon menu. We create a new landing page that sells what they already publish, plus marketing so visitors who land on the site know the offer and can become a customer. On top of that we offer agent work, OCR on documents, and a system-level database (DMS-class). Public proof is https://netie.ai/hire/ and the suite screens on https://netie.ai/.

## Email that goes with the file

Plaintext `body` only. Never `htmlBody`. Point at the proposal in one sentence. One hire URL at most in the mail. Put the checkout in the proposal as an optional test after they want the draft. Recreate the Gmail reply with `replyToMessageId`. Do not `update_draft`.

## Never

- A proposal that is only "I will send a short draft" with no terms.
- Fake Accenture or Goldman logos, stolen slide decks, or verbatim copyrighted pages.
- Invented ROI percentages.
- Sending the file before the owner says send.
- Gemini passwords in git.
