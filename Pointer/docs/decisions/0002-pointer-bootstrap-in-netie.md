---
status: proposed
date: 2026-08-22
decision-makers: founder
---

# DR-0002 - Pointer bootstrap lives in Netie until the product repo is cloneable

## Context and Problem Statement

`NETIE.md` lists Pointer at `Netie-AI/Pointer` / `D:\Pointer`. This cloud token
receives GitHub 404 for that repo. Gmail proves the repo exists and is receiving
PRs. The founder asked this run to control the laptop with Pointer and to install
OpenClaw/Hermes if Pointer failed.

Installing OpenClaw here would add a third orchestrator (forbidden) and would not
reach the laptop.

## Considered Options

- Stop and wait for Pointer clone access
- Install OpenClaw/Hermes on this VM as the control plane
- Ship a fail-closed localhost daemon in this meta repo that this VM can test

## Decision Outcome

Ship the bootstrap daemon in `Pointer/` of `Netie-AI/Netie`. It is a client, not
a planner. OpenClaw/Hermes stay uninstalled on this VM. When a token can clone
`Netie-AI/Pointer`, this bootstrap is replaced by a contract test against that API
or deleted.

Confirmation: `Pointer/scripts/verify.sh` exits 0, including a live mouse move
when `DISPLAY` is set.

## Consequences

Positive: laptop-control work is testable in cloud without lying about clone access.

Negative: two Pointer trees until the product repo is visible. That split is
named in `Pointer/STATUS.md` and `PARKING_LOT.md` P-004.
