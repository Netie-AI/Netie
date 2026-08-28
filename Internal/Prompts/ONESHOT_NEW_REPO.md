# One-shot prompts

Copy-paste. Each one is self-contained - it assumes the session knows nothing.

---

## 1. Initialise a new repo

> Set up this repo on the Netie operating system.
>
> Run `python D:\Netie\scripts\netie_init.py .` from the repo root. It is idempotent, so
> re-running is safe.
>
> Then read the `CLAUDE.md` it produced and fill in the **Hard rules** section, which it
> leaves empty on purpose. Write the invariants where a violation would be *silent and
> expensive* in this specific codebase - not general good practice. For each one, name
> the CI job or test that enforces it, or say plainly that nothing does. A rule with no
> enforcer is a wish, and marking it as such is more useful than pretending.
>
> Finally, tell me which of the five governed files you created versus which already
> existed under a different name, so I know what to rename by hand.

---

## 2. Start a new product slice (PRD -> epics)

> Use the `prd-agent` subagent.
>
> Read `D:\Netie\NETIE.md`, `D:\Netie\Internal\Rules\DOCUMENT_SYSTEM.md`, and
> `D:\Netie\Internal\Agents\AGENT_SYSTEM.md` sections 4-6. Then read the PRD at
> `D:\Netie\Software Blueprint\<PRODUCT>\PRD-<NNN>-*.md`.
>
> Before slicing anything, verify the PRD's claims against the actual code and tell me
> where it is wrong. Then slice it into epics ordered by irreversibility, respecting the
> WIP limit: at most two in flight, at least one human-inspectable.
>
> File them as GitHub Issues with the `epic` label, each carrying `Repo:`,
> `Contract impact:`, and `Depends on:`. Do not create tickets.

---

## 3. Work the backlog

> Use the `epic-agent` subagent on `EPIC-<NNN>`.
>
> If tickets do not exist, decompose the epic into them. If tickets exist and have
> closed, run the completeness check - re-derive from the code, not from checkboxes, and
> report `COMPLETE`, `INCOMPLETE`, or `UNVERIFIABLE`.
>
> Then use `ticket-runner` on whatever is open and unblocked. Follow each ticket's
> embedded agent prompt literally. Stop and tell me if any acceptance assertion cannot be
> met without weakening a test or a gate.

---

## 4. Report a bug or ask for a feature

> Use the `prd-agent` subagent.
>
> Here is what I want: **<describe it in your own words>**
>
> Do not implement it. Route it: find which PRD and which epic it belongs to, append it
> to that PRD's feedback ledger, and file a ticket if it maps to an open or reopenable
> epic. If it maps to no epic, stop and tell me - that is a PRD amendment and it is my
> call, not yours.

---

## 5. Resume cold, no context

> Read `CLAUDE.md` in this repo, then the four sources its "Resume from cold" table
> names. Then run `gh issue list` here and tell me:
>
> 1. what the current epic wave is,
> 2. what is open and unblocked that you could start now,
> 3. what is blocked, naming the repo and issue number it waits on,
> 4. anything needing a decision from me.
>
> Use the status line format: `DONE` / `BLOCKED <id> waiting on <owner/repo#N> in <repo>`
> / `NEEDS-YOU <id> <decision>` / `FAILED <id>`.

---

## 6. Roll the system out everywhere

> Run `python D:\Netie\scripts\netie_init.py --all --dry-run` and show me the plan.
>
> If it looks right, run it without `--dry-run`, then commit each repo separately with an
> honest message naming what was created versus what already existed. Do not use
> `git add -A` - stage explicit paths, because several lanes work these repos.

---

## 7. Bootstrap Cortex-Crew (only after PRD-001 wave 1)

> Create `Netie-AI/Cortex-Crew` (or rename Control into it). Then:
>
> 1. `python D:\Netie\scripts\netie_init.py .`
> 2. Read `D:\Netie\Software Blueprint\Crew\PRD-002-operator-factory.md` and `TAS/TAS-CREW.md`.
> 3. `uv add deepagents` (MIT). Wrap every tool with Cortex `tool_runner`. Call OpenVault `POST /api/crew/gate` before leave-machine.
> 4. Do not clone OpenWork, Deep Agents source, or Grok Bot reconstructed into the tree.
> 5. Fold Netie Control's board views in as Crew UI, not a sibling product.
>
> Refuse to start if PRD-001 Space boundary is still decorative.
