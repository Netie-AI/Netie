# Stripe business-model verification checklist

Status verified from the live Stripe account on 2026-08-23:

- `charges_enabled=true` and `payouts_enabled=true`.
- Card, GrabPay, Link, and transfers capabilities are active.
- The account has one MYR standard-payout bank account configured.
- `business_model_verification.form` is currently due and past due. Its recorded deadline was 2026-07-21 06:45 UTC.
- Stripe has not disabled charges or payouts yet, but this is a compliance risk. Do not claim it is resolved until the Dashboard shows no past-due requirement.

## Paste-safe business description

Use only if it still describes the actual business at submission time:

> Netie.AI is a Malaysia-based software-development and consulting business. It provides custom business websites, document and spreadsheet analysis, browser-based process prototypes, document-search prototypes, and scoped internal operations systems. Services are agreed in writing before payment and delivered as files, documentation, or custom software.

This is grounded in `docs/resume.md`, `docs/OFFER.md`, and `docs/pay.html`. It intentionally removes unsupported property-transaction, consumer-device, and generic gamified-service claims from the current Stripe profile.

## Owner-only answers

Complete these only from actual business records and policies:

1. Legal entity type, registration, owner/director relationship, and identity documents.
2. Actual expected transaction frequency, volume, and average payment amount. Do not project from an empty revenue history.
3. Refund, cancellation, and terms links. Do not promise a policy that is not published and followed.
4. Actual data-handling default and any customer-controlled-infrastructure commitment.
5. Any declaration, consent, or attestation submitted to Stripe.

## Before submitting

- Verify the public support contact and website remain current.
- Confirm the business description matches the services that can actually be delivered.
- Do not describe Jumpwin employer infrastructure, unrelated historical products, gambling/casino services, financial advice, or property-transaction facilitation as a current Netie offer.
- Record the Dashboard outcome and any new requirement in `STATUS.md`.
