# Patches for sibling repos this token cannot push (403)

Apply on a machine with write access. Do not vendor OpenWork or Grok Bot.

## Constructor (`Netie-AI/constructor`)

From the constructor repo root, on `landing-9-first-path`:

```
git apply docs/patches/constructor-compiler-tests.patch
node --test tests/compiler.test.cjs
```

Adds `rankForKinds`, node `--test` for Cortex IR, and `.github/workflows/test.yml`.
Measured on this VM 2026-08-27: 3 passed.

## OpenVault (`Netie-AI/OpenVault`)

From the OpenVault repo root, on `main`:

```
git apply docs/patches/openvault-detect-stacks.patch
cd OpenMW && uv run pytest tests/test_detect_stacks.py -q
```

Also:

```
git apply docs/patches/openvault-strict-random.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py -q
```

Adds `strict-random` (9th of 19 OmniRoute user-facing strategies). Algorithm port + remainder shuffle. Measured on this VM 2026-08-27: 9 passed. Push 403.
