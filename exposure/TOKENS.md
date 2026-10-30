# Official tokens only. Chat cannot mint these.

I cannot create LinkedIn or Reddit OAuth tokens. "I grant you all access" in chat
is not OAuth. Create the apps, paste tokens into gitignored `exposure/.env`.

## LinkedIn

1. https://www.linkedin.com/developers/apps  -> Create app
2. Products: Sign In with LinkedIn using OpenID Connect, Share on LinkedIn
   (w_member_social). Company Page posts need Marketing Developer Platform.
3. Auth -> generate a member access token with `openid profile w_member_social`
4. Put it in `LINKEDIN_ACCESS_TOKEN`

## Reddit

1. https://www.reddit.com/prefs/apps  -> create **script** app
2. Fill `REDDIT_CLIENT_ID` (under the app name), `REDDIT_CLIENT_SECRET`,
   `REDDIT_USERNAME`, `REDDIT_PASSWORD` (the Reddit account that owns the app)

## GitHub

Optional `GITHUB_TOKEN` with public repo scope. This pack does not open issues
to farm stars.

## Enable auto-post

```bash
cd exposure
python -m netie_exposure tokens --init    # writes .env + local EXPOSURE_GATE
# edit .env: paste official tokens, set EXPOSURE_AUTO_POST=1
python -m netie_exposure tokens         # booleans only, no secret print
python -m netie_exposure auto --grant-auto
```

Auto-post uses official APIs only. One draft per channel per run. No scrape,
no fake followers, no unofficial clients.
