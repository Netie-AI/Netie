# Netie operating model

How this company works in the software layer: which files may exist, how work becomes a
ticket, how code gets verified, and who does what.

Companion to `NETIE.md` (what we are). This file is *how*.

Version 1.0 - 2026-08-01.

---

## Part 1. The file law

### The problem this solves

As of the 2026-08-01 audit, `D:\Cortex` had **four different files each claiming to be
the one you read first**, and its own `README.md` contained instructions to disbelieve
three of its own top-level documents. Three files stated the test suite was "153 passed,
4 skipped"; the measured number that day was 1289. One file named the active branch as
`dms-v2`, which another file in the same directory listed as retired.

None of this was carelessness. It is what happens when every session invents a filename.

### The rule

**Five file types exist per repo. There is no sixth.**

| Type | Filename | Changes | Size | Rule |
|------|----------|---------|------|------|
| **LAW** | `CLAUDE.md` | when a decision changes | any | Invariants, boundaries, protected paths, how to verify. Never a status update. `AGENTS.md` is a 3-line pointer to it, nothing more. |
| **MAP** | `docs/ACTIVE.md` | when structure changes | < 150 lines | What exists, where it lives, which doc to open for which lane. |
| **STATE** | `STATUS.md` | every session | **< 60 lines, hard cap** | The only churn file. What is true now, what is next. Older entries move to HISTORY, they do not accumulate here. |
| **HISTORY** | `CHANGELOG.md` | on every ship | append-only | Never edited, only appended. Dated. This is where narrative goes. |
| **DEFERRED** | `PARKING_LOT.md` | when something is postponed | any | Every entry carries an unlock condition. No condition means it is not parked, it is abandoned - delete it. |

Everything else is one of:
- **generated** (a script writes it; never hand-edit),
- **reference** (a stable explainer under `docs/`; if it has a date in the body it is not reference, it is history), or
- **archived** (`docs/bin/`; kept for provenance, never read for truth).

### Consequences, stated so nobody has to re-derive them

**No per-agent files.** `CLAUDE_HANDOFF.md` and `CURSOR_HANDOFF.md` were created because
several agents work these repos. That was the wrong fix. Different agents do not need
different truth; they need the same truth plus a role. **One `STATUS.md`, read by
everyone.** Both handoff files are deleted.

**No per-session files.** The question "what filename should I store this session's
context in?" has exactly one answer: **you do not create a file.** You update `STATUS.md`
and, if you learned something reusable, you file a Netie-KB record. A new filename per
session is how an estate ends up with eleven canonical documents.

**No dated filenames outside `docs/bin/`.** `NETIE_ENGINE_DEPTH_PLAN_2026-07-31.md` is a
snapshot pretending to be a plan. If it is live, it has no date and lives under `docs/`.
If it is a snapshot, it is history and lives in `docs/bin/`.

**Anything a script can write, a script writes.** Test counts, branch tips, doc indexes,
version tables. Every hand-maintained table in this estate was stale within 48 hours -
this is measured, not asserted. `D:\Netie-KB` already proves the pattern works:
`kb.py render` writes the agent rule files, and they are byte-identical to their sources
right now.

**One `STATUS.md` header block is generated.** Branch, tip, test count, CI status. If a
human types a test count into a file, it is wrong by Thursday.

### The consolidation this implies for Cortex

Proposed, not yet executed - needs your yes because it deletes and moves tracked files.

> **Correction 2026-08-02.** An adversarial check found three defects in the table below,
> two of them in entries I had called safe. They are corrected in place. The general
> lesson: **"no production callers" is not "no callers"**, and **"tracked, therefore
> recoverable" must be verified with `git ls-files`, not assumed.**

