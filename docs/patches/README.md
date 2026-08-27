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

Replaces D:\ tree skips with tmp_path fixtures.
Measured on this VM 2026-08-27: detect_stacks 36 passed; full OpenMW 840 passed, 4 DPAPI skips.
