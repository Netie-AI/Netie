---
name: show-before-send
description: Never send buyer Gmail, WhatsApp paste, or a priced proposal until the owner has seen the exact body in this chat and said send. Use before any send_message.
---

# Show before send

Toon at Advanced Inkjet (`toon@advancedinkjet.com.my`, thread `1a03642393b091d6`) replied that "Sungai Buloh print page" was unclear. That is the proof. Do not send another buyer mail from memory of the old Coming Soon pitch.

## Rule

1. Write the exact plaintext `body` and subject in this chat, or in `docs/proposals/<slug>.md` under `Owner-approval draft:`.
2. Tell the owner who it is to, and that it is not sent yet.
3. Wait for an explicit send. "Looks good", "send it", or a corrected body.
4. Then `send_message`. Plaintext `body` only. Never `htmlBody`.

`create_draft` is allowed as a holding pen after the owner has seen the words. Do not treat a draft as approval. For a reply, set `replyToMessageId` to the buyer's message. Do not `update_draft` a reply holding pen: Gmail MCP can move it onto a new thread. Recreate the draft on the original thread, then trash the stray thread only.

## Exceptions

- A timer the owner already approved for a named send window may fire those already-approved `draftId`s. New replies and new first-mails after 25 Aug 20:40 MYT are not in that bucket.
- Do not rewrite and send the 168 queued Coming Soon drafts under the old voice. Load `.cursor/skills/outreach-tone/SKILL.md` and rewrite one firm at a time, then show the owner, or skip that firm.

## Never

- Send because the standing revenue goal is still open.
- Send because they replied and you want to be fast.
- Send a Stripe link until they asked for the first draft and the owner approved that mail.
