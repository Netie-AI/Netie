# CTA scope preselection deployment

- Date: 2026-08-23 UTC
- Agent: computerUse
- Keywords: CTA, brief form, service selection, File Manager, Spaceship, conversion, scope
- Main idea: Each service CTA now carries its matching offer into the scope form before a buyer submits, removing the RM500 website default from file-analysis, system, search, and process requests.

## Deployment return

- Uploaded `/workspace/docs/pay.html` to `/hire/index.html` with Spaceship Hosting File Manager.
- Verified `https://netie.ai/hire/` loads after the upload and has no JavaScript errors.
- Did not change passwords, billing, DNS, domains, Stripe settings, unrelated files, form data, or checkout state.

## Manual verification

| CTA | Observed form selection |
|---|---|
| Hero `Request a written scope` | `Not sure - help me scope it` |
| Proof `Request a file-analysis scope` | `File analysis and presentation - RM 1,500` |
| Company-file search `Request a scope` | `Company-file search with citations - quote` |
| Process map `Map one process` | `Process map and decision prototype - quote` |
| Operations `Discuss the system` | `Internal operations system - RM 20,000 after scope` |
| File analysis `Request a written scope` | `File analysis and presentation - RM 1,500` |

All six CTAs navigated to the brief and selected the expected offer before any submission.

## Mirror verification return

- Agent: computerUse
- Keywords: BrewPage, Surge, CTA, file analysis, browser verification, no submission
- Main idea: The two full-page mirrors serve the same file-analysis scope selection as the canonical page.
- `https://brewpage.app/public/ANzfhLqHto/index.html` loaded and passed both file-analysis CTA checks.
- `https://netie-penang.surge.sh/` loaded and passed both file-analysis CTA checks.
- On each mirror, `Request a file-analysis scope` and the file-analysis card's `Request a written scope` navigated to `#brief` and selected `File analysis and presentation - RM 1,500`.
- No form was submitted and no personal data was entered.
