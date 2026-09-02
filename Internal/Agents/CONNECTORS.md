# Connectors + identity (honest, 2026-08-23)

PR Bot publishes this table every wake. No second OAuth broker.

| Connector | Identity / probe | Connected | Notes |
|---|---|---|---|
| GitHub | `gh auth status` -> **jian-hong** (`repo`, `workflow`) | yes | Merge via `gh pr merge`. Crew `github.py` report-only. |
| Gmail | **oojianhongg@gmail.com** (MONEY_LANE) | IMAP if `GMAIL_IMAP_USER` + `GMAIL_APP_PASSWORD` in Crew Providers; else drop `.eml` | Crew **never sends**. Headers only (From/Subject/Date). |
| OpenVault | `GET http://127.0.0.1:5000/api/healthz` | probe | Keys / FreeRoute. HT2-HT5 HUMAN_STOP for spend. |
| Spaceship host | Hosting Manager (persistent Playwright profile) | yes | **Reuse.** `netie.ai` Web Hosting Essential at `209.74.68.17`. cPanel + FTP `ship@netie.ai` already exist. SoT: `SHIP_SPACESHIP.md`. Do not buy New hosting. Passwords: OpenVault / `%USERPROFILE%\.netie\spaceship-ftp.env`. |
| Cortex engine | `GET http://127.0.0.1:8010/api/engine/activity` | probe | Governed ask via `/dms/query`. |
| Plane board | `http://localhost:8099/netie/` | probe | Holds view. GitHub Issues stay SoT. |
| Netie Control | `GET http://127.0.0.1:8040/healthz` | probe | Tree **E:\NetieControl**. If dirty, writer is **netie-controlagent** - EXTRA_STOP. Do not clone `E:\Netie-Control`. Do not boot paperclip `:3100`. Probe: `Start-NetieControl.ps1`. KB F-0029. |
| UACC | armed + `CORTEX_COMPUTER_CONTROL=1` | disarmed default | Mutating = Approve. |
| Pointer HUD | Electron `D:\Pointer` | DOWN typical | Human-confirm Act. Not Crew MCP. |
| Slack / Notion | paste-only | no | Operator pastes. |
| Grok Bot | local app | alive when capped | Judgement when uncapped. |

## Gmail identify flow

1. If IMAP configured: `CortexOS.crew.inbox` fetches last N INBOX headers.
2. Else: operator drops `.eml` / `.txt` onto Crew.
3. Match replies to `Internal/learning-plan/sme-targets*.md` domains.
4. If a human replied: `feedback-learn` then `chat-human` draft. Append `feedback-log.md`. Do not mail a new SME that tick. Do not default to a 45-min extract booking.
5. If no open reply: MONEY_LANE heartbeat may draft one new extract. Human sends.

## Mem0 / MemPalace

**Not installed.** Markdown vault: `PR_BOT_MEMORY.md`. Chat RAG: Cursor SearchConversations.
