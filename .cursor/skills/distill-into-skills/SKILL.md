---
name: distill-into-skills
description: After Claude or another model produces a good method, save it as a Netie skill so the next Grok run can reuse it.
---

# Distill into skills

When a model writes a strong email, proposal, or build sequence:

1. Strip the one-off names.
2. Keep the rule: what to do, what never to do, one example.
3. Write or patch a file under `.cursor/skills/<name>/SKILL.md`.
4. Add one row to `.cursor/AGENTS.md`.
5. If it is a trap, add a row in `docs/subagents_findings/INDEX.md`.

Do not store secrets, NRIC, passwords, or Stripe keys in skills.

Next timer should load `.cursor/AGENTS.md` then the matching skill, not rediscover tone from STATUS.
