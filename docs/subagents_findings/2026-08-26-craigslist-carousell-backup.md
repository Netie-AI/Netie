# 2026-08-26 Craigslist Malaysia as Carousell backup

- Date: 2026-08-26 MYT
- Keywords: Craigslist, malaysia, post.craigslist.org/c/mly, services, RM 500, Carousell Cloudflare, Go Passwordless, quoted-printable
- Main idea: Carousell from this VM stays on Cloudflare. Craigslist Malaysia computer-services listing is live at https://malaysia.craigslist.org/cps/d/landing-page-writer-in-penang-rm-500/7955885182.html (HTTP 200, RM 500 first draft, hire URL, no Stripe checkout). A listing is not income until a buyer pays.
- Traps: Gmail MCP `PLAIN_TEXT` / HTML strips `=` from Craigslist URLs (`key=` becomes `key`; `userid=3D40` can look like `userid@`). Use `get_message` `RAW`, quoted-printable decode (`=3D` -> `=`, soft wrap), then GET `/pass` (never HEAD; HEAD burns one-time links). The `/pass` page is password options. Use **Go Passwordless** (`goPasswordless=1`) then ACCEPT terms. Do not invent a Craigslist password. Search/RSS from this VM can stay empty or 403 while the direct post URL is live. Do not post erotic or housing. Do not resume remain-host hunt.
