# Freelance channel login finding

- Date: 2026-08-23 UTC
- Scope: Push registered marketplaces toward a payable gig without Stripe or inbox polling
- Keywords: Fiverr, PeoplePerHour, Freelancer, Twine, Truelancer, Guru, Gumroad, Workana, Hacker News
- Main idea: Twine is live. A Truelancer landing-page service is submitted and pending moderator approval. Fiverr, Guru, and Gumroad passwords fail. Do not treat pending review as a paid order.

## Measured

- Fiverr: wrong username or password for oojianhongg@gmail.com. Did not reset.
- PeoplePerHour: logged in; seller application needs a paid plan. Did not buy.
- Freelancer.com: credentials accepted, repeated reCAPTCHA failed.
- Twine: https://www.twine.net/jianhong live, available, application_credits=0, inbox empty. Did not buy credits.
- Truelancer: service submitted 23 Aug. Seller URL https://truelancer.com/freelance-service/i-will-build-an-ai-product-landing-page-from-your-copy-655675 titled for INR 10000 (~USD 120). Status pending moderator approval. Profile city set to George Town, Penang, Malaysia. Constructor screenshot uploaded. Honest Penang copy. No Stripe on the listing.
- Guru: login failed.
- Gumroad: password in the VM file is rejected. Did not reset.
- Workana: account was created with Facebook; email/password login refused.
- wantstobehired.com: login works; it only aggregates HN seeker posts, no seller gigs.
- Hacker News: logged in as jianhongpg, karma 1, too new for a top-level freelance-thread comment. Profile email and about saved in the logged-in browser session. This datacenter IP gets `Sorry.` on the public user page, so public HN HTML was not re-fetched here.

## Do not

- Reset Fiverr, Guru, or Gumroad.
- Buy Twine Pro, PPH plans, or bid packs.
- Treat a pending Truelancer review or a live Twine profile as a Stripe charge.
