# Restore original homepage finding

- Date: 2026-08-23 UTC
- Scope: Stop sending netie.ai/ to /hire/; keep the April landing as the public homepage
- Keywords: .htaccess, 302, homepage, suite, hire band, File Manager, HSTS
- Main idea: The original Next.js landing was still on disk at index.html. Removing the root rewrite restores it. Hire stays a smaller centered introduce page with a compact home-page band.

## Verified result

- `curl -sI https://netie.ai/` is HTTP 200. Title is `Netie.AI | Unified AI x Web3 x Hardware Platform`.
- Homepage HTML includes `<script src="/home-hire-band.js" defer></script>`. `/home-hire-band.js` matches git.
- Hire, suite, knowledge, ops, trace, catalog, and both llms/sitemap files match committed source.
- `/aim/` and `/asa/` remain HTTP 200. HSTS, nosniff, and DENY remain on the homepage response.

## Do

- Keep HSTS, nosniff, and DENY when replacing document-root .htaccess.
- Upload `home-hire-band.js` and add one script tag to the existing homepage. Do not replace `_next/` or the Suite chat UI.
- /suite/ is a side index, not the new homepage.

## Do not

- 302 `/` to `/hire/` again.
- Throw away the April cinematic landing to make hire full-bleed landscape.
