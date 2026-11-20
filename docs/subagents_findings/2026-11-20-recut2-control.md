# 2026-11-20 - re-cut 2, Control lane: the board past the budget

Preflight: KB `D:\Netie-KB` absent in this cloud box. `INDEX.md` and
`2026-11-12-sibling-recut.md` read; F3 there ("green here hides sibling regressions") is the
hit. PREFLIGHT: PARTIAL.

Shape: one lane of a five-lane wave, one session, no subagents (one patch, one sibling, nothing
to parallelise). Branch `claude/recut2-control`, stacked on PR #59. Sibling
`Netie-AI/netie-control` at pin `93959c6`. The live head was the same commit when cloned on
2026-11-20, so the pin did not move and nothing upstream matters here.

## Result (measured)

`control-netie-board.patch` re-cut. Sibling suite on fresh clones at the pin: **173 passed**
unpatched, **194 passed** patched, no failure in either. The 21 extra are the patch's own test
file (9 tests before this cut, 21 now). Gate test passes. `make ci` passes.

## Option comparison (the founder's ruling: check carefully, then solve)

| Option | Touches | Side effects found | Verdict |
|---|---|---|---|
| (a) show the leading rows that fit, count the rest on the board | the patch only: `netie_board.py`, 12 lines in `sources.py`, 2 label blocks in `render.py` | none measured: sibling suite and lint unchanged, payload change is additive | **Taken** |
| (b) raise `MAX_BOARD_CHARS` | `scripts/control_board.py`, `netie/`, `scripts/test_control_board.py:231` and `scripts/test_netie_api.py:942` (both assert 12000), the mirror in `ecosystem/overlays/control/0002-gate.patch`, the local copy in this patch | moves a number shared with DMS, AirGPT and Space; and any fixed number goes dark again one row later. 100 real rows need about 29000 characters, 2.4 times the budget | Refused. Does not fix the class |
| (c) page the board | new route or query parameter, `render.py` server body and page script, the `shared_read` cache key, `pickup_tray` (reads `items` once), the public Pages board (static, cannot page) | largest surface, and the static public board would still need (a) | Refused |
| (d) cut each row shorter (drop `url`, clip `title`) | `_issue_row` consumers: page script builds links from `url`, pickup dedupes on `url` | breaks links and pickup dedupe | Refused |

No change to the shared contract is needed. `scripts/control_board.py` and `netie/` are
untouched and `guard_issue_board` (which lives in the patch, not in the contract) is unchanged.

What was checked before choosing (a):

- **Page and script.** `render._board_body` (desk panel and `public_board_page`) and the page
  script `boardHtml` both read `items || open`, and print `Truncated: showing {shown} at cap
  {cap}` when `truncated` is set, and `Not shown, unreachable: ...` for the `unreachable` list.
  Neither had a way to say "N left out", so two label lines were added to each. An unreachable
  reading renders as `Board unread: <detail>` and is unchanged.
- **Pickup.** `pickup_tray` lists `board_data["items"]` and copies `truncated`. It now lists
  the rows the board shows and reports `truncated: true`. Tested.
- **Other callers.** `guard_issue_board` has no caller in this repository outside the patch and
  the gate method. `project_board`, `board_index`, `project_session` callers (`crew_runner.py`,
  `test_crew_durable.py`, `test_control_board.py`, `test_netie_api.py`, `netie_init.py`) are
  not touched and still refuse over budget, as the contract says.
- **Ids-only.** Rows keep exactly the nine `_issue_row` keys at 40, 60 and 100 rows. A gh item
  carrying a `body` never reaches the payload or the page. Tested.
- **What a human sees.** 40 rows: the board as before, no new line. 60 or 100 rows: the first
  rows plus `Truncated: showing 49 at cap 100.` and `Left out: 51 of 100 open issues did not
  fit the 12000 character board budget. The first 49 in search order are shown. Not a quiet
  omission.` Unreachable gh: `Board unread`, as before.

## F1. Past about 48 open issues the whole board went dark

