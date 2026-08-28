# STATUS - Netie constitution repo

**Branch:** `cursor/kahn-object-failclose-ca9b` · **PR:** https://github.com/Netie-AI/Netie/pull/9
**Local gate:** `make ci` (compileall + `python3 scripts/check_docs.py`). GitHub docs-ci: red X, job never starts (Actions spending limit). Not a test fail. PR #7 is on `main`.

## Now

- Gap scores in `TAS/ESTATE-GAP.md`. Cortex path has no JEPA/gen-cFSM; C7 generated-SQL stays off; coding-agent tools (`bash` / filesystem) refuse even via `tool_runner` (not Claude Code); writes (`export_pptx` / `item.intake`) need an actor; answers need `verified`; `/a2a/messages` is dms-pack only (`scripts/cortex_path.py`). Switchyard host is OpenVault leave-machine only (`scripts/switchyard_honesty.py`); FreeRoute is not that job; score stays 2/10.
- Crew portable contract: `bind_deep_agent` (MIT `create_deep_agent` after wrap; HarnessProfile excludes filesystem/`task`/`write_todos`; `skills`/`memory`/`subagents`/`system_prompt`/`middleware`/`backend`/`response_format`/`debug` refuse), wrap (empty wrap / extra unwrapped names refuse; Deep Agents `glob`/`grep`/`delete`/`task` / filesystem / `write_todos` refuse), HITL on known writes including `item.intake`, OpenWork-shaped `search_capabilities` / `execute_capability` (ungranted does not run; batch cap-2), cap-2 hard refuse above 2, parent-run, `skill` kind refused until a registry row exists, factory `index()` drops prompts, ticket runner (refusal on the board, ticket stays open), session view (no transcript; permissions drop builtins), checkpoint/summarise ids-only, ledger refuses skill_body on append, refused jobs do not spend budget, seat router names billing-bypass products, WIP-2, OV gate.
- Product specs: DMS Space ACL (warehouse bind, SQL required, row copy, SQL cannot name an ungranted table, bronze browse still needs grant, `chat_mode` AnythingLLM overlay abstains), AirGPT retrieve stays in one Space (incomplete/unlabeled/`chat_*.md` not cited; file mention stays in Space; NVIDIA_RAG_EVAL/semantic not a chunker; ChatGPT memory abstains; over-budget retrieve abstains), Pointer UACC wrap (68 names behind Cortex; planner/history/clipboard/JS/uncropped screenshot/page-dump/process-list/env-dump/secret-hotkey/uncropped-paint/uacc-override refuse), Space preview/write refuses secrets / ungated OCR / ungated chat-over-preview / over-budget excerpts, Control board + session (no prompts / no transcript; RDP/Guacamole kinds refuse).
- Accessible remotes: Netie (this), OpenVault public (`main` CI green 2026-08-27, STATUS ~78%, HT1 not done), constructor public (pages.yml green).
- 404 to this token: Cortex, dms, AirGPT, Pointer, Space, Control, KB, Cortex-Crew.
- Sibling push 403: patches in `docs/patches/`. Constructor compiler **42 passed** (18 patches; `item.intake` is a write). OpenVault: 15 sorts + 4 execution shapes. `/v1` last-hop usage is measured; context-relay persists caller handoff per issued seat (32-blob cap); Anthropic-only shape hops name the skip (no Messages API); no matching hop is 503 not empty; execution-shape serves() is catalog-true; `parallel` / quota-fetch / sqlite persist / autoCombo / compress / MCP/A2A / `quota-share` is 501; hop posts drop `combo` / `skill_body`; `/v1` Crew body is 400 `openvault_crew_body`. Tests **90 passed** (25 product patches). C2/MIN_TESTS stand. No Cortex #42.

## Next (blocked on founder clicks in `docs/ACCESS.md`)

1. GitHub App select private repos (no passwords).
2. Pay / raise https://github.com/organizations/Netie-AI/settings/billing
3. Write on OpenVault + constructor.
4. Wire contracts into product callers (PRD-001 in dms first; PRD-002 imports `scripts/crew_*.py`).

## Later

Crew product repo. OpenVault HT1. AirGPT `rag/` vs corpus. Pointer vs UACC on HEAD.

C2/MIN_TESTS stand. Do not mint Cortex #42. Do not touch Cortex PRs #4 #41 #43 #44.

Do not clone `b-nnett/grok-bot-0.18-reconstructed`. Do not take account passwords.
