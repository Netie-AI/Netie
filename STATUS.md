# STATUS - Netie constitution repo

**Branch:** `cursor/redact-openrouter-key-0d3c` · **PR:** https://github.com/Netie-AI/Netie/pull/10
**Local gate:** `make ci` / `python3 scripts/check_docs.py`.
**GitHub docs-ci:** red X, job never starts (Actions spending limit). Not a test fail.

## Now

- GitGuardian OpenRouter leak: public `Keys.txt` + curl Bearer since 2026-08-02. Files removed; scan gate on; **founder must revoke** OpenRouter plus the six other keys in that dump (`docs/ACCESS.md` section 5). History still has the blobs.
- Gap scores in `TAS/ESTATE-GAP.md`. Cortex path has no JEPA/gen-cFSM; writes need an actor; answers need `verified`; `/a2a/messages` is dms-pack only (`scripts/cortex_path.py`).
- Crew portable contract: wrap (empty wrap / extra unwrapped names refuse; Deep Agents `task` / filesystem / `write_todos` refuse), HITL on known writes, cap-2 hard refuse above 2, parent-run, `skill` kind refused until a registry row exists, factory `index()` drops prompts, ticket runner (refusal on the board, ticket stays open), session view (no transcript), checkpoint/summarise ids-only, ledger refuses skill_body on append, refused jobs do not spend budget, seat router names billing-bypass products, WIP-2, OV gate.
- Product specs: DMS Space ACL (warehouse bind, SQL required, row copy, SQL cannot name an ungranted table), AirGPT retrieve stays in one Space (incomplete/unlabeled not cited), Pointer UACC wrap (68 names behind Cortex; planner/clipboard/JS/secret-hotkey refuse), Space preview/write refuses secrets / ungated OCR, Control board + session (no prompts / no transcript).
- Accessible remotes: Netie (this), OpenVault public (`main` CI green 2026-08-27, STATUS ~78%, HT1 not done), constructor public (pages.yml green).
- 404 to this token: Cortex, dms, AirGPT, Pointer, Space, Control, KB, Cortex-Crew.
- Sibling push 403: patches in `docs/patches/`. Constructor compiler **28 passed** (`compileIR` entry is Kahn source not array[0]; output is Kahn sink app, or last Kahn node when no app/audit, not array-last; `topo()` drops cycle leftovers; unlabeled `tool_call` / object / `set point` / tier do not invent Cortex defaults; inspect shows `(pick)`). OpenVault: 15 sorts + 4 execution shapes. `/v1` last-hop usage is measured; context-relay persists caller handoff per issued seat (32-blob cap); Anthropic-only shape hops name the skip (no Messages API); no matching hop is 503 not empty; execution-shape serves() is catalog-true; `parallel` / quota-fetch / sqlite persist / autoCombo / compress / MCP/A2A is 501. Tests **77 passed**. C2/MIN_TESTS stand. No Cortex #42.

## Next (blocked on founder clicks in `docs/ACCESS.md`)

1. Revoke leaked provider keys (ACCESS.md section 5). OpenRouter first.
2. GitHub App select private repos (no passwords).
3. Pay / raise https://github.com/organizations/Netie-AI/settings/billing
4. Write on OpenVault + constructor.
5. Wire contracts into product callers (PRD-001 in dms first; PRD-002 imports `scripts/crew_*.py`).

## Later

Crew product repo. OpenVault HT1. AirGPT `rag/` vs corpus. Pointer vs UACC on HEAD.

C2/MIN_TESTS stand. Do not mint Cortex #42. Do not touch Cortex PRs #4 #41 #43 #44.

Do not clone `b-nnett/grok-bot-0.18-reconstructed`. Do not take account passwords.
