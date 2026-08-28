# How this agent gets product remotes (no passwords)

Do not paste GitHub, email, or 2FA secrets into chat. NETIE.md forbids credential intercept. A password in this thread is a leak.

This cloud environment currently has **only** `github.com/Netie-AI/Netie`. Cortex, dms, AirGPT, Pointer, Space, Control, Netie-KB, and Cortex-Crew return 404 to the agent token. OpenVault and constructor clone as public; **push** is 403.

Re-probed 2026-08-28: same 404s (including `jian-hong/AirGPT`). OpenVault `main` still `62bb1c7` (GitHub CI success). constructor `landing-9-first-path` still `ee3a6cf` (pages.yml success, no unit-test workflow on HEAD).

Local CI is the gate until GitHub Actions billing works:

```
make ci
```

That is `python3 -m compileall -q scripts` then `python3 scripts/check_docs.py` (required files + laptop-ASCII + all `scripts/test_*.py`). GitHub `docs-ci` jobs fail in ~3s without starting: spending limit. Empty steps, no logs. That is not a test failure. Origin (git remote) is already `origin`; we already push there. Switching hosts does not fix clone 404 or Actions billing.

Measured on this VM 2026-08-28 against public clones: Netie unittest **233 passed**; constructor (14 patches) `node --test` **28 passed**; OpenVault OpenMW (23 patches) `uv run pytest tests -q --cov=openmw.openvault --cov-fail-under=75` **912 passed, 4 skipped**.

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
3. Create empty `Netie-AI/Cortex-Crew` (do not clone OpenWork or Grok Bot). Then add that repo to the same App list. Import `scripts/crew_*.py`. `uv add deepagents`.
4. AirGPT: if it still lives at `jian-hong/AirGPT`, either transfer it into `Netie-AI` or install the Cursor GitHub App on the `jian-hong` account and grant that repo. Do not paste that account password here.
5. Cursor environment: `https://cursor.com/dashboard/cloud-agents/environments/e/eb1a4238-9fe4-11f1-b532-320a589b8025` -> add the same repo URLs. The next Cloud Agent then gets them in its GitHub token.
6. Do **not** add `b-nnett/grok-bot-0.18-reconstructed`.

A fine-grained PAT is a fallback if the App UI is stuck: GitHub -> Settings -> Developer settings -> Fine-grained tokens -> Contents read on those repos. Store it in the Cursor environment secrets UI, not in chat.

---

## 2. GitHub Actions billing (Netie docs-ci)

Jobs never start. Annotation: account payments failed or spending limit.

Pay or raise the limit: `https://github.com/organizations/Netie-AI/settings/billing`

Until that is green, **local** `python3 scripts/check_docs.py` (or `make ci`) is the estate gate. Commit `afb773b` GitHub check is the same billing annotation, not a test failure. OpenVault `main` CI is already green. Constructor has green `pages.yml` and no unit-test workflow on HEAD.

---

## 3. Write access for sibling patches

`cursor[bot]` cannot push to OpenVault or constructor. On a machine that can, apply patches in the order listed in `docs/patches/README.md` (routing stack then constructor). Do not skip hop-walk / hop-failover / hop-park / hop-stream / hop-relay / hop-trace / hop-usage / hop-persist / hop-anthropic / hop-scope / hop-serve / hop-bound / hop-catalog or constructor-ir-refuse / constructor-ir-ids / constructor-ghost-refuse / constructor-ir-emit / constructor-tool-action / constructor-inspect-action / constructor-inspect-object / constructor-inspect-tier / constructor-chat-object / constructor-topo-leftover / constructor-ir-entry / constructor-ir-output; later patches assume them.

Or add write permission for the Cursor GitHub App on those two public repos.

---

## 4. What we will not do

- Accept account passwords, 2FA codes, or session cookies
- Intercept logins
- Vendor Grok Bot reconstructed
- License-strip or rebrand OmniRoute, OpenWork, Deep Agents, xyflow, Guacamole, UACC
