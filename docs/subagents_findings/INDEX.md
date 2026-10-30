# Subagent and session findings

One row per finding. Newest first. Each file states expected vs actual, repro, root-cause
class and the invariant it rests on. "R4 held" is a valid finding.

| Date | File | One line |
|---|---|---|
| 2026-10-22 | `2026-10-22-wave2-sessions.md` | Shape of the 8 wave 2 sessions; netie-memory row contradicts ov_memory.py; parent replay: 6 of 6 stage 2 trees match (crew-harness after a restated hash); freeroute-core gate fails 1 of 17 once go test runs |
| 2026-10-22 | `2026-10-22-crew-agent-stage2.md` (PR #54, branch `claude/stage2-crew-agent`) | crew-agent stage 2; replay matches |
| 2026-10-22 | `2026-10-22-control-stage2.md` (PR #53, branch `claude/stage2-control`) | control stage 2; replay matches |
| 2026-10-22 | `2026-10-22-freeide-ext-stage2.md` (PR #52, branch `claude/stage2-freeide-ext`) | freeide-ext stays stage 1: bun install and test denied in its sessions |
| 2026-10-22 | `2026-10-22-crew-edge-stage2.md` (PR #51, branch `claude/stage2-crew-edge`) | crew-edge stage 2 plus a stage 3 increment; replay matches |
| 2026-10-22 | `2026-10-22-crew-harness-stage2.md` (PR #50, branch `claude/stage2-crew-harness`) | crew-harness stage 2; patch recut, finding restated both cut hashes in 7035d25, replay matches |
| 2026-10-22 | `2026-10-22-freebuild-stage2.md` (PR #49, branch `claude/stage2-freebuild`) | freebuild stage 2; replay matches |
| 2026-10-22 | `2026-10-22-netie-wiki-stage2.md` (PR #48, branch `claude/stage2-netie-wiki`) | netie-wiki stage 2; replay matches |
| 2026-10-22 | `2026-10-22-freeroute-core-stage2.md` (PR #47, branch `claude/stage2-freeroute-core`) | freeroute-core stays stage 1; parent run: 1 gate case fails, 1 package red |
| 2026-10-05 | `2026-10-05-airgpt-stage2.md` | AirGPT (LibreChat) to stage 2: one endpoint, OpenVault /v1, memory off and labeled ungoverned, gate test red on baseline and green after, 0002 patch replays |
| 2026-10-05 | `2026-10-05-wave1-sessions.md` | Shape and reasons for the 3 stage 2 sessions |
| 2026-10-05 | `2026-10-05-ecosystem-lane.md` | 5 named projects are not forkable for sale; sibling patch gate is red on base; 4 tool bugs found only on real upstream trees |
