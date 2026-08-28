# STATUS - Netie constitution repo

**Branch:** `cursor/ecosystem-scale-constructor-0d3c`
**Local gate:** `make ci` (compileall + `python3 scripts/check_docs.py`). GitHub docs-ci: red X, job never starts (Actions spending limit). Not a test fail.

## Now

- GitGuardian leak: public `Keys.txt` dump still on `main` until this lands. Scan gate on. **Founder must revoke** OpenRouter plus the six other keys (`docs/ACCESS.md` section 5). History still has the blobs.
- Gap scores in `TAS/ESTATE-GAP.md`. Product repos `uv add git+https://github.com/Netie-AI/Netie.git` then `from netie.crew import bind_deep_agent, crew_harness_profile`. Wheel ships contracts. Cortex path has no JEPA/gen-cFSM; writes need an actor; answers need `verified`; `/a2a/messages` is dms-pack only.
- Constructor `compileIR` stays ours (`scripts/constructor_honesty.py`). Crew wrap/HITL/cap-2/OV gate/ids-only checkpoint already on main. Sibling push 403: constructor compiler **62 passed** (26 patches). OpenVault routing **145 passed**.

## Next (blocked on founder clicks in `docs/ACCESS.md`)

1. Revoke leaked provider keys (ACCESS.md section 5). OpenRouter first.
2. GitHub App select private repos (no passwords). Create `Netie-AI/Cortex-Crew`.
3. Pay / raise https://github.com/organizations/Netie-AI/settings/billing
4. Write on OpenVault + constructor.
5. Wire contracts into product callers (PRD-001 in dms; PRD-002 `from netie.crew import bind_deep_agent, crew_harness_profile`).

## Later

Crew product repo. OpenVault HT1. AirGPT `rag/` vs corpus. Pointer vs UACC on HEAD. Palantir-class DMS after Space ACL callers.

C2/MIN_TESTS stand. Do not mint Cortex #42. Do not touch Cortex PRs #4 #41 #43 #44.

Do not clone `b-nnett/grok-bot-0.18-reconstructed`. Do not take account passwords.
