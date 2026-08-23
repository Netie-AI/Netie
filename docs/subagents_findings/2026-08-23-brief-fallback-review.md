# Brief form fail-visible conversion review

- Date: 2026-08-23 UTC
- Agent: Claude Opus explore
- Keywords: mailto, copy fallback, scope brief, conversion, mobile, accessibility, no false sent state
- Main idea: The written-scope form is the last step for the RM1,500 offer, so it must visibly prepare a copyable brief instead of relying on a scripted `mailto:` navigation that can fail without feedback.

## Evidence

- The former submit handler only assigned a `mailto:` URL through JavaScript, leaving no visible result if no local mail handler existed.
- The prior conversion review already identified this as an open risk: the mail-composing script must be an enhancement only and must never imply that a brief was sent.
- The Monday RM1,500 outreach and the trace proof both route interested buyers to the written-scope form, so this failure affected the current outbound funnel rather than an unused path.

## Implemented recommendation

- Replace `Open an email draft` with `Prepare my brief`.
- After valid native form validation, reveal a panel that states no data has been sent or uploaded.
- Put the full composed brief in a readonly textarea.
- Provide a user-triggered email-app link and a copy button with Clipboard API plus manual-copy fallback.
- Preserve the existing WhatsApp route and service-CTA preselection.

## Required verification

- Empty required fields must keep the prepared panel hidden.
- A synthetic file-analysis brief must show every expected field and the selected `Need:` value.
- The generated email route must be a link rather than an automatic mail-client navigation.
- Copy feedback must only claim success when copying succeeds; otherwise it must explain manual selection.
- Canonical, BrewPage, and Surge must be re-published from the same source and tested without sending a brief.

## Canonical deployment return

- Agent: computerUse
- Keywords: Spaceship, File Manager, native validation, prepared brief, mailto, clipboard
- Main idea: The canonical page exposes the visible fallback only after valid input and never opens an email app automatically.
- Spaceship File Manager uploaded `docs/pay.html` to `/hire/index.html`; no account, domain, billing, or Stripe settings changed.
- Native browser validation kept the panel hidden for an empty submission.
- With synthetic test data and the file-analysis CTA, the panel showed all nine brief fields and `Need: File analysis and presentation - RM 1,500`.
- The `mailto:` link existed but was not clicked. Copy showed a success message after a clipboard operation; no brief was pasted, sent, or uploaded.

## Mirror verification return

- Agent: computerUse
- Keywords: BrewPage, Surge, prepared brief, copy fallback, mailto, no submission
- Main idea: Both full-page mirrors provide the same locally prepared brief and truthful no-send state as the canonical page.
- Hard-refreshed BrewPage and Surge passed the synthetic file-analysis brief flow.
- Each panel displayed `Your brief is ready to send`, stated nothing was sent or uploaded, and included all synthetic form fields.
- Both `Open my email app` controls were verified as `mailto:` links without being clicked.
- Copy feedback was visible, and no form submission, file upload, checkout, email, or WhatsApp route occurred during testing.
