# CLAUDE.md - Pointer agent contract

Read this before any edit.

## Hard rules

1. Pointer is a plane-4 client. It does not plan. Cortex plans. A second orchestrator
   in this tree is a bug. Enforced by `tests/test_pointer.py` (gate refuses act when
   Cortex is down unless `source=local-test` or `allow_local_act` is explicit and
   appears in `degraded`).
2. Irreversible actions (`shell`, `file_write`, `file_delete`) require the approval
   token. `shell` is refused even with approval. Enforced by gate + engine tests.
3. File writes stay inside `.pointer-state/sandbox`. Enforced by
   `SandboxEngineTests`.
4. Bind is loopback unless `POINTER_ALLOW_REMOTE=1`. Remote act still needs the pair
   token and the approval token. Enforced by `server.main` and gate tests.
5. Kill switch file `.pointer-state/KILL` refuses every intent. Enforced by
   `test_kill_switch_refuses`.
6. Laptop-ASCII in CLI JSON and docs. Nothing enforces this yet (wish).
