# How this agent gets product remotes (no passwords)

Do not paste GitHub, email, or 2FA secrets into chat. NETIE.md forbids credential intercept. A password in this thread is a leak.

This cloud environment currently has **only** `github.com/Netie-AI/Netie` in the Cursor env list. Public clones (HTTP 200) with **push** still 403: Cortex, dms, OpenVault, constructor, Pointer, netie-control, Netie-KB. AirGPT, Space, and Cortex-Crew return 404.

Re-probed 2026-09-02: Cortex HEAD `bf4ecee`, dms HEAD `3f9a9be`, Pointer HEAD `8c0e6c2`, netie-control HEAD `82ab1ae`, Netie-KB HEAD `10356e5` (`kb.py validate` OK, 58 artifacts). OpenVault `main` still `62bb1c7` (GitHub CI success). constructor `landing-9-first-path` `4896ddd` (pages.yml success, no unit-test workflow on HEAD). Do not `uv add` Netie.git into Cortex (package name `netie` is the CortexOS alias). dms / Pointer / netie-control may `uv add git+https://github.com/Netie-AI/Netie.git`.

`Keys.txt` is untracked. Curl samples use `$OPENROUTER_API_KEY`. Founder must revoke leaked keys (section 5). History still has blobs until a founder rewrite.

Local CI is the same gate GitHub `docs-ci` runs:

```
make ci
```

That is `python3 -m compileall -q scripts netie` then `python3 scripts/check_docs.py` (required files + laptop-ASCII + all `scripts/test_*.py`). GitHub `docs-ci` on `main` is green (measured 2026-09-02: `d87abd4` and the ship/ticket/batch/wrap commits before it, 2 checks). Older 1-5s red X jobs were org billing; those are not a code ticket. Pay or raise: `https://github.com/organizations/Netie-AI/settings/billing`. Origin (git remote) is already `origin`; we already push there. Switching hosts does not fix clone 404. Product callers: `uv add git+https://github.com/Netie-AI/Netie.git` (wheel ships `netie._contracts`; `--editable` is optional).

Measured on this VM 2026-09-02 against public clones: Netie unittest via `make ci`; constructor (26 patches) `node --test` **62 passed**; OpenVault OpenMW (28 patches + free-pool) routing+chat+crew-gate pytest plus ship-claim plus crew-netie plus free-pool (sibling `make ci` runs them). Cortex constitution path tests after `cortex-netie-path.patch` (stdlib). `cortex-web-via-runner.patch` broker skip is a file-read assert (no pytest). dms `netie_acl` module is stdlib plus optional `netie.dms`; `dms-demo-acl-resolve.patch` makes `demo_acl` return `resolve_session_acl`. Pointer `netie-hands.test.js` **6 passed** after `pointer-netie-hands.patch`; additive `pointer-observe-guard.patch` (`netie-observe.test.js` **5 passed**; `uacc.test.js` still **16 passed**; native observe unchanged). Founder apply-all: `python3 scripts/apply_product_patches.py`. Control `test_netie_board.py` + plane-4 **51 passed** after `control-netie-board.patch` (needs fastapi). Netie-KB `kb.py validate` OK (58 artifacts); `kb-netie-index.patch` skill show is ids-only. AirGPT/Space/Crew still 404.

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
3. Create empty `Netie-AI/Cortex-Crew` (do not clone OpenWork or Grok Bot). Then add that repo to the same App list. `uv add git+https://github.com/Netie-AI/Netie.git` then `from netie.crew import bind_deep_agent, crew_harness_profile, TokenBudget, dispatch_seat, register_from_kb, register_index`. `uv add deepagents`.
4. AirGPT: if it still lives at `jian-hong/AirGPT`, either transfer it into `Netie-AI` or install the Cursor GitHub App on the `jian-hong` account and grant that repo. Do not paste that account password here.
5. Cursor environment: `https://cursor.com/dashboard/cloud-agents/environments/e/eb1a4238-9fe4-11f1-b532-320a589b8025` -> add the same repo URLs. The next Cloud Agent then gets them in its GitHub token. After clone: `python scripts/netie_init.py .` stamps `uv add git+https://github.com/Netie-AI/Netie.git` and the product's `from netie.*` import.
6. Do **not** add `b-nnett/grok-bot-0.18-reconstructed`.

