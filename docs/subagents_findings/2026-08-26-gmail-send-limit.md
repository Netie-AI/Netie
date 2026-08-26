# 2026-08-26 Gmail send limit

- Date: 2026-08-26 MYT
- Keywords: Gmail, 500/day, mailer-daemon, CH Seah, not sent, one inbox
- Main idea: Consumer Gmail hit the daily send cap during the Wed 11:00 482. mailer-daemon: "You have reached a limit for sending mail. Your message was not sent." Changing To does not bypass the cap. C H Seah live site only prints `sales@chseahfishery.com.my`. Do not invent a second inbox. Do not send more today. Retry remaining Thu 10:00 MYT after quota reset.

## Evidence

- CH Seah SENT `1a03c15eb1ba5c83` then daemon `1a03c15f5f43d8d3` on thread `1a03ada0afe2fe98`. Recipient never got it.
- Same daemon on City E, XD Auto, Clasico, Cleanmaid, CLT Engineering.
- Live https://www.chseahfishery.com.my/ HTTP 200. JSON-LD and mailto are only `sales@chseahfishery.com.my`. WhatsApp +60 12-745 7188. Did not WhatsApp. Did not invent `info@`.
- Remain list: `docs/wed1100-remain.tsv`.