| Action | Files |
|---|---|
| ~~**Delete** `key.md`~~ **Do not delete** | `key.md` is **not tracked** - `git ls-files --error-unmatch key.md` fails. It is gitignored at `.gitignore:37` and is a **named secrets slot**: `scripts/secrets_scan.py:47` hardcodes `FORBIDDEN_TRACKED = {"env.local", "key.md"}`, and `.sops.yaml:5` plus `PORTABLE_README.md:49` document it as the local secrets file. Deleting an untracked file is not recoverable from git. It is 0 bytes today so nothing is lost today, but the safety rationale was false. Leave it. |
| **Move to `docs/bin/handoffs/`** | `CONTEXT.md`, `CLAUDE_HANDOFF.md`, `CURSOR_HANDOFF.md` |
| **Fold into MAP, then archive** | `ARCHITECTURE.md` (its honest built-vs-partial table is good; the branch table must become generated) |
| **Merge** | `PORTABLE_README.md` -> `docs/SETUP_NEW_MACHINE.md`; `docs/DEMO.md` -> README quick start (its first command `cd C:\Users\user\RUMA\Cortex` points at a machine that no longer exists) |
| **Reduce to a pointer** | `docs/README.md` (currently still recommends the disavowed `CONTEXT.md`) |
| **Trim** | `STATUS.md` 453 lines -> under 60. The dated narrative moves to `CHANGELOG.md`, which is where it belonged. |
| **Fix in place** | `README.md:9` claims the system "applies Wasm sandboxing". It does not. See Part 3. |
| **Retire or repoint** | `scripts/handoff.py` - it can only re-stamp a timestamp, which is why the stale "153 tests" survived every regeneration |

Same pass applies to `D:\OpenVault` (merge `next_plan.md` into `STATUS.md`) and
`D:\AirGPT` (archive `GATE_PASS.md`).

**`PRODUCT_ROLES.md` becomes generated.** Four copies exist across four repos, the file
says "keep this file identical", and all four differ. One source in `D:\Netie`, a sync
script, and a CI diff check - the same pattern already used for the OpenAPI spec.

---

## Part 2. Work: tickets that carry their own prompt

### Correction (2026-08-02)

**An earlier version of this file proposed making Netie-KB the ticket system. That was
wrong.** Netie-KB is the *distillation record* - what was learned from Claude and Cursor
sessions, promoted into rules. Overloading it with work items would destroy the thing it
is good at.

**Tickets live in GitHub Issues.** The full chain, ID scheme, and plan-to-issue
automation are specified in [`../Rules/DOCUMENT_SYSTEM.md`](../Rules/DOCUMENT_SYSTEM.md),
which supersedes this section. What follows below is the ticket *body format*, which
survived the correction unchanged and is still what every issue must contain.

### What Netie-KB still needs, as a KB

1. **An `enforced_by` field, validated to resolve to a real file.** Today the
   highest-severity rule in the corpus (`R-0001`, gates assert the customer artifact)
   points at `tests/invariants/test_envelope.py`, which does not exist. A rule that names
   a non-existent enforcer is a wish.
2. **A git remote and running CI.** Netie-KB has no remote - the corpus exists only on one
   disk - and `kb.py validate` exits 1 with roughly 33 errors, including laptop-ASCII
   violations inside the rule corpus itself. A rules engine that fails its own rules
   cannot be quoted in a code review.

### Ticket format

Every work record carries five fields. The fifth is the one that makes it AI-executable.

