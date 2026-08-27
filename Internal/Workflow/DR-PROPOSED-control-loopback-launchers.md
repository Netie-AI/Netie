# DR-PROPOSED - Control loopback launchers (P-CTL-2 unlock)

**Status:** proposed. Not law. Binds only when filed as a PR against this file
and merged by the founder (DOCUMENT_SYSTEM Tier 5). Until then, launchers stay
rendered no-ops (`PARKING_LOT.md` P-CTL-2).

**Repo:** Netie constitution + Control (`E:\NetieControl`, not `E:\Netie-Control`)
**Why:** PRD success says WHEN the operator launches a local CLI lane, Control
shall not write a customer system except via a Cortex action type. Today the
three rows render and click does nothing because DR-0004 Option A has no auth:
a wired POST on a reachable port is RCE. Measured 2026-08-27: Control listens
**only** on `127.0.0.1:8040`. That is the loopback SOW P-CTL-2 named.

## Decision (if accepted)

1. Control may execute **only** the argv tuples already declared in
   `netie_control/sources.py` `LAUNCHERS` (estate-gate, kb-search,
   dms-demo-verify). No extra binaries. No shell strings.
2. Bind stays `127.0.0.1`. Refuse the run if the peer is not loopback.
   Publishing `:8040` on all interfaces undoes this DR.
3. Cwd must exist. On this laptop `D:\DMS` / `D:\Netie-KB` may be absent;
   resolve to `E:\` twins or refuse with the missing path named (R-0011).
4. Do not start, stop, or focus Grok Bot, Cursor, Pointer, or any desktop
   app (R-0015). Those are not launchers.
5. `/v1/run` stays **405** (customer write). Launcher POST is a different
   path, local CLI only, allowlisted.
6. TAS-CONTROL.md still describes paperclip `:3100`. On accept, amend TAS
   to the Python slice at `E:\NetieControl` `:8040`. That amendment is not
   this DR's merge (founder TAS card in ECOSYSTEM_EXECUTION_PLAN).

## Does not do

Does not invent a principal. Does not un-405 `/v1/goal` `/v1/secrets`
`/v1/route`. Does not seat a second writer on `E:\NetieControl` while
netie-controlagent is dirty. Does not clone `E:\Netie-Control`.

## Implementation note (for the seated Control writer only)

After merge: POST that execs the named argv, timeout, capture stdout/stderr,
never a 200 with empty body on failure. Test: 127.0.0.1 allowed; a spoofed
non-loopback refused; unknown name 404; `/v1/run` still 405.
