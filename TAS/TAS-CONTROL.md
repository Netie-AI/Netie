# TAS-CONTROL - Netie Control technical architecture

**Plane:** 4 (operator board view) · **Repo:** `Netie-AI/netie-control` (this token: not found)
**Measured:** 2026-08-27 from founder inventory and DR-0001. Not cloned.

---

## 1. What it is

The board *view* of Cortex-Crew: estate gate, ledger/manifest/refusal cards, who is running. Deliberately thin (founder: 12 files, 1 commit).

**Is not:** a product, a second Cortex, Apache Guacamole, or Plane.so.

DR-0001: fold into Crew when Crew exists. Do not grow a sibling shell.

Portable view in this Netie repo (Control remote still 404): `scripts/control_board.py`.
Read-only cards from Crew index + Factory.index() tickets/epics + ledger peek + refusals.
`project_session` is one live run: ids, todos, permissions, hand-off id. No transcript.
Transcript / prompt / key leak is denied on every row (runs, tickets, epics, ledger, refusals).
Ticket runner: `scripts/crew_runner.py` (Cortex refusal on the board, ticket stays open).
`run_dag` raises. Score stays **2 / 10** as a board view, **1 / 10** as Guacamole.
`python3 scripts/test_control_board.py` and `python3 scripts/test_crew_runner.py`.

---

## 2. vs Guacamole

Guacamole is a remote-desktop gateway (Apache-2.0). Control is a ticket/ledger board. Wrong analogue. Closer: GitHub Projects (already the ticket system) + Crew session view.

---

## 3. Verify

```
NEEDS-YOU TAS-CONTROL  add Netie-AI/netie-control or merge those 12 files into Crew
```
