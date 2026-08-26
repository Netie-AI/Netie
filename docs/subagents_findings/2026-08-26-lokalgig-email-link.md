# LokalGig Malaysia: email link, captcha blocks curl

Date: 2026-08-26 08:20 MYT

## What is true

- https://lokalgig.my/ HTTP 200. Zero-commission Malaysia gig board. `/gigs/create` exists. Category `web-mobile-dev` already has RM 500 website gigs.
- Sign-in page offers Email link: "No password needed — we'll email you a sign-in link." Also Google and Password. Do not invent a password.
- Supabase OTP without Turnstile returns `captcha_failed` / `no captcha_token found`. Do not scrape the anon key into git.
- Owner phone paste sent thread `1a03b71618229dc8`. File `docs/lokalgig-paste.txt`. Headed computerUse started to click the captcha and request the mail.
- Locanto still not live (Cloudflare human check). Craigslist still HTTP 200. Hire still sha256 `dce8fe2c...`.

## Trap

A magic-link board still needs the site captcha. Curl of `/auth/v1/otp` is not enough. Same Gmail RAW + GET-not-HEAD rule as Craigslist once the mail arrives.