```markdown
---
id: W-0042
type: work
status: open
severity: high
enforced_by: tests/dms/test_space_acl_boundary.py
---

# Space ACL boundary must hold

**Problem.** Every Space currently reads the whole warehouse. `live_ask` mints its
manifest from `demo_acl()`, which allowlists every table with predicate TRUE regardless
of `space_id`. The correct functions exist and are unit-tested with no production caller.

**Acceptance - the customer-visible assertion.**
Two Spaces, one warehouse. Space A asks a question whose answer requires a table granted
only to Space B. The returned envelope is `abstained: true` with a refusal reason. Not a
green badge over an empty result.

**Why it is not a one-liner.** It cannot simply be switched on: `acl_grants` has zero
rows and three of six demo tables have no `data_sources` row, so enforcement today would
refuse 100 percent of asks. The product decision - which tables are company-scoped versus
Space-scoped - has to be made first.

**Agent prompt.**
> Read `D:\DMS\packages\executor\dms_executor\__init__.py:111-172` and
> `D:\DMS\tests\test_space_acl_boundary.py`. Seed `data_sources` rows for `suppliers`,
> `shipments`, `alerts`, then `acl_grants` to match the scoping decision in this ticket.
> Switch `live_ask` from `demo_acl()` to `intersect_space_grants`. The strict-xfail in
> the test file flipping to pass is the completion signal - do not weaken it to get
> there. Then re-run the full corpus and confirm nothing valid became refused (R-0005).
```

**Why the prompt is part of the ticket.** Writing it forces the author to name the files,
the acceptance signal, and the failure mode. A ticket whose prompt cannot be written is a
ticket that is not ready. This is a specification discipline that happens to also be
machine-readable.

### The loop

```
observe -> file a work record (kb.py new work)
        -> agent executes against the embedded prompt
        -> a DIFFERENT agent verifies against the acceptance assertion   [R-0003]
        -> merge
        -> file a finding for what was learned
        -> promote recurring findings to rules
```

---

## Part 3. Verification: CI, and the false greens

### What exists

The CI design is genuinely good and should not be rebuilt:

- **Cortex** `ci.yml`: ruff -> mypy -> lint-imports -> version check -> OpenAPI drift ->
  contract compat -> full pytest, plus a base-install job proving the core profile
  imports, plus a protected-paths job requiring `INVARIANT-CHANGE:` in the commit body
  for changes under `tests/contract/**`, `tests/invariants/**`, `.importlinter`.
- Two **independent side gates** (`rls.yml` Postgres row-level-security deny-proof,
  `secrets.yml` key scanner) run as separate workflows, so they still report if the main
  chain dies. That separation is a real design win.
- **DMS** verifies vendored OpenAPI sha256 sidecars before anything else runs.
- **Versioning** is correct and enforced: engine and contract version lines are
  independent, with an AST scanner that fails the build if code assumes they are equal.

### What is broken, and it is the urgent part

| Problem | Evidence |
|---|---|
| **Cortex CI is red and dies at gate 1** on 5 Ruff errors, so mypy, import-linter, the version check, OpenAPI drift, contract compat and all 1298 tests **have never run on main** | reproduced locally on HEAD |
| **The v2.5.0 release failed** on OpenAPI drift. Zero GitHub Releases exist. The release ritual has never completed once | release run history |
| **DMS CI dies in 14 seconds** on a stale spec digest; **OpenVault CI failed 7 of its last 8 runs** | run history |
| **Cortex and DMS each carry 13 unpushed commits** - today's HEAD has never seen CI in either repo | `git status` |
| **AirGPT has no CI at all** | one manual workflow |
| **`tests/invariants/**` is a CI-protected path containing zero tests** | directory listing |
| **`.githooks/pre-commit` is tracked but `core.hooksPath` is unset**, so the secrets gate never fires | git config |

### The three false greens

These matter more than the red builds, because a red build announces itself.

1. **The import-linter boundary reports "2 kept, 0 broken" while the engine's hottest
   module violates the top invariant 8 times.** `packs/dms/semantic/` has no
   `__init__.py`, so it is invisible to the dependency graph. Adding one surfaces eight
   real violations in `answer_engine.py`. Worse, the verdict also depends on whether
   `.import_linter_cache` is warm: the same tree returns KEPT or BROKEN depending on
   cache state. `CLAUDE.md` currently instructs agents to trust this checker over the AST
   test; that instruction is backwards.

