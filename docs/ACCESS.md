# How this agent gets product remotes (no passwords)

Do not paste GitHub, email, or 2FA secrets into chat. NETIE.md forbids credential intercept. A password in this thread is a leak.

This cloud environment currently clones public `Netie-AI/{Netie,Cortex,OpenVault,constructor,Pointer,dms,netie-control,Netie-KB}`. **Push** to OpenVault and constructor is 403. **Still 404:** Cortex-Crew, Space, AirGPT (`jian-hong/AirGPT` also 404 to this token).

Re-probed 2026-08-28: Cortex `bf4ecee` / Pointer `8c0e6c2` / dms `3f9a9be` / control / KB / constructor `landing-9-first-path` `4896ddd` / OpenVault `62bb1c7` clone. Cortex-Crew still missing. OpenVault `main` CI success. constructor pages.yml success; public HEAD still has no `tests/compiler.test.cjs` until patches land. Netie 12 patches that fit `4896ddd`: **29** compiler tests. The 26-patch / 62-pass stack was refreshed for unpushed `eebff20` and does not apply (`inspect-object` fails).

Local CI is the gate until GitHub Actions billing works:

```
make ci
```

That is `python3 -m compileall -q scripts netie` then `python3 scripts/check_docs.py` (required files + laptop-ASCII + all `scripts/test_*.py`). GitHub `docs-ci` jobs fail in ~3s without starting: spending limit. Empty steps, no logs. That is not a test failure. Origin (git remote) is already `origin`; we already push there. Switching hosts does not fix clone 404 or Actions billing. Product callers: `uv add git+https://github.com/Netie-AI/Netie.git` (wheel ships `netie._contracts`; `--editable` is optional).

Measured on this VM 2026-08-28 against public clones: constructor `4896ddd` (12 patches) `node --test` **29 passed**; OpenVault OpenMW (29 patches) routing+chat+crew-gate+free-pool pytest via sibling gate. Prior full OpenMW suite on 23 patches was **912 passed, 4 skipped**. Cortex/Pointer/dms/control/KB clone. AirGPT / Space / Cortex-Crew still 404.

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

`cursor[bot]` cannot push to OpenVault or constructor. On a machine that can, apply patches in the order listed in `docs/patches/README.md`. Constructor public HEAD is `4896ddd`: stop after `constructor-ir-4896ddd.patch` (29 passed). Do not apply `inspect-object` onward on that SHA. OpenVault: do not skip hop-walk through `openvault-free-pool.patch`. Later eebff20 patches assume inspect-object.

Or add write permission for the Cursor GitHub App on those two public repos.

---

## 4. What we will not do

- Accept account passwords, 2FA codes, or session cookies
- Intercept logins
- Vendor Grok Bot reconstructed
- License-strip or rebrand OmniRoute, OpenWork, Deep Agents, xyflow, Guacamole, UACC
- Commit provider API keys. `Keys.txt` is gitignored. Curl samples use `$OPENROUTER_API_KEY`. `python3 scripts/secrets_scan.py` fails the local gate if a live `sk-or-v1-` / `csk-` / GitHub / Anthropic token is tracked.

## 5. Rotate keys leaked from this public repo (2026-08-28)

GitGuardian flagged an OpenRouter key in `Free APIs for OpenVault Free/`. That file was a dump of **seven** live keys, in HEAD since 2026-08-02, on a **public** repo. Removing the files does not revoke them. Git history still has the old blobs until main is rewritten (founder-only, force-push).

Revoke and issue new keys, then store them only in OpenVault / env, never in git:

1. OpenRouter: https://openrouter.ai/workspaces/default/keys (the GitGuardian hit)
2. Cerebras, Mistral, Bytez, Ollama, Aion Labs, Kilo AI (same `Keys.txt` dump)
3. Confirm GitHub secret scanning / GitGuardian goes quiet after revoke. A still-open alert on historical commits is expected until history purge.

Do not paste the old or new values into chat, issues, or this file.
