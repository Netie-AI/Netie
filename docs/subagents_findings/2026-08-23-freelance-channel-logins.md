# Freelance channel login finding

- Date: 2026-08-23 UTC
- Scope: Push registered marketplaces toward a payable gig without Stripe or inbox polling
- Keywords: Fiverr, PeoplePerHour, Freelancer, Twine, Truelancer, Guru, Gumroad, Workana, Hacker News
- Main idea: Twine is live. A Truelancer landing-page service is submitted and pending moderator approval. Fiverr, Guru, and Gumroad passwords fail. Do not treat pending review as a paid order.

## Measured

- Fiverr: wrong username or password for oojianhongg@gmail.com. Did not reset.
- PeoplePerHour: logged in; seller application needs a paid plan. Did not buy. 24 Aug 22:20 MYT recheck: SEND PROPOSAL is visible on buyer projects, but the next page still asks for a paid plan (£11.95/month, 12-month). Proposal credits 0. Profile title/about/location can be saved without paying; location had geolocated to Ashburn, VA and was corrected to George Town, Penang (pending moderation).
- Freelancer.com: credentials accepted, repeated reCAPTCHA failed.
- Twine: https://www.twine.net/jianhong live, available, application_credits=0, inbox empty. Did not buy credits.
- Truelancer: service still pending 23 Aug 14:25 MYT. Seller URL https://truelancer.com/freelance-service/i-will-build-an-ai-product-landing-page-from-your-copy-655675 INR 10000. 0 sold. Bidding blocked on mobile OTP; did not request SMS. Country field locked to India at account level. Image re-upload did not persist through Update Service (Please Try Again).
- Mastodon: public seeking-work post https://mastodon.social/@jianhongpg/117143382421294576 verified via statuses API. Proof and Twine links present. 0 boosts at post time.

- Guru: login failed.
- Gumroad: password in the VM file is rejected. Did not reset.
- Workana: account was created with Facebook; email/password login refused.
- wantstobehired.com: login works; it only aggregates HN seeker posts, no seller gigs.
- Hacker News: logged in as jianhongpg, karma 1, too new for a top-level freelance-thread comment. Profile email and about saved in the logged-in browser session. This datacenter IP gets `Sorry.` on the public user page, so public HN HTML was not re-fetched here.
- Reddit r/forhire 24 Aug 20:17 MYT: datacenter IP blocked ("network security"), then login wall. No existing session. Did not type a password or request SMS. Paste is `docs/reddit-paste.txt`. Do not spam a second subreddit.

## Do not

- Reset Fiverr, Guru, Gumroad, or Reddit.
- Buy Twine Pro, PPH plans, or bid packs.
- Treat a pending Truelancer review or a live Twine profile as a Stripe charge.
