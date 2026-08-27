# Patches for sibling repos this token cannot push (403)

Apply on a machine with write access. Do not vendor OpenWork or Grok Bot.

## Constructor (`Netie-AI/constructor`)

From the constructor repo root, on `landing-9-first-path`:

```
git apply docs/patches/constructor-compiler-tests.patch
git apply docs/patches/constructor-empty-graph.patch
node --test tests/compiler.test.cjs
```

Adds `rankForKinds`, empty-graph IR (no invented Cortex nodes), node `--test`, and `.github/workflows/test.yml`.
Measured on this VM 2026-08-27: 6 passed.

## OpenVault (`Netie-AI/OpenVault`)

From the OpenVault repo root, on `main`:

```
git apply docs/patches/openvault-detect-stacks.patch
cd OpenMW && uv run pytest tests/test_detect_stacks.py -q
```

Also, in this order (lkgp edits StrategyName after strict-random):

```
git apply docs/patches/openvault-strict-random.patch
git apply docs/patches/openvault-lkgp.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py -q
```

Adds `strict-random` (9th) then `lkgp` (10th of 19 OmniRoute user-facing strategies). LKGP stickies the last *successful* `execution_key` and clears that pin on a later failure of the same key. Not OmniRoute SQLite provider+connection.

Then:

```
git apply docs/patches/openvault-context-headroom.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py -q
```

Adds `context-optimized` (11th: largest known `context_window` first; no model catalog) and `headroom` (12th: `1 - max(util_5h, util_7d)`; missing util = full headroom; no provider quota fetch).

Then:

```
git apply docs/patches/openvault-reset-window.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py -q
```

Adds `reset-window` (13th: soonest `reset_remaining_ms` first; unknown last; no quota fetch; tie-band rotation not ported).

Then:

```
git apply docs/patches/openvault-reset-aware.patch
cd OpenMW && uv run pytest tests/test_route_strategies.py -q
```

Adds `reset-aware` (14th: session/weekly remaining mixed with reset-pressure; missing reset remaining => urgency 0, remaining-only; OmniRoute uses 0.5 there; `limit_reached` last). Measured on this VM 2026-08-27: 20 passed. Push 403.

Independent of routing:

```
git apply docs/patches/openvault-crew-gate.patch
cd OpenMW && uv run pytest tests/test_crew_gate.py tests/test_contract.py -q
```

Adds `POST /api/crew/gate`: location + allowed, never a skill body. Unknown kinds (including `skill` until a registry row exists) refuse. This is not OpenVault PR #44 (that RFC also adds Netie-KB signposts). Measured 2026-08-27: 17 passed with contract tests.