2. **The eval corpus reports 376/376 with zero wrong and did not catch a single one of
   the five most recent confidently-wrong live defects.** Every one of the last five
   commits fixes a P0 answer defect found by a human in a live session, and every commit
   body records that the corpus stayed green throughout. That is a demonstrated zero
   detection rate on the exact defect class the corpus exists to catch.

3. **The "live" corpus mode does not score the live answer.** For an answerable seed it
   checks the envelope only for the presence of `abstained` and `sql_used`, then re-runs
   the question **offline** and scores that. The live artifact is an offline result
   wearing a live label - the precise failure `CLAUDE.md` section 8 was written to
   prevent.

**Rule 9 exists because of this: verify a gate can fail before trusting it green.**
Any gate added from here ships with a deliberately-broken commit proving it goes red.

### And one documentation defect that is a customer-facing problem

`D:\Cortex\README.md:9` tells the public the system "applies Wasm sandboxing + platform
security". It does not. Both shipped wasm modules are **0 bytes** (git's empty blob). A
real `wasmtime` wrapper exists at `CortexOS/execution/wasm_isolate.py` but has zero
production callers - only three test files import it. Every internal document is honest
about this; the README is the outlier, and the README is the document a customer reads.

**Delete the clause today.** This is the cheapest integrity fix available.

---

## Part 4. Containerisation and isolation - the honest answer

You asked whether it is actually safe, and whether to use WebAssembly or move to local
containerisation. The audited answer:

**Today it is not safe to run untrusted agent-generated code on this.** Not "partially" -
not at all.

- **No WASM isolation.** Zero production callers, 0-byte modules.
- **No container isolation for execution.** `docker-compose.yml` starts exactly one
  service, Qdrant. The engine itself is not containerised. Untrusted apps execute on the
  **host** via `subprocess.Popen` with `env = os.environ.copy()`, so the child process
  inherits every engine secret. Both Dockerfiles run as root with no `cap_drop`, no
  `read_only`, no `seccomp`, no resource limits, and bind `0.0.0.0`.
- **Auth is disabled by default in both shipped images** (`DMS_AUTH_DISABLED=1`), which
  hands every anonymous caller an `admin` role. With it unset, the fallback is three
  admin/steward/viewer keys published in the source tree, applied with no warning - and
  the CI secrets scanner is hardcoded to skip them.
- **The whole import -> approve -> start chain for third-party apps is unauthenticated.**
  The "one human approval" the ship gate depends on is itself an anonymous POST.
- **The manifest control is real, rigorous, and bypassed on the product path.**
  `enforce_manifest` is wired into `/v1/contract/*`. But `answer_engine.answer` takes
  `verified` as an *optional* argument, and `POST /dms/query` - the demo and product path
  - calls it without one, opening DuckDB directly under no manifest enforcement.

Real controls that do exist and should be credited: `shell=False`, engine-generated argv
rather than zip-supplied, zip-slip-safe extraction, an approved-status check, and the
`core` profile genuinely disabling the exec chain (it returns 501). None of these is
isolation.

### The recommendation

**Do not build WASM.** It is the wrong tool: your workloads are Python and Node with
native dependencies, which is precisely what WASI does badly.

> **Correction 2026-08-02.** I previously said to *delete* `wasm_isolate.py`. That was
> wrong and would have broken the build. It has zero **production** callers - correct -
> but three test modules import it: `tests/test_execution/test_wasm_isolate.py:5`,
> `tests/security/test_adversarial_prompts.py:10`, and `tests/security/test_wasm_honesty.py:12`.
> The last one calls `inspect.getsource(wasm_isolate)` at `:26-28` - it asserts on the
> module's own source text, so deleting the file fails three modules at **import** time.
>
> Correct sequence: delete the three test modules first (`test_wasm_honesty.py:41` is an
> unconditional `@pytest.mark.skip` labelled SCAFFOLD, which is a failing test under
> R-0002 anyway), then the module. Keep `PARKING_LOT.md` P2 as the record of why.
>
> The general rule this cost me: **grep for importers across the whole tree, not just
> production paths, before calling anything dead.**

