# Stripe payouts - founder Dashboard only

This agent will not upload identity documents and will not store NRIC, passport, or selfie files.

Measured 2026-08-22: live NETIE `charges_enabled=true`, `payouts_enabled=false`, `disabled_reason=requirements.past_due`. Charges can still land. Bank payouts cannot.

## Currently due (no PII)

1. Identity document (keyed identity failed). Upload in Dashboard a document that matches the name already on the account.
2. Business-model verification form (Stripe interview in Dashboard).

Do not email those files to this agent. Do not commit them. Do not send NRIC in chat.

## Open

https://dashboard.stripe.com/settings/update

Bank on file: Bank Islam, last4 5043, weekly Monday. Delay 5 days after payouts_enabled becomes true. Do not promise same-day bank receipt.

Unlock: `payouts_enabled=true` recorded in Pointer/STATUS.md.
