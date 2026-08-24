---
name: distill-into-skills
description: After a method works, save it under .cursor/skills so the next agent does not rediscover it.
---

# Distill into skills

When a proposal, chat, or login path worked:

1. Strip one-off names.
2. Keep the rule: what to do, what never to do, one example.
3. Write `.cursor/skills/<name>/SKILL.md`.
4. Add one row to `.cursor/AGENTS.md`.
5. Put a one-line pointer in `STATUS.md` if the lane is live.

Do not store secrets, NRIC, passwords, or API keys in skills.
Do not create a dated capture file when a skill patch will do.