**Do this instead, in order:**

1. **Close the manifest bypass.** Make `verified` a required argument on
   `answer_engine.answer`. This is hours of work and it is the single highest-value
   security change available, because it turns the one rigorous control you already built
   from decorative into load-bearing on the path customers use.
2. **Turn auth on by default.** Invert the flag: `DMS_AUTH_REQUIRED` defaulting to true,
   with demo keys refused unless an explicit demo profile is set, and a visible startup
   banner when running degraded (rule 6 - a silent fallback is a lie).
3. **Put `require_role` on the four modules that lack it** - `app_routes`, `dag_run`,
   `dms_query`, `chat_routes`. These are exactly the modules that execute code and run
   SQL. The other ten route modules already have it.
4. **Then, and only when a customer asks for untrusted-code execution:** container
   isolation via rootless Podman or gVisor, non-root user, `cap_drop: ALL`, `read_only`
   rootfs, no network by default, scrubbed environment. Not WASM.

Steps 1-3 are days. Step 4 should not begin before a customer needs it.

---

## Part 5. Repositories: do not split

The instinct to split is correct in feeling and wrong in fact. Measured:

- Cortex tracks **826 files**. That is small.
- `activeflow/activepieces` - the vendored tree that *looks* like the clone-cost problem -
  is **gitignored and tracks 0 files**. The split premise is dead on arrival.
- `.git` is ~305 MB of pack, mostly historical blobs under `CortexOS/` and `data/`.
- Windows path length is a non-issue (`core.longpaths=true`, longest tracked path is 73
  characters). Git LFS is not in play.

**Keep the monorepo.** The product split you already did - Cortex engine plus sibling app
repos, talking over HTTP with a pinned contract - is the right seam and it is done.

Cheaper fixes for the coordination pain, in order:

| # | Fix | Effort |
|---|-----|--------|
| 0 | **Unify the contract import spelling.** `cortex_contract` and `packages.cortex_contract` currently resolve to the same file as **two different module identities** (proved: `A is B` is False). An `isinstance` check inside `canonical_manifest_bytes` already silently takes the wrong branch. The bytes match today only by luck - every field happens to be a string. **Add one datetime field and manifest signing breaks, presenting as a crypto bug.** This must be fixed *before* any packaging work. | days |
| 1 | Build the contract wheel - **after** step 0, and built from the monorepo (spec generation needs both trees in one working copy) | days |
| 2 | Remove the `netie.pth` global sys.path injection (it puts `D:/Cortex` on the path of **every** Python process on the machine) | hours |
| 3 | `git clone --filter=blob:none` for cheap clones - confirmed unused today, zero SHA churn | minutes |
| 4 | Fix AirGPT's `.gitmodules` - three gitlinks, one mapping, `git submodule status` fails outright | minutes |

Do **not** rewrite history. 305 MB against four active worktrees and three concurrent
lanes is not a trade worth making.

---

## Part 6. Roles

### CEO (you)

Owns: what we sell, to whom, and which of the four planes we are on. The single scarce
resource is your judgement on scope - this estate's failure mode is eight workstreams at
80 percent, and only you can close that by refusing.

**The one operational task nobody can do for you:** the gold-verification review waves.
329 corpus items are machine-written and unverified, which is why every accuracy claim is
bounded at n=47 and not n=376. It is roughly 1.5 days of your attention at 15 seconds an
item, it is deliberately TTY-gated, and no agent can do it. Until it is done, "zero
confidently wrong" is a claim bounded at 6.4 percent error, not under one percent.

### Marketing specialist

Owns: the demo video, the product narrative, social distribution.

Must be able to: run the demo stack unaided, produce SaaS-grade product videos with AI
tooling, write copy that does not overclaim.

**First 30 days:** one warehouse case study - video plus metrics. Nothing else ships
until a stranger can watch two minutes and understand what Netie does.

