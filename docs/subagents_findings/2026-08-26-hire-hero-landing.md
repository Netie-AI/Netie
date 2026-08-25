# Hire hero now matches the RM 500 landing mail

- Date: 2026-08-26 MYT
- Keywords: hire, hero, RM 500, landing page, Wed 09:00, File Manager
- Main idea: Live `/hire/` still said "Hire us for your work" and buried the landing offer. Wed 09:00 drafts send people to that URL. Source hero is now: better landing page, RM 500 unlocks the first draft, Request the first draft. No Stripe button. Landing card is first. 08:00 File Manager must upload because sha256 changed.

## Why

Toon proved a vague hook fails. 168 first-mails now say landing page + RM 500 + https://netie.ai/hire/. The old hero dumped every service and asked for a written scope with "Not sure".

## What changed in git

- `docs/pay.html` H1, lede, primary CTA, facts, first service card, brief default
- `docs/catalog.json`, `docs/llms.txt`, `docs/root-llms.txt` lead with the same offer
- No `buy.stripe.com` on hire. Checkout still sent only after they ask

## Upload

Wed 08:00 timer must write website-row `/home/ffvftugcxb/netie.ai/hire/`, not token cPanel `public_html`. Do not overwrite `/`. Live still sha256 `a8fb92f4...`. Git and Surge now `7c91bf0ba5bb5cfebdbb2abdfe5b99ae4f253a88085b4b943d450dbe6c80c06d` (56306 bytes). Skip only if live already matches that.
