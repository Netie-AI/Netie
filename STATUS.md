# STATUS - Netie constitution repo

**Branch:** `cursor/pointer-control-callers-ca9b` · **PR:** (this) · **main:** `94161af` (PR #12 merged)
**Local gate:** `make ci` (compileall + `python3 scripts/check_docs.py`). GitHub docs-ci: red X, job never starts (Actions spending limit). Not a test fail.

## Now

- Gap scores in `TAS/ESTATE-GAP.md`. Product repos `uv add git+https://github.com/Netie-AI/Netie.git` then `from netie.crew import bind_deep_agent, crew_harness_profile` (also `netie.cortex` / `dms` / `pointer` / `space` / `airgpt` / `control` / `route`). Wheel ships contracts (no `--editable` required). Cortex path has no JEPA/gen-cFSM; C7 generated-SQL stays off; coding-agent tools (`bash` / filesystem) refuse even via `tool_runner` (not Claude Code); writes (`export_pptx` / `item.intake` / `amend.apply` / `call_action`) need an actor; answers need `verified`; `/a2a/messages` is dms-pack only (`scripts/cortex_path.py`). Switchyard host is OpenVault leave-machine only (`scripts/switchyard_honesty.py`); FreeRoute is not that job; score stays 2/10.
- Crew portable contract: `bind_deep_agent` (MIT `create_deep_agent` after wrap; requires `TokenBudget` else unbounded spend; `crew_harness_profile` excludes filesystem/`task`/`write_todos` and `SummarizationMiddleware` so `/conversation_history` is not a transcript dump; injected factory without harness register refuses; `skills`/`memory`/`subagents`/`system_prompt`/`middleware`/`backend`/`response_format`/`debug` refuse), wrap (empty wrap / extra unwrapped names refuse; skill_body on wrap refuses and does not spend; over-budget wrap does not execute; Deep Agents `glob`/`grep`/`delete`/`task` / filesystem / `write_todos` refuse), HITL on known writes including `item.intake`, OpenWork-shaped `search_capabilities` / `execute_capability` / `run_open_ticket` (ungranted does not run; require `TokenBudget`; over-budget ticket stays open; batch cap-2), `run_batch` requires `TokenBudget` else unbounded spend, cap-2 hard refuse above 2, parent-run, `skill` kind refused until a registry row exists, factory `index()` drops prompts, ticket runner (refusal on the board, ticket stays open), session view (no transcript; permissions drop builtins), checkpoint/summarise ids-only, ledger refuses skill_body on append, refused jobs do not spend budget, seat router names billing-bypass products, WIP-2, OV gate.
- Product specs: DMS Space ACL (warehouse bind, SQL required, row copy, SQL cannot name an ungranted table, bronze browse still needs grant, `chat_mode` AnythingLLM overlay abstains, answer over DitchContext 12k abstains), AirGPT retrieve stays in one Space (incomplete/unlabeled/`chat_*.md` not cited; file mention stays in Space; NVIDIA_RAG_EVAL/semantic not a chunker; ChatGPT memory abstains; over-budget retrieve abstains), Pointer UACC wrap (68 names behind Cortex; planner/history/clipboard/JS/uncropped screenshot/`get_screen_info`/page-dump/process-list/window-dump/env-dump/secret-hotkey/uncropped-paint/uacc-override refuse; hosted e2b/Perplexity Computer refuse), Space preview/write refuses secrets / ungated OCR / ungated chat-over-preview / over-budget excerpts, Control board + session (no prompts / no transcript; RDP/VNC/SSH/Guacamole kinds refuse; over DitchContext 12k refuses). Constructor `compileIR` stays ours (`scripts/constructor_honesty.py`). Crew `load_den` refuses OpenWork `ee/`.
- Accessible remotes (clone yes, `cursor[bot]` push 403): Netie (this; main merge works), OpenVault, constructor, Cortex `bf4ecee`, dms `3f9a9be`, Pointer `8c0e6c2`, netie-control `82ab1ae`, Netie-KB `10356e5` (`kb.py validate` OK, 58 artifacts).
- 404 to this token: AirGPT, Space, Cortex-Crew.
- Sibling push 403: patches in `docs/patches/`. Cortex/dms callers already on Netie main (PR #12). New: `pointer-netie-hands.patch` (UACC search drops planner/clipboard/window dump; `bindComputer` is local tray; native observe stays DR-0005). `control-netie-board.patch` (`from netie.control import project_board` when installed; `/v1/rdp` `/v1/vnc` `/v1/guacamole` `/v1/ssh` 405). C2/MIN_TESTS stand. Do not mint a new Cortex #42.

## Next (blocked on founder clicks in `docs/ACCESS.md`)

1. GitHub App select private repos (no passwords).
2. Pay / raise https://github.com/organizations/Netie-AI/settings/billing
3. Contents write on OpenVault + constructor + Cortex + dms + Pointer + netie-control (clone yes, push 403).
4. Land Cortex/dms/Pointer/Control patches on product HEAD.

## Later

Crew product repo. OpenVault HT1. AirGPT `rag/` vs corpus.

C2/MIN_TESTS stand. Do not mint Cortex #42. Do not touch Cortex PRs #4 #41 #43 #44.

Do not clone `b-nnett/grok-bot-0.18-reconstructed`. Do not take account passwords.