A fine-grained PAT is a fallback if the App UI is stuck: GitHub -> Settings -> Developer settings -> Fine-grained tokens -> Contents read on those repos. Store it in the Cursor environment secrets UI, not in chat.

---

## 2. GitHub Actions (Netie docs-ci)

`docs-ci` on `main` now runs for real and is green (measured 2026-09-02, 2 checks). Local `make ci` is the same command and is still the merge gate this agent runs.

Older 1-5s red X jobs were org billing. Do not treat those as a code ticket. Pay or raise: `https://github.com/organizations/Netie-AI/settings/billing`

OpenVault `main` CI is already green. Constructor has green `pages.yml` and no unit-test workflow on HEAD.

---

## 3. Write access for sibling patches

`cursor[bot]` cannot push to OpenVault, constructor, Cortex, dms, Pointer, or netie-control. On a machine that can, apply patches in the order listed in `docs/patches/README.md` (routing stack then constructor, then `cortex-netie-path.patch` then `cortex-web-via-runner.patch` then `cortex-role-execute.patch` on Cortex `main`, then `dms-netie-acl.patch` then `dms-demo-acl-resolve.patch` on dms `main`, then `pointer-netie-hands.patch` on Pointer `main`, then `control-netie-board.patch` on netie-control `main`). Do not skip hop-walk / hop-failover / hop-park / hop-stream / hop-relay / hop-trace / hop-usage / hop-persist / hop-anthropic / hop-scope / hop-serve / hop-bound / hop-catalog / openvault-quota-share / openvault-hop-strip / openvault-hop-sidecar / openvault-ship-netie / openvault-crew-netie / openvault-free-pool / openvault-free-pool-route / openvault-ship-claim-ov or constructor-ir-refuse / constructor-ir-ids / constructor-ghost-refuse / constructor-ir-emit / constructor-tool-action / constructor-inspect-action / constructor-inspect-object / constructor-inspect-tier / constructor-chat-object / constructor-topo-leftover / constructor-ir-entry / constructor-ir-output / constructor-ir-object / constructor-ir-bind / constructor-ir-action-allow / constructor-ir-intake / constructor-ir-hitl / constructor-ir-connected / constructor-ir-note / constructor-ir-cortex-post / constructor-object-pick / constructor-engine-order / constructor-ir-post / constructor-ir-kahn-nodes; later patches assume them. Do not mix `constructor-*-4896ddd.patch` with that 26-stack.

Or add write permission for the Cursor GitHub App on those public repos (Cortex, dms, Pointer, netie-control now clone; they still need Contents write).

---

## 4. What we will not do

- Accept account passwords, 2FA codes, or session cookies
- Intercept logins
- Vendor Grok Bot reconstructed
- License-strip or rebrand OmniRoute, OpenWork, Deep Agents, xyflow, Guacamole, UACC
- Commit provider API keys. `Keys.txt` is gitignored. Curl samples use `$OPENROUTER_API_KEY`. `python3 scripts/secrets_scan.py` fails the local gate if a live `sk-or-v1-` / `csk-` / GitHub / Anthropic token is tracked.

## 5. Rotate keys leaked from this public repo (2026-08-28)

GitGuardian flagged an OpenRouter key in `Free APIs for OpenVault Free/`. That dump had live provider keys, in HEAD since 2026-08-02, on a **public** repo. Removing the files does not revoke them. Git history still has the old blobs until main is rewritten (founder-only, force-push).

Revoke and issue new keys, then store them only in OpenVault / env, never in git:

1. OpenRouter: https://openrouter.ai/workspaces/default/keys (the GitGuardian hit)
2. Cerebras, Mistral, Bytez, Ollama, Aion Labs, Kilo AI (same `Keys.txt` dump)
3. Confirm GitHub secret scanning / GitGuardian goes quiet after revoke. A still-open alert on historical commits is expected until history purge.

Do not paste the old or new values into chat, issues, or this file.
