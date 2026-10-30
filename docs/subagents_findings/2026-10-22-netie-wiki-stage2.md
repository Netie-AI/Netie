# 2026-10-22 - Netie Wiki stage 2 (OpenWiki gate wired and tested)

Preflight: KB `D:\Netie-KB` absent in this cloud box. `docs/subagents_findings/INDEX.md`
and both findings it lists were read, plus the wave 1 airgpt, freeide and freeroute
findings on their branches. PREFLIGHT: PARTIAL. No subagents spawned; one session did
clone, build, edit, test and patch-cut directly.

Session history: started 2026-10-22, halted by the founder mid-edit the same day,
resumed 2026-10-28 on a relayed message that the halt was lifted and a direct
"Continue" from the user. The /tmp clone and its baseline commit survived the halt; no
work was redone.

Branch `claude/stage2-netie-wiki`, base `claude/netie-ecosystem-rebrand-uq9q3z` (PR #43).
Upstream langchain-ai/openwiki at c0173dca92 (MIT), overlay
`ecosystem/overlays/netie-wiki/0002-gate.patch`.

## F1. Grounded Claims had no tie to Netie-KB and no label for "not grounded"

- **Expected (catalog gate):** every grounded claim the CLI writes carries a Netie-KB id
  in the shape `scripts/kb_lookup.py` returns; a claim without one is labeled ungrounded.
- **Actual on stage 1:** the sidecar `openwiki/.claims/<page>.json` holds
  `{id, statement, evidence}` only. Nothing says whether a claim rests on a KB row.
- **Fix:** `kbId` on the agent's `submit_page` schema, carried through page-job
  reconciliation and the claims mutation layer to a resolver over `NETIE_KB_INDEX`
  (a TypeScript port of `kb_lookup.show_brief` and `lookup`, `src/netie/kb.ts`). The
  store writes `grounding: "netie-kb"` with a `kb` brief, or `grounding: "ungrounded"`,
  on every claim. An unknown id or a skill row carrying a body throws, so a bad id is
  never silently dropped to ungrounded.
- **Repro:** `clone` + `apply` into D, `pnpm install --frozen-lockfile`, then
  `npx vitest run test/netie/netie-wiki-gate.test.ts`. Cases 1 to 4 drive the real
  `prepareClaimsRuntime`, `reconcilePageClaims` and `finalize` and read the sidecar JSON.
- **Root-cause class:** provenance without custody: evidence was versioned, but which
  authority vouches for a claim was not recorded at all.
- **Invariants:** assert the artifact the customer receives (the sidecar on disk);
  silent fallback is a lie (unknown ids refuse, ungrounded is written as a label).

## F2. An ambient provider key routed model calls around any vault

- **Expected (NETIE.md section 3):** one key vault; model calls go to OpenVault `/v1`.
- **Actual on stage 1:** with `OPENWIKI_PROVIDER` unset, `resolveConfiguredProvider`
  picks a direct provider from whichever key is in the shell (`OPENAI_API_KEY`,
  `OPENROUTER_API_KEY`, `NVIDIA_API_KEY`, a Bedrock pair, and others). Measured: the gate
  test's model-call case on the stage 1 tree sent its request to api.openai.com, which
  answered `401 Incorrect API key provided: sk-must-*****eave` (the test's fake value).
  All three example workflows shipped `OPENROUTER_API_KEY` and LangSmith keys.
- **Fix:** provider `openvault` (default), endpoint `${NETIE_OPENVAULT_URL}/v1`, default
  `http://127.0.0.1:5000`, model `auto` (OpenVault's catalog pick per
  `TAS/TAS-OPENVAULT.md`), placeholder key `openvault`. Ambient-key auto-select removed:
  a direct provider runs only when `OPENWIKI_PROVIDER` names it. Example workflows set
  `OPENWIKI_PROVIDER: openvault` and no key. README model-provider section rewritten.
- **Repro:** gate cases 5 to 7. Case 6 runs a local HTTP stub as OpenVault and asserts
  the one request is `POST /v1/chat/completions` with `Authorization: Bearer openvault`
  and that an ambient `OPENAI_API_KEY` value appears nowhere in it.
- **Root-cause class:** convenience fallback standing in for a routing decision.
- **Invariants:** silent fallback is a lie; prove a gate can fail (12 of 12 red on base).

## F3. Source connectors and MCP tools left the machine with no gate

- **Expected (`TAS/TAS-SPACE.md`, `scripts/space_leave.py`):** a personal source is read
  only after OpenVault leave-machine allows it; off by default with a visible label.
- **Actual on stage 1:** Gmail, Slack, X, Notion, custom MCP, web search, Hacker News
  and LangSmith pull as soon as they are configured. Two egress paths exist: connector
  `ingest`, and the MCP runtime the agent calls directly (`discoverMcpConnectorTools`,
  `callMcpConnectorTool`), which never goes through `ingest`.
- **Fix:** both paths ask `POST ${NETIE_OPENVAULT_URL}/api/crew/gate` with
  `{kind: service, id: wiki.connector.<id>, intent: leave, parent_run_id, child_id,
  deficit}` (the `crew_ov_gate.py` body) and proceed only on `allowed: true`. Missing
  OpenVault, transport error, non-2xx, or `allowed` not exactly `true` is a refusal.
  Refused ingest returns `skipped` with the label, the URL asked and the reason;
  refused MCP calls throw the same text. `git-repo` (local) is the only ungated one.
- **Repro:** gate cases 8 to 11.
- **Root-cause class:** egress enumerated per entry point instead of at the boundary;
  the MCP path would have stayed open had only `ingest` been wrapped.
- **Invariant:** a control that blocks legitimate work is a failure, so an OpenVault
  allow is tested to run the connector (case 10), not only the refusal.

## F4. Build and test, before and after

Measured on this box (4 cores, 15 GB, Node 22.22.0, pnpm 11.25.0). Upstream's documented
gate is `pnpm test` = typecheck + build + coverage; the same three steps were run
separately, plus upstream `eslint .` and `prettier --check .` after.

| Step | Before (stage 1) | After (0002) |
|---|---|---|
| `pnpm install --frozen-lockfile` | exit 0, 20 s | not re-run (lockfile unchanged) |
| `pnpm run typecheck` | exit 0, 17 s | exit 0, 12 s |
| `pnpm run build` | exit 0, 17 s | exit 0, 13 s |
| `npx vitest run` | 3389 passed, 3 skipped, 0 failed, 98 s | 3401 passed, 3 skipped, 0 failed, 76 s |
| gate test alone | 12 of 12 failed | 12 of 12 passed (also in the replayed tree) |
| `eslint .`, `prettier --check .` | not run | exit 0, exit 0 |

- The +12 is exactly the gate suite. The 3 skips are upstream's own live evals, the same
  three before and after. No skip added.
- 17 upstream tests failed on the first after-run and were changed, none deleted:
  - 4 in `test/config/constants.test.ts` asserted ambient-key auto-select (F2). Each now
    asserts the same input resolves to `DEFAULT_PROVIDER`.
  - 8 in `test/connectors/mcp-runtime.test.ts` and 1 in `test/ingestion/code-mode.test.ts`
    test upstream logic that now sits behind the gate. Those two files mock the OpenVault
    answer to `allowed` in the upstream's own `vi.mock` style. The gate code itself still
    runs, and the gate suite covers it directly.
  - 2 brand assertions in header and first-run notice tests now read `PRODUCT_NAME`.
  - 1 sidecar round-trip in `store.test.ts` now expects the `ungrounded` label on disk.
  - 1 error-text assertion in `mutations.test.ts`: the new message keeps upstream wording.
- Built CLI measured: `node dist/cli/cli.js --help` prints
  `Netie Wiki v0.7.0`, `provider: OpenVault (Netie)`, `model: auto`.

## F5. Patch replay

- `0002-gate.patch` is `git diff --binary --cached` against the stage 1 tree: 94,496
  bytes, 32 files, 1374 insertions, 321 deletions. A fresh `clone` + `apply` gives the
  same `git write-tree` as the edited tree: `214d44def7a6aa5270e5dbfaa13f2da1088a69fa`.
  LICENSE sha256 `1126322e...ef685` unchanged and equal to the catalog.
- Catalog stage set to 2 only after F1 to F5 held.

## Not done / assumed

- **Not measured:** a live OpenVault. Whether `/v1` wants a seat token, whether it serves
  `/v1/models`, whether `model: auto` is accepted live, and whether `/api/crew/gate` is on
  OpenVault main. All are read from `TAS/TAS-OPENVAULT.md` and `scripts/crew_ov_gate.py`.
- **Not done (stage 3):** package name, `openwiki` binary, `~/.openwiki` home,
  `openwiki/` wiki directory, `OPENWIKI_*` env names, producer actor `openwiki/<version>`,
  ASCII logo, telemetry copy. The example workflows install the upstream npm package
  `openwiki`, which lacks this gate, because no Netie Wiki package exists.
- **Flagged, out of scope:** telemetry to PostHog is on by default upstream and is not
  routed through OpenVault leave-machine. OAuth login flows (`openwiki auth`) reach
  providers directly; they set up credentials and move no source data.
- **Assumed:** OpenVault and the KB index are local. A hung OpenVault costs up to 5 s per
  connector per run (gate timeout); a refused port fails immediately.
- **Unchanged, reported as asked:** `scripts/test_sibling_patches.py` is red on base and
  on this branch, F2 of `2026-10-05-ecosystem-lane.md`. Measured 2026-10-28: 9 of 10 fail
  on both, one more than the 8 recorded on 2026-10-05 (the siblings kept moving). So
  `scripts/check_docs.py` and `make ci` exit 1 for that reason only. Not touched, not
  skipped.
- `INDEX.md` and `STATUS.md` not edited; the parent aggregates them.