- **Expected:** a board with more rows than the budget still shows rows and says what is cut.
- **Actual:** `guard_issue_board` raised `board over DitchContext` and `board()` returned
  `Reading.unreachable`. Synthetic 241-character rows: 49 pass, 50 refuse. The organisation
  has 307 open issues visible to this session, the search cap is 100, and the newest 100 real
  rows need about 29000 characters. So with the old patch landed the board is dark today.
- **Repro:** clone the pin, apply the patch from `dbaaaa5`, make `gh` return 60 rows, call
  `sources.board(slices=("open",))`: `ok False`, detail `board over DitchContext`.
- **Fix:** `fit_issue_board` runs before the strict guard. Every row ends in exactly one count,
  `fetched == shown + omitted + withheld`, and both leftover counts print on the board.
- **Root-cause class:** a refuse-all control on a list whose normal size is over the limit.
- **Invariant:** a control that blocks legitimate work is itself a failure. Silent fallback is
  a lie (so the cut is counted and printed, not quiet).

## F2. One issue title with the word "prompt" also took the whole board dark

- **Expected:** a guarded word in one title does not hide every other issue.
- **Actual:** the budget check also scans the dumped rows for `prompt`, `transcript`,
  `password`, `skill_body` and the vault key name as substrings. Three rows, one titled
  `fix prompt cache`: `ok False`, detail `board contained prompt`. Not in the brief. Real
  titles: 8 of the 307 open issues match (6 `prompt`, 1 `password`, 1 vault key name). None is
  in the newest 100 today, so it has not fired yet. It would on the next such issue.
- **Repro:** as F1 with three rows and that title.
- **Fix:** such a row is withheld: never displayed, counted, and printed as `Withheld: 1 of 3
  open issues are not shown because their text names a guarded key.` A guarded key as a row
  *key*, or a remote-desktop `kind`, still refuses the whole board, even in a row the cut would
  have left out. The text is still never shown, so the check is narrower in blast radius, not
  weaker.
- **Root-cause class:** same as F1, a per-row fault escalated to a whole-view refusal.
- **Invariant:** a control that blocks legitimate work is itself a failure.
- **Open decision for the founder:** withholding hides a legitimate issue (visibly). The other
  choice is to show titles and scan only keys. That loosens a check, so it was not taken here.

## F3. With Netie installed, 3 of the patch's own tests failed

- **Expected:** the control stack in `apply_product_patches.py` (`uv_add_netie=True`) passes.
- **Actual:** with `netie.control` importable, `project_board` raises the contract's
  `control_board.ControlDenied`, and the patch defined a second local `ControlDenied`. Three
  tests expecting the local class failed (179 passed, 3 failed), on the old patch too.
- **Repro:** old patch on the pin, `PYTHONPATH=<this repo> pytest -q`.
- **Fix:** the patch imports `ControlDenied` from `netie.control` when installed and defines
  it only as a fallback. 194 passed both ways. One test pins the identity.
- **Root-cause class:** the gate never ran the patch in the mode the apply-all script uses.
- **Invariant:** prove a gate can fail before trusting it green.

## F4. The old patch turned the sibling's lint red

- **Expected:** a patch does not break the sibling's CI (`ruff check netie_control tests`).
- **Actual:** base clean, old patch 3 errors (2 import order, 1 RUF015), all in the patch's own
  two new files. Fixed with ruff's own rewrite. Patched tree is clean.
- **Root-cause class / invariant:** as F3. Assert the artifact the sibling actually receives.

## Edits under `scripts/` (every one)

- `test_sibling_patches.py`, method `test_control_netie_board_applies_on_main` only: 49 lines
  **added** (fit at 40, 60, 100 rows; counts sum; prefix order; the strict guard still refuses
  the unfitted list; a guarded word is withheld; a leaked key still raises; both labels are in
  `render.py`). No existing assertion changed or removed.
- `apply_product_patches.py`, control entry: `min_passed` 51 -> 149. The floor was stale (the
  two files already ran 137 before this cut). Raised, not lowered.

