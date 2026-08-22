# STATUS.md - Netie estate

**Last updated:** 2026-08-20
**Rule:** Tier 1 roadmap only. Max 3 in Now. No dates. Problems, not features.

---

## Now

1. **DMS CI past checkout, failing mypy** - `Netie-AI/dms#1` (`feat/grounding-promote-spaces-boundary`): `contract-pin` and `protected-paths` pass; `lint-type-test` fails (19 mypy errors + import-linter debt pre-existing, unmasked once checkout works). `CORTEX_CONTRACT_TOKEN` wired at repo level because org secrets cannot reach private repos on the current plan.
2. **Cortex PR green on chore branch** - `Netie-AI/Cortex#4` (`chore/unblock-ci-and-estate-audit`): all checks pass (`lint-type-test`, `protected-paths`, `secrets-scan`, `rls-proof`). Wheel publish still blocked on dual-module identity (`Cortex#5` / EPIC-002).
3. **Founder-overridden tickets queued** - C7 (`EPIC-006`) and claim_n 47->310 (`EPIC-010`) routed from PRD-001 feedback ledger; parent to file issues. Acceptance for C7 must require a held-out real-user question set OR an adversarial corpus not written by the team.

## Next

- **Netie Control (option 3 locked)** - plane-4 client. Cortex hero + healthz + ledger probes. Goals/secrets writes 405. Heartbeat/agent-hire still live (rest of C05). GitHub Issues stay lawful.
- **Plane.so trial** - Community v1.4.1 at `http://localhost:8099`. Mapping in `D:\plane-selfhost\HOWTO.md`. GitHub Issues stay lawful until DOCUMENT_SYSTEM is amended.
- **TAS fill** - `TAS-CORTEX`, `TAS-DMS`, `TAS-SPACE` measured 2026-08-02; `TAS-OPENVAULT`, `TAS-AIRGPT`, `TAS-POINTER` still missing.
- **PRD stubs** - thin PRD-001 files for OpenVault, AirGPT, Pointer, Space, Cortex (companion to DMS); slice on next PRD Agent pass.
- **Open PRs** - Cortex #4, DMS #1 open; Cortex #2/#3 and DMS drafts remain.

## Later

- Palantir/AIP marketing parity and full column lineage (parked until paying client)
- Multi-tenant hosted DMS (self-host and single-tenant pilot only)
- Plane 1 inference build (declined - host vLLM behind OpenVault if ever needed)
