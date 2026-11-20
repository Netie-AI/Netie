# 2026-11-20 - OpenVault re-cut 2: one crew-gate route

Lane 1 of 5 of the re-cut wave on PR #59. Preflight: KB `D:\Netie-KB` absent in this cloud
box. `2026-11-12-sibling-recut.md` F3 was the hit (OpenVault: 2 sibling tests fail, duplicate
`POST /api/crew/gate`). PREFLIGHT: HIT.

Shape: one session, no subagents, Fable for all steps. Pin `3ba51cd`, not moved. OpenVault
live `main` was the same commit as the pin when cloned on 2026-11-20, so nothing upstream
has moved under this cut.

Outcome: re-cut, not a stop memo. Ours only lowers verdicts that OpenVault's route gives.
No assertion in either suite contradicts the other. One product question is left open and
is written as a memo below (D1). I did not pick it; the re-cut keeps the behaviour the three
patches already had and already documented.

## Route comparison (measured on the pin, `TestClient`, empty vault)

"Theirs" is OpenVault PR #44's `crew_gate` in `OpenMW/openmw/openvault/app.py`. "Old ours"
is the route `openvault-crew-gate.patch` registered before it (first match wins, so theirs
never ran). "Re-cut" is theirs after the three patches.

| Question | Theirs (#44) | Old ours (shadow) | Re-cut |
|---|---|---|---|
| Who may call | No auth on the route. Same middleware as every `/api` route | Same | Same, untouched |
| Kinds accepted | `AccessKind` literal: memory, api, component, runtime, model, service, skill, mcp. Other kind is 422 | `kind: str`. Other kind is 200 `allowed: false` | Theirs: 422 |
| Intent | `AccessIntent` literal. Other intent is 422 | `str`. Other intent is 200 `allowed: false` | Theirs: 422 |
| Defaults | Empty body means `skill` / `netie-kb.skills` / `invoke` | `kind` and `id` required | Theirs |
| `skill_body`, `prompt`, `instructions`, `transcript` in the request | Not a field. Dropped. Answers as if not sent (`service` + `skill_body` is `allowed: true`) | 200 `allowed: false`, `found: false` | 200 `allowed: false`, reason first. Signpost kept |
| `kind=skill`, `id=netie-kb.skills`, no `skill_ids` | `found: true`, owner `netie-kb`, `allowed: true` | `found: false`, `allowed: false` | `found: true`, owner `netie-kb`, `allowed: false` |
| `kind=mcp`, `id=netie-kb.mcp` | `found: true`, `allowed: true` | `allowed: false` | `found: true`, `allowed: false` |
| `kind=skill` with `skill_ids` that include the id | `skill_ids` dropped. Resolver decides | Check passes, resolver decides | Check passes, resolver decides |
| `kind=skill`, `id=S-0004`, `skill_ids=[S-0004]` | `found: false`, `allowed: false` (no such row) | Same | Same |
| `kind=service` and the other five kinds | Resolver verdict (`resolve_access` + `check_gate`) | Same call | Resolver verdict, unchanged |
| ids-only | Response never has a body (asserted by their test). Request is not checked | Request and response checked | Request checked, response is theirs |
| What it records | `log.info("crew_gate")`: kind, resource, intent, parent_run_id, child_id, deficit, allowed, reasons | No intent, no deficit. Nothing on the unknown-intent path | Theirs, with the final `allowed` and reasons |
| Echo | `parent_run_id`, `child_id`, `deficit` | `deficit` missing on refusals | Theirs |

Direction: the set of requests the re-cut allows is a subset of what theirs allows. It never
raises a verdict (`payload["allowed"]` is only ever set to `False`). It adds one refusal
theirs does not have (a body in the request) and lowers two that theirs allows (`skill`
without ids, `mcp`).

## F1. A patch registered a route the sibling already owned

- **Expected:** a patch changes OpenVault's `POST /api/crew/gate`; OpenVault's own suite
  stays green.
- **Actual:** the old cut registered a second `POST /api/crew/gate` earlier in `create_app`.
  FastAPI served ours and #44's never ran. Full OpenMW suite: 1611 passed, 2 failed
  (`tests/test_access_routing.py::test_crew_gate_is_resolve_plus_audit`,
  `::test_no_route_path_is_registered_twice`). The old cut also added a second
  `("POST", "/api/crew/gate")` row to OpenVault's `tests/test_contract.py`.
- **Repro:** fresh clone at the pin, apply the 32 patches from `dbaaaa5` in stack order,
  `cd OpenMW && uv run --with-editable <Netie> pytest -q`.
- **Fix:** the three crew patches now edit #44's route. `crew-gate`: body keys on the model,
  refusal lowers `allowed`, no second decorator, no `test_contract.py` hunk. `crew-netie`:
  the inline rule becomes `check_crew_gate`. `crew-skill-ids`: `skill_ids` field and
  argument. Each patch keeps its old tests byte for byte and adds route tests (4, 1, 1).
  Result: 1619 passed, 0 failed.
- **Root-cause class:** a patch cut against an old base, re-cut to "applies" and not to
  "what does the base already do". Same class as F3 of 2026-11-12.
- **Invariant:** assert the artifact the sibling actually receives. Fix the class, not the
  symptom: `tests/test_crew_gate.py::test_gate_is_one_route_not_a_shadow` now ships in the
  patch.

## F2. This repo's gate still cannot see that failure

- **Expected:** the gate goes red when a patch breaks the sibling route it edits.
- **Actual:** `test_openvault_patches_apply_on_main` runs 10 named test files. The two tests
  that caught F1 live in `tests/test_access_routing.py`, which is not one of them. The gate
  was green on the old cut and is green on the new one.
- **Repro:** read the pytest argument list in the gate method.
- **Not fixed here:** my brief allows a `scripts/` edit only where the re-cut makes a line
  obsolete. None is. Proposed for the parent: add `tests/test_access_routing.py` to the
  pytest list in the gate method and in the `openvault` entry of
  `scripts/apply_product_patches.py`. Measured: that file has 2 failures on the old cut and
  0 on the new one, so the addition can fail. `min_passed` 90 can stay.
- **Root-cause class:** gate scope narrower than the claim read into it.
- **Invariant:** prove a gate can fail before trusting it green.

## F3. Stale contract text outside this lane (noted, not edited)

- **Expected:** docs match the code.
- **Actual:** `scripts/crew_ov_gate.py` says of the crew-gate patch and PR #44 "neither is
  on OpenVault main yet", and "Same set as OpenVault ACCESS_KINDS" over a six-kind set.
  #44 is on the pin and `ACCESS_KINDS` has eight kinds (`skill`, `mcp` added). The module
  docstring of `scripts/test_sibling_patches.py` is still correct.
- **Repro:** `grep -n "ACCESS_KINDS = " -A10 OpenMW/openmw/openvault/route/access.py` on
  the pin.
- **Root-cause class:** a comment that asserts a sibling's state with no test under it.
- **Invariant:** say what is measured and what is assumed.

## F4. Two other OpenVault patches edit OpenVault tests (noted, not changed)

Acceptance 3 holds for the three crew patches: they only add `tests/test_crew_gate.py` and
`tests/test_crew_netie_gate.py`. Across the other 29, measured with `git apply --numstat`:

- `openvault-detect-stacks.patch` rewrites three tests in `tests/test_detect_stacks.py`
  (47 added, 21 removed). They were skipped off Windows (`D:\Cortex`,
  `D:\OpenVault\vendor\openship`); the patch makes them `tmp_path` fixtures. That is the
  patch's purpose and it removes skips, but it is an edit to a sibling test.
- `openvault-execution-shapes.patch` changes one import line in
  `tests/test_route_strategies.py` (adds `StrategyNotASort`).
- The rest only append tests.

None of the 29 changed in this cut.

## D1. Decision memo: who says yes to `skill` and `mcp` at the gate

Not picked. The re-cut keeps what the patches did before.

- **Behaviour A (OpenVault #44):** `kind=skill id=netie-kb.skills` and `kind=mcp
  id=netie-kb.mcp` are registry rows. The gate answers `allowed: true` (subject to
  `check_gate`). An empty POST body means exactly that ask. Skill ids never reach OpenVault.
- **Behaviour B (Netie `refuse_crew_gate`, these patches):** `skill` is allowed only when the
  POST carries ids-only `skill_ids` that include `id`. `mcp` has no path at all: it is not in
  Netie's `REGISTERED_KINDS`.
- **Evidence:** the table above. Their test asserts `found` and `owner` for the skill ask,
  not `allowed`. Our test asserts `allowed is not True` for the same ask. Both pass on the
  re-cut, so no test decides it. The patch said "skill refuses until a registry row exists";
  #44 added that row, and `scripts/crew_ov_gate.py` did not follow.
- **Consequence today:** after the patches a Cortex crew that sends #44's default ask gets
  `allowed: false`. With `id=netie-kb.skills` and `skill_ids=["netie-kb.skills"]` it gets the
  resolver verdict. A real skill id (`S-0004`) is `found: false` either way: OpenVault holds a
  signpost, not skill rows. `mcp` cannot be allowed.
- **Options:** (1) keep B (this cut). (2) Accept A for the two signpost ids: add `skill` and
  `mcp` to Netie's registered kinds when `id` is the Netie-KB signpost; needs a change to
  `scripts/crew_ov_gate.py` and its tests, outside this lane. (3) Keep B for `skill`, give
  `mcp` an ids path (`mcp_ids`) so it is not a dead kind.
- **Recommendation:** (2) or (3) need a founder call on whether the signpost row counts as
  "registered". My read: the dead `mcp` kind is the part most likely to block real work.

## Spend caps (asked: confirm or refute, do not fix)

Confirmed. `_run_execution_shape` in `vault/proxy.py` takes no `spend` argument and both
call sites return before `_walk_plan` / `_admit_hop`, so fusion / pipeline / context-relay
posts are never admitted against the #154 caps (0 references to `spend` in the function).
Its `post` closure calls `vault.get_secret(rec.id)` directly, not `_secret_for_hop`.

## Edits outside `docs/patches/openvault-*.patch`

- `docs/patches/README.md`, OpenVault section: the crew-netie paragraph and the crew-gate
  paragraph.
- This file.
- `scripts/`: none. No gate assertion changed.

## Measured

All on 2026-11-20, pin `3ba51cdc307f539be13fd872230d660d31436bab`, Linux, Python 3.11.

1. `python3 scripts/test_sibling_patches.py SiblingPatchTests.test_openvault_patches_apply_on_main`:
   OK, 1 test, 19.8 s.
2. Fresh clone, unpatched, `cd OpenMW && uv run --with-editable /home/user/Netie pytest -q
   --tb=short -p no:cacheprovider --junitxml=...`: 1504 passed, 0 failed, 7 skipped. Run
   twice (two clones): same counts.
3. Fresh clone, 32 patches applied with `git apply` in `OPENVAULT_STACK` order, same
   command: **1619 passed, 0 failed, 4 skipped.**
4. Difference 2 to 3 by test id (junit compare): 0 tests changed outcome. 3 ids gone, all
   skipped before: `tests.test_detect_stacks::test_cortex_is_python_not_docker_compose[tree0]`,
   `::test_openship_api_is_hono[tree0]`, `::test_openship_monorepo[tree0]` (the same three
   names come back unparametrized and pass). 115 ids new, all passed: `test_crew_gate` 7,
   `test_crew_netie_gate` 7, `test_detect_stacks` 3, `test_execution_chat` 29,
   `test_execution_shapes` 39, `test_free_pool` 5, `test_free_pool_route` 3,
   `test_freeroute_metering` 1, `test_route_strategies` 16, `test_ship_netie_claim` 5. The 4
   skips left are `tests.test_keywrap.TestDpapi` (Windows DPAPI), skipped in the baseline too.
5. Fresh clone, the 32 patches as of `dbaaaa5` (old cut), same command: 1611 passed, 2
   failed, 4 skipped. The two failures are the ones named in F1. Old to new: those two go
   failed to passed, 6 new ids, nothing else moves.
6. Patches 5 to 27 and 30 to 32 apply unchanged on the new crew patches (`git apply
   --check` each, in order).
7. Crew and routing files without Netie installed (`uv run pytest tests/test_crew_gate.py
   tests/test_crew_netie_gate.py tests/test_access_routing.py`): 34 passed. So the local
   fallback rule and Netie's rule give the same answers on these tests.
8. After `crew-gate` alone (stack position 4): `tests/test_crew_gate.py
   tests/test_contract.py tests/test_access_routing.py`: 43 passed.
9. `make ci`: `ok 30 files, laptop-ASCII clean, 46 script tests passed`.

## Not run

- `crew-netie` and `crew-skill-ids` tests at their own stack position (28, 29). Only run
  with the whole stack applied.
- `scripts/apply_product_patches.py --all` end to end.
- Any real Cortex crew client against the patched route. Route answers come from
  `TestClient` only.
- OpenVault on Windows (the 4 DPAPI tests).
- No push, issue or pull request on OpenVault.

## Assumed

- That a 422 for an unknown kind or intent is an acceptable refusal for Netie's portable
  client (`OpenVaultCrewGate.allow` treats a transport error as a refusal; read, not run).

## Follow-up on F2 (T1 executor, recut 2 consolidation)

- **Done:** `tests/test_access_routing.py` added to the OpenVault pytest list in
  `scripts/test_sibling_patches.py::test_openvault_patches_apply_on_main` and in the
  `openvault` entry of `scripts/apply_product_patches.py`. `min_passed` stays 90. No other
  line in either file changed.
- **Proved it can fail:** fresh clones at the pin, the 32 patches applied in stack order, then
  `cd OpenMW && uv run --with-editable <Netie> pytest tests/test_access_routing.py -q`.
  Old cut (patches as of `dbaaaa5`): 2 failed, 18 passed
  (`test_crew_gate_is_resolve_plus_audit`, `test_no_route_path_is_registered_twice`).
  New cut: 20 passed.
- **Gate:** `python3 -m unittest test_sibling_patches.SiblingPatchTests.test_openvault_patches_apply_on_main`
  (cwd `scripts/`): OK, 39 s.