## Measured (2026-11-20, this VM)

- `python3 scripts/test_sibling_patches.py SiblingPatchTests.test_control_netie_board_applies_on_main`: OK.
  Same command with the old patch file restored: FAILS on the first new assertion. Gate can fail.
- Fresh clone at `93959c6`, `python -m pytest -q`: unpatched **173 passed**; patched **194
  passed**; patched with `PYTHONPATH=<this repo>`: **194 passed**. Old patch: 182 passed, and
  179 passed 3 failed with Netie importable. venv: `fastapi` 0.165.0, `pytest` 9.2.0, `httpx`,
  Python 3.13.18. `tests/test_netie_board.py` went from 9 tests to 21.
- `pytest tests/test_netie_board.py tests/test_control_stays_plane_4.py -q`: 149 passed.
- `ruff check netie_control tests` (ruff 0.16.8, the sibling pin): base clean, old patch 3
  errors, new patch clean.
- Mutation checks on the patched tree, each run against `tests/test_netie_board.py`: omitted
  rows not counted, 5 fail; server label removed, 3 fail; script label removed, 2 fail; word
  withhold removed, 1 fails; prefix rule removed, 1 fails.
- `git status` on the patched clone: 3 files modified, 2 added. No sibling test file is edited,
  reversed, skipped or deleted. `FORBIDDEN` has 4 keys, `NOT_GUACAMOLE` has the 4 desktop routes.
- `gh api -X GET search/issues -f q='org:Netie-AI is:open is:issue'` (4 pages): 307 open
  issues (Cortex 127, dms 103, OpenVault 57, Space 13, Pointer 4, landing 3). Page 1 is in
  created-descending order. Titles on page 1: 31 to 155 characters, mean 94.
- Those newest 100 rows through the patched `board()`: shown 42, omitted 58, withheld 0, ok.
  Through the old patch: `board over DitchContext`.
- `make ci`: `ok 30 files, laptop-ASCII clean, 46 script tests passed`.

## Assumed, not measured

- `gh search issues --owner Netie-AI` returns the same newest-first order as the REST search
  measured above. The label says "in search order", which is true either way.
- 307 is what this session's token can see. Private repositories it cannot see would add more.
- `uv add git+...Netie.git` gives the same import behaviour as `PYTHONPATH=<this repo>`.

## Not run

- A live `gh` on an operator machine, and the page in a real browser. The page script was run
  in node on real readings; the DOM around it was not.
- `scripts/apply_product_patches.py --all` end to end (it needs `uv add` from GitHub).
- The sibling's Pages workflow (`publish_board`). `public_board_page` is tested directly.

## Not changed, worth a look

- `completed` (up to 100 rows), `prs` (40) and `actions` are not budgeted and not row-guarded,
  before or after this cut. The budget covers `items` and `unreachable` only.
- The budget fits about 42 real rows of a 100-row cap. Whether 12000 is the right number for a
  human board is a contract question for the parent. This cut makes any answer safe.

## Verified by T1 (independent agent, not the builder)

A separate verifier agent replayed the lane on its own fresh clones at pin `93959c6`. It
edited nothing here.

- Command, both trees: `uv run --with 'fastapi>=0.110' --with 'uvicorn[standard]' --with pytest --with httpx python -m pytest -q --tb=short -p no:cacheprovider -rfE`
  (an ephemeral uv env, not this finding's venv; Netie not installed).
- Unpatched: 173 passed, 0 failed, 0 errors, 0 skipped. Patched: 194 passed, 0 failed.
  Patched with `PYTHONPATH=<Netie>`: 194 passed. Confirmed.
- The +21 are all in the new `tests/test_netie_board.py`. No per-id diff was run; this is
  inferred from the counts and from the patch's file list. No existing Control test file is
  modified (`git diff --name-status` against the pin: `netie_control/{app,render,sources}.py`
  M, `netie_control/netie_board.py` A, `tests/test_netie_board.py` A).
- Gate: `test_control_netie_board_applies_on_main` OK.
- Not replayed: the builder's mutation claims.
