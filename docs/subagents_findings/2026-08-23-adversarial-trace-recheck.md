# Adversarial source-trace recheck

- Date: 2026-08-23 UTC
- Model: GPT
- Scope: regression verification after fail-closed fixes
- Keywords: source trace, adversarial verification, fail-closed, shared formula, stale cache, non-finite xlsx
- Main idea: All prior false-trace paths now fail closed, and the static proof page matches generated output exactly.

## Verified results

- Circular self-reference: refused with exit code 2.
- Formula-valued input with a stale cache: refused with exit code 2.
- Lowercase shared formula: translated to the child row correctly; a stale cache then refused.
- Non-finite XML values: refused without a traceback.
- Static page uses `python3` and its output blocks include final terminal newlines.
- Full local suite: 12 of 12 behavior gates passed.

Deployment recommendation: `SAFE TO DEPLOY`.
