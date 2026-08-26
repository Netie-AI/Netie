# 2026-08-25 Spaceship website-row File Manager is the live hire docroot

- Keywords: Spaceship, Manage files, netie.ai, ffvftugcxb, document root, hire overwrite, RM 500
- Main idea: Token cPanel File Manager writes `/home/ffvftugcxb/public_html/hire/` and can show 55KB while live https://netie.ai/hire/ still served a 19KB invoices page. The live vhost is `/home/ffvftugcxb/netie.ai/`. Open it with Hosting Manager **website-row** Manage files (button next to the website name), not plan-card Manage and not the generic cPanel File Manager. After overwrite, curl last-modified and sha256; do not trust File Manager size alone.
- Traps: `nfftugcxb` vs `ffvftugcxb` look similar; this account is `ffvftugcxb`. Query-string cache bypass does not help if you wrote the wrong tree. Last-modified staying at 06:52 GMT means the serving file did not change. Do not overwrite `/`. Do not click Reset cPanel.
