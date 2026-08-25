# 2026-08-26 Craigslist Malaysia as Carousell backup

- Date: 2026-08-26 MYT
- Keywords: Craigslist, malaysia, post.craigslist.org/c/mly, services, RM 500, Carousell Cloudflare
- Main idea: Carousell from this VM stays on Cloudflare. Craigslist Malaysia posting is https://post.craigslist.org/c/mly. Paste in `docs/craigslist-paste.txt`. Confirm mail would land in oojianhongg@gmail.com. Do not put Stripe on the listing. A listing is not income until a buyer pays.
- Traps: Do not invent a Craigslist password. Do not post erotic or housing. Skip if hCaptcha blocks. Do not resume remain-host hunt. Gmail MCP strips `=` from Craigslist URLs (`key=` becomes `key`), so curl/browser of the decoded `/pass` link 404s. HEAD on a one-time login link burns it. Owner must tap complete your posting in the Gmail app on `robot@craigslist.org` / `craigslist email verification`. A listing is not income.
