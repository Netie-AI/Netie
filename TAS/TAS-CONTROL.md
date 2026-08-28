# TAS-CONTROL - Netie Control technical architecture

**Plane:** 4 (operator board view) · **Repo:** `Netie-AI/netie-control` (public clone; push 403)
**Measured:** 2026-08-28 HEAD `82ab1ae` (12 files). FastAPI shell, 405 on secrets/route/goal/run. Not Guacamole.

---

## 1. What it is

The board *view* of Cortex-Crew: estate gate, ledger/manifest/refusal cards, who is running. Deliberately thin (founder: 12 files, 1 commit).

**Is not:** a product, a second Cortex, Apache Guacamole, or Plane.so.

DR-0001: fold into Crew when Crew exists. Do not grow a sibling shell.

Portable view in this Netie repo: `scripts/control_board.py`.
Read-only cards from Crew index + Factory.index() tickets/epics + ledger peek + refusals.
`project_session` is one live run: ids, todos, permissions, hand-off id. No transcript.
Session permissions drop Deep Agents builtins and billing-bypass names (`search_capabilities`).
Transcript / prompt / key leak is denied on every row (runs, tickets, epics, ledger, refusals).
RDP / VNC / SSH / telnet / Kubernetes / Guacamole kinds refuse (Control is not a remote-desktop gateway).
Board / session over DitchContext 12k refuse (no silent drop). Score stays **2 / 10** as a board view, **1 / 10** as Guacamole.
Ticket runner is `scripts/crew_runner.py` (`run_open_ticket` -> Factory -> wrap). Not a second loop.
`run_dag` on the board still refuses. `python3 scripts/test_control_board.py` and `python3 scripts/test_crew_runner.py`.

---

## 2. vs Guacamole

Guacamole is a remote-desktop gateway (Apache-2.0). Control is a ticket/ledger board. Wrong analogue. Closer: GitHub Projects (already the ticket system) + Crew session view.

---

## 3. Verify

```
NEEDS-YOU TAS-CONTROL  add Netie-AI/netie-control or merge those 12 files into Crew
```
