# 2026-08-26 Hire URL on all Wed first-mail drafts

- Keywords: Wed 09:00, netie.ai/hire, update_draft, google.com/url, HD Hearing, Solid Kitchen
- Main idea: All 168 queued landing-page drafts now include one hire line before the close. Gmail MCP wraps a typed `https://netie.ai/hire/` into `https://www.google.com/url?q=https://netie.ai/hire/` in stored plaintext and HTML. Click still reaches hire. Do not pass `htmlBody`. Do not `update_draft` the Toon reply.
- Traps: Rewriting to unwrap just re-wraps. Send with `draftId` as-is at 09:00. Do not send Toon (`r-7427464740298229176` on `1a03642393b091d6`). One link max; no Stripe in first mail.
