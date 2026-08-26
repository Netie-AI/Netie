# 2026-08-25 Spaceship Domain Manager cannot path-redirect /hire

- Keywords: Spaceship, Domain Manager, URL redirect, path redirect, /hire, Surge, DNS
- Main idea: Domain Manager can forward the whole domain or a subdomain. It cannot redirect only `https://netie.ai/hire/` to Surge. File Manager is still the upload path.
- Traps: Domain-wide URL redirect would take the April homepage with it. Subdomain redirect could make `hire.netie.ai` point at Surge, but that is a DNS change; do not add it unless the owner asks. `.htaccess` for `/hire/` needs File Manager/cPanel, which still says login unavailable. Do not overwrite `/`.
