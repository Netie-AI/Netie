# STATUS

**Hard cap: 60 lines.** Older narrative moves to CHANGELOG.md.

## Now

1. Product repo `Netie-AI/Pointer` still 404 to this token. Bootstrap daemon is up on `127.0.0.1:7420` (`GET /health` 200). Cortex unreachable. OpenClaw/Hermes still missing; not installed here.
2. Windows type/hotkey/screenshot now coded (`pointer/windows_input.py`) and unit-tested (12 tests). Live Linux mouse 220,180 -> 400,300 after fixing `--sync` hang when already at target. This VM is not the founder laptop, so Windows SendInput is unproven on real hardware.
3. Stripe live `acct_1RMx9FFV5wcFod2f`: available MYR 0, pending MYR 0, charges listed 0. Sibling Number Trace SKUs remain the buyable path. Do not recreate them.

## Next

- Founder: `cd D:\Netie\Pointer; python -m pointer serve` then `python -m pointer pair --show` (tokens stay on the laptop).
- Payouts: upload `Ic.pdf` in Stripe Dashboard. Charges can land; Bank Islam cannot receive until identity clears.
- Competitions: Slingshot 2026 and IPHatch Asia 2026 are closed. Startup SG Tech needs a Singapore Pte Ltd with >=30% SC/PR shareholding - no such entity is in evidence.

## Later

- Clone product Pointer when the token can see `Netie-AI/Pointer` and replace this bootstrap with a contract test against that API.
- OCR `verify.expect_contains` (currently fail-closed).
- Authorized bug bounty only after Stripe `payouts_enabled=true`. $1M/month is not in evidence.
