# 2026-08-25 Gmail update_draft can detach a reply

- Keywords: Gmail, update_draft, replyToMessageId, Toon, Advanced Inkjet, holding draft
- Main idea: `update_draft` on a reply holding pen can move it onto a new thread. Recreate with `create_draft` + `replyToMessageId` set to the buyer's message. Trash only the stray draft thread.
- Traps: Draft `r-7513366825887340098` left thread `1a03642393b091d6` for `1a03933c336afc6c`. Sending that would have been a new mail, not a reply. Current holding draft is `r-7427464740298229176` on the original thread. Do not send until the owner says send. Do not trash the buyer thread.
