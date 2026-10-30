# GitHub secrets runbook

Token file (local, never commit): `D:\NetieSecrets\GITHUB_SECRETS.md`

## Why not org secrets
Organization secrets cannot be used by private repositories on the current GitHub plan.
Use **per-repo secrets** until plan upgrade or until cortex-contract is a published wheel (Cortex EPIC-002 / issue #5).

## Required today
| Repo | Secret name | Purpose |
|------|-------------|---------|
| Netie-AI/dms | CORTEX_CONTRACT_TOKEN | private checkout of Cortex to build cortex-contract in CI |

## Set without echoing
```powershell
(Get-Content D:\NetieSecrets\GITHUB_SECRETS.md -Raw).Trim() |
  gh secret set CORTEX_CONTRACT_TOKEN --repo Netie-AI/dms
```

## PAT that works
Classic PAT with `repo` scope that can see `Netie-AI/Cortex`.
Fine-grained: resource owner `Netie-AI`, repo `Cortex` selected, Contents Read, org-owner approval if policy on.

## Rotate
If a chat or log ever printed the token, rotate it and re-run the set command.
