# Adversarial source-trace review

- Date: 2026-08-23 UTC
- Model: GPT
- Scope: source-trace correctness, fixture, static proof page, safety claims
- Keywords: source trace, false Traced, shared formula, stale cache, circular reference, malformed xlsx, reproducible proof
- Main idea: Happy-path output passed, but multiple adversarial workbooks could produce a confident false `Traced`; deployment is blocked until the tool fails closed.

## Blocking findings

1. Circular formulas were accepted as traced. Replacing `SUM(C4:E4)` with `SUM(F4:F4)` made the tool use the target cell as an input and exit zero.
2. Formula inputs were trusted as cached values. Replacing C4 with a formula cache that disagreed with its formula made F4 report traced against the stale cache.
3. Lowercase references in a shared-formula master were not translated because the token matcher only handled uppercase references. A child shared formula could then resolve and trace the wrong row.
4. XML values such as `Infinity` were accepted as numbers. `Infinity` could produce `Traced`; `Infinity` and `-Infinity` could raise an uncaught `decimal.InvalidOperation`.

## Nonblocking findings

- Captured output in the static page omitted the final terminal newline, so it was visually but not byte-identical.
- The public command should use `python3`, which is available in this environment, instead of assuming `python`.

## Deployment condition

Do not deploy until:

- Self-references and input formulas are rejected rather than trusted.
- Shared-formula translation is case-insensitive.
- Non-finite numeric values are rejected cleanly.
- Regression tests cover all reported cases.
- The static page uses byte-identical captured output and `python3`.
