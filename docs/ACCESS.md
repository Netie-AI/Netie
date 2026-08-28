# How this agent gets product remotes (no passwords)

Do not paste GitHub, email, or 2FA secrets into chat. NETIE.md forbids credential intercept. A password in this thread is a leak.

This cloud environment currently has **only** `github.com/Netie-AI/Netie` in the Cursor env list. Cortex and dms went public 2026-08-28 (HTTP 200, cloneable); **push** is still 403. OpenVault and constructor clone as public; **push** is 403. AirGPT, Pointer, Space, Control, Netie-KB, and Cortex-Crew return 404.

Re-probed 2026-08-28: Cortex HEAD `bf4ecee`, dms HEAD `3f9a9be`. OpenVault `main` still `62bb1c7` (GitHub CI success). constructor `landing-9-first-path` `4896ddd` (pages.yml success, no unit-test workflow on HEAD; constructor patches refreshed for this tip). Do not `uv add` Netie.git into Cortex (package name `netie` is the CortexOS alias). dms may `uv add git+https://github.com/Netie-AI/Netie.git`.

Local CI is the gate until GitHub Actions billing works:

```
make ci
```

That is `python3 -m compileall -q scripts netie` then `python3 scripts/check_docs.py` (required files + laptop-ASCII + all `scripts/test_*.py`). GitHub `docs-ci` jobs fail in ~3s without starting: spending limit. Empty steps, no logs. That is not a test failure. Origin (git remote) is already `origin`; we already push there. Switching hosts does not fix clone 404 or Actions billing. Product callers: `uv add git+https://github.com/Netie-AI/Netie.git` (wheel ships `netie._contracts`; `--editable` is optional).

Measured on this VM 2026-08-28 against public clones: Netie unittest via `make ci`; constructor (26 patches) `node --test` **62 passed**; OpenVault OpenMW (28 patches) routing+chat+crew-gate pytest **145 passed** plus ship-claim **4 passed** plus crew-netie **4 passed** (sibling `make ci` runs them). Cortex constitution path tests **3 passed** after `cortex-netie-path.patch` (stdlib; tool_runner bash test needs the Cortex suite). dms `netie_acl` module is stdlib plus optional `netie.dms`. Pointer/Space/KB/Crew/AirGPT still 404.

---

## 1. Grant clone access (GitHub App, not a password)

1. Open GitHub while logged in as the org owner (the avatar is your username; you do not type a password here).
2. Org app access: `https://github.com/organizations/Netie-AI/settings/installations` -> **Cursor** -> Repository access -> **select**:
   - `Netie-AI/Cortex`
   - `Netie-AI/dms`
   - `Netie-AI/Pointer`
   - `Netie-AI/Space`
   - `Netie-AI/netie-control`
   - `Netie-AI/Netie-KB`
3. Create empty `Netie-AI/Cortex-Crew` (do not clone OpenWork or Grok Bot). Then add that repo to the same App list. `uv add git+https://github.com/Netie-AI/Netie.git` then `from netie.crew import bind_deep_agent, crew_harness_profile, TokenBudget, dispatch_seat`. `uv add deepagents`.
4. AirGPT: if it still lives at `jian-hong/AirGPT`, either transfer it into `Netie-AI` or install the Cursor GitHub App on the `jian-hong` account and grant that repo. Do not paste that account password here.
5. Cursor environment: `https://cursor.com/dashboard/cloud-agents/environments/e/eb1a4238-9fe4-11f1-b532-320a589b8025` -> add the same repo URLs. The next Cloud Agent then gets them in its GitHub token. After clone: `python scripts/netie_init.py .` stamps `uv add git+https://github.com/Netie-AI/Netie.git` and the product's `from netie.*` import.
6. Do **not** add `b-nnett/grok-bot-0.18-reconstructed`.

A fine-grained PAT is a fallback if the App UI is stuck: GitHub -> Settings -> Developer settings -> Fine-grained tokens -> Contents read on those repos. Store it in the Cursor environment secrets UI, not in chat.

---

## 2. GitHub Actions billing (Netie docs-ci)

Jobs never start. Annotation: account payments failed or spending limit.

Pay or raise the limit: `https://github.com/organizations/Netie-AI/settings/billing`

Until that is green, **local** `python3 scripts/check_docs.py` (or `make ci`) is the estate gate. Commit `afb773b` GitHub check is the same billing annotation, not a test failure. OpenVault `main` CI is already green. Constructor has green `pages.yml` and no unit-test workflow on HEAD.

---

## 3. Write access for sibling patches

`cursor[bot]` cannot push to OpenVault, constructor, Cortex, or dms. On a machine that can, apply patches in the order listed in `docs/patches/README.md` (routing stack then constructor, then `cortex-netie-path.patch` on Cortex `main`, then `dms-netie-acl.patch` on dms `main`). Do not skip hop-walk / hop-failover / hop-park / hop-stream / hop-relay / hop-trace / hop-usage / hop-persist / hop-anthropic / hop-scope / hop-serve / hop-bound / hop-catalog / openvault-quota-share / openvault-hop-strip / openvault-hop-sidecar / openvault-ship-netie / openvault-crew-netie or constructor-ir-refuse / constructor-ir-ids / constructor-ghost-refuse / constructor-ir-emit / constructor-tool-action / constructor-inspect-action / constructor-inspect-object / constructor-inspect-tier / constructor-chat-object / constructor-topo-leftover / constructor-ir-entry / constructor-ir-output / constructor-ir-object / constructor-ir-bind / constructor-ir-action-allow / constructor-ir-intake / constructor-ir-hitl / constructor-ir-connected / constructor-ir-note / constructor-ir-cortex-post / constructor-object-pick / constructor-engine-order / constructor-ir-post / constructor-ir-kahn-nodes; later patches assume them.

Or add write permission for the Cursor GitHub App on those public repos (Cortex and dms now clone; they still need Contents write).

---

## 4. What we will not do

- Accept account passwords, 2FA codes, or session cookies
- Intercept logins
- Vendor Grok Bot reconstructed
- License-strip or rebrand OmniRoute, OpenWork, Deep Agents, xyflow, Guacamole, UACC