**Hard constraint:** every claim in every asset must be traceable to a passing gate. The
README WASM claim is the example of what marketing must never generate. If a claim cannot
be pointed at a test, it does not go in the video.

### Technical specialist - prompts, rules, evaluation

Owns: `D:\Netie-KB`. The rules, the workflows, the agent rule files, and the eval corpora.

**First 30 days:**
1. Get Netie-KB passing its own validator, then give it a remote and CI.
2. Add `enforced_by` validation so no rule can name a test that does not exist.
3. Reconcile the **four** independently maintained eval corpora into one gold set. There
   are currently four, with overlapping intent, no shared gold, and a 38-item golden set
   with zero verified items.
4. Make the eval gate able to fail - score abstain-on-an-answerable-question as a
   regression rather than free, and make `--live` compare the real envelope to gold.

This role is the immune system. It is the highest-leverage hire because every false green
above is a failure of this function.

### Agent-coordination builder

Owns: multi-agent execution - the workflows, subagent definitions, isolation, and
verification harnesses that let work actually parallelise.

**First 30 days:**
1. Codify the preflight-then-fan-out-then-adversarially-verify pattern as a reusable
   workflow, not a per-session improvisation.
2. Enforce rule 3 mechanically: the agent that found a defect never verifies it.
3. Stand up the work-record loop from Part 2 so tickets carry executable prompts.

**Hiring signal for this role:** ask the candidate to describe a time an automated check
told them something was working when it was not, and what they changed so it could not
happen again. Someone who has never been burned by a false green will build more of them.

---

## Part 7. The next four weeks

The estate has eight workstreams open between 60 and 90 percent and none at 100. The fix
is not more parallelism. Pick one buyer-visible slice and finish it until a stranger can
use it.

**The slice:** *ask a governed question inside a Space and get an auditable answer, with
the Space boundary actually holding.*

| # | Do | Size |
|---|----|------|
| 1 | Delete the WASM claim from `README.md` | minutes |
| 2 | Fix the 5 Ruff errors so CI runs at all, then push the 13 unpushed commits | hours |
| 3 | Fix the exclusion stop-list defect - a question naming an exact SKU currently abstains, because two lists disagree about the word "and". Fix at the funnel so the lists cannot diverge again | 1-2 hours |
| 4 | Make the eval gate able to fail (three changes to `bench/corpus.py`) | 2-3 days |
| 5 | Close the manifest bypass on `/dms/query` | 1-2 days |
| 6 | Space ACL: decide company-scoped vs Space-scoped, seed the tables, switch `live_ask` off `demo_acl()` | 2-3 days |
| 7 | Run the gold-verification waves - yours, not an agent's | 1.5 days |
| 8 | Execute the kill list - **with a link sweep first**. Moving or deleting the named basenames touches **37 files** that reference them, including `scripts/handoff.py`, `README.md`, `STATUS.md`, `PARKING_LOT.md`, `docs/ACTIVE.md` and `docs/README.md`. Any move without the sweep leaves dangling pointers in the very map that is supposed to orient a cold session. Order: sweep links, then `activeflow/`, `D:\AirGPT\CortexOS`, the dead `query_skill` layer, the duplicate `demo/dms-ui`, `tests/test_dms/`, then the wasm test modules, then `wasm_isolate.py`. Not `key.md`. | 2-3 days |

**Not in the next four weeks:** the H0-H6 depth plan, gen-cFSM, OSR wiring, JEPA, the
Palantir-parity programme, and the C7 decision. C7 in particular cannot be decided
without real customer questions - the generated-SQL path measured 17 confidently wrong
against a floor of zero, and no amount of paraphrasing your own test set will resolve it.

**The honest condition:** if at the end of four weeks there is no user, stop and
reconsider. If there is one user, C7 becomes answerable with their questions, which is
the only way it was ever going to be answerable.
