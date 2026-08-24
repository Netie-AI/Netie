# 2026-08-25 Canonical hire copy/records/docs File Manager upload

- Keywords: Spaceship File Manager, hire, copywriting, records ops, documentation, llms.txt, catalog.json
- Main idea: Hosting Manager File Manager overwrote `/hire/index.html`, `/hire/catalog.json`, `/hire/llms.txt`, and true-root `/llms.txt` from git. Independent curl after upload: all four byte-match source. Title is copy/records/docs. Homepage still HTTP 200 with no 302. Session was already logged in; no new 2FA this pass. Jupiter is still the wrong path.
- Traps: File Manager can sit in `/page/`. Root `/llms.txt` must be in the folder that contains `hire/`, not under `/page/`. Do not overwrite `/`. Do not commit the Spaceship password. Surge mirror was already republished from the same `docs/pay.html`. Do not poll Stripe until 26 Aug MYT.
