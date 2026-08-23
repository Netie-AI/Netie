# Root sitemap and llms.txt finding

- Date: 2026-08-23 UTC
- Scope: Domain-root discovery for payable /hire/ work
- Keywords: sitemap, llms.txt, File Manager, document root, SEO, agent catalog
- Main idea: The April suite homepage has no hire link and the old sitemap omitted /hire/. Uploading root llms.txt and a hire-first sitemap made the live offers discoverable without touching the Next.js app.

## Verified result

- `/llms.txt`, `/sitemap.xml`, and `/hire/llms.txt` match committed source byte-for-byte.
- Homepage title is still the April Web3 suite page. `/aim/` and `/hire/` remain HTTP 200.
- File Manager can write the document root, not only `/hire/`.

## Public boundary

Do not treat the suite homepage as a sold product. Payable work is https://netie.ai/hire/. The homepage still needs a human-visible hire link in the Next.js source, which is not in this repo.
