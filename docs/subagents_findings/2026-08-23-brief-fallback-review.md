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
