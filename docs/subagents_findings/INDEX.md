# Subagent and session findings

One row per finding. Newest first. Each file states expected vs actual, repro, root-cause
class and the invariant it rests on. "R4 held" is a valid finding.

| Date | File | One line |
|---|---|---|
| 2026-10-05 | `2026-10-05-freeroute-stage2.md` | OmniRoute fork: 42 providers gated off by default (9 subscription-login, 33 web-session), proved on the /v1/models artifact; full Next build OOMs here, stage stays 1 |
| 2026-10-05 | `2026-10-05-wave1-sessions.md` | Shape and reasons for the 3 stage 2 sessions |
| 2026-10-05 | `2026-10-05-ecosystem-lane.md` | 5 named projects are not forkable for sale; sibling patch gate is red on base; 4 tool bugs found only on real upstream trees |
