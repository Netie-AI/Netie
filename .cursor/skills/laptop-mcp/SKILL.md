---
name: laptop-mcp
description: Use laptop browser, Gmail, Drive, and MCP plugins. Lazy-load tools. Never store passwords in git. Record blocks in STATUS.md.
---

# Laptop and MCP

## Load when needed

- Gmail: search `from:truelancer.com`, `in:anywhere`, spam. Label job mail. Do not send platform bids via Gmail.
- Drive: Docs/Slides as the shareable copy of a proposal.
- Browser / computerUse: Truelancer Send Proposal, Google sign-in. Stop on a password wall. Ask Jian. Do not invent passwords.
- Cloudflare / Higgsfield MCP: needsAuth until Jian signs in. Do not fake a hosted skill server.

## Shared state

Push `STATUS.md` so cloud agents, laptop Cursor, and Claude Code see the same lane.
Skills stay in `.cursor/skills/`. That is the catalog. GitHub is the host.

## Never

- Commit `key.md`, `.env`, or session cookies
- Pay off-platform
- Click through a 2FA screen with a guessed code
