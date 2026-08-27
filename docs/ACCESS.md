# How this agent gets product remotes (no passwords)

Do not paste GitHub, email, or 2FA secrets into chat. NETIE.md forbids credential intercept. A password in this thread is a leak.

This cloud environment currently has **only** `github.com/Netie-AI/Netie`. Cortex, dms, AirGPT, Pointer, Space, Control, and Netie-KB return 404 to the agent token. OpenVault and constructor clone as public; **push** is 403.

Local CI is the gate until GitHub Actions billing works:

```
python3 scripts/check_docs.py
```

`make ci` is the same command. GitHub `docs-ci` jobs fail in ~3s without starting: spending limit. That is not a test failure. Origin (git remote) is already `origin`; we already push there. Switching hosts does not fix clone 404 or Actions billing.

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
3. AirGPT: if it still lives at `jian-hong/AirGPT`, either transfer it into `Netie-AI` or install the Cursor GitHub App on the `jian-hong` account and grant that repo. Do not paste that account password here.
4. Cursor environment: `https://cursor.com/dashboard/cloud-agents/environments/e/eb1a4238-9fe4-11f1-b532-320a589b8025` -> add the same repo URLs. The next Cloud Agent then gets them in its GitHub token.
5. Do **not** add `b-nnett/grok-bot-0.18-reconstructed`.

A fine-grained PAT is a fallback if the App UI is stuck: GitHub -> Settings -> Developer settings -> Fine-grained tokens -> Contents read on those repos. Store it in the Cursor environment secrets UI, not in chat.

---

## 2. GitHub Actions billing (Netie docs-ci)

Jobs never start. Annotation: account payments failed or spending limit.

Pay or raise the limit: `https://github.com/organizations/Netie-AI/settings/billing`

Until that is green, **local** `python3 scripts/check_docs.py` is the estate gate. OpenVault `main` CI is already green. Constructor has green `pages.yml` and no unit-test workflow on HEAD.

---

## 3. Write access for sibling patches

`cursor[bot]` cannot push to OpenVault or constructor. On a machine that can:

```
git apply docs/patches/openvault-detect-stacks.patch
git apply docs/patches/constructor-compiler-tests.patch
```

Or add write permission for the Cursor GitHub App on those two public repos.

---

## 4. What we will not do

- Accept account passwords, 2FA codes, or session cookies
- Intercept logins
- Vendor Grok Bot reconstructed
- License-strip or rebrand OmniRoute, OpenWork, Deep Agents, xyflow, Guacamole, UACC
