# TAS-UPSTREAM-LICENSES - what we may take, and how

**Checked:** 2026-09-26. Each license below was read from the repo's own `LICENSE` file on the default branch
(`raw.githubusercontent.com/<owner>/<repo>/HEAD/LICENSE*`). The GitHub API was not reachable from this session,
so the license was read directly from the file; GitHub's own SPDX detection was not used. Rows marked
**UNVERIFIED** could not be pinned to one repo. This is an engineering read, not legal advice. Get counsel to
sign off before any resale contract.

**Law (ESTATE-GAP.md line 6):** depend, port with attribution, or reimplement. Never vendor a tree, strip a
license, or put a Netie logo on someone else's product. "Clone and rebrand" is only legal for permissive code,
and even then **only the code is licensed, not the name or logo** (see the trademark section below).

Move key:
- **DEPEND**: pin it as a package or container and call it. Upstream stays upstream.
- **FORK-WITH-ATTRIBUTION**: port files or modules into our tree with LICENSE/NOTICE and headers kept, under our own name.
- **STUDY-ONLY**: read it for design, then reimplement clean. Copy no code.
- **DO-NOT-USE**: the license or provenance blocks commercial resale.

## Table

| Project | Repo URL | License (SPDX) | Resale under our brand? | Must keep | Move | Netie product |
|---|---|---|---|---|---|---|
| n8n | https://github.com/n8n-io/n8n ([LICENSE.md](https://github.com/n8n-io/n8n/blob/HEAD/LICENSE.md)) | `LicenseRef-n8n-Sustainable-Use-1.0` (fair-code, **not OSI**); `*.ee.*` files are under the proprietary n8n Enterprise License | **No.** Allowed only for "your own internal business purposes", and it may be distributed only "free of charge for non-commercial purposes" | All notices. Enterprise files need a paid license | **STUDY-ONLY** (node/credential model, execution log UX) | Constructor |
| Dify | https://github.com/langgenius/dify ([LICENSE](https://github.com/langgenius/dify/blob/HEAD/LICENSE)) | `LicenseRef-Dify-Open-Source` (Apache-2.0 **plus conditions**, so not OSI) | **Conditional/No.** Multi-tenant hosting needs written permission. You may not remove or modify the Dify logo or copyright in the `web/` frontend. The license also says the interactive design is "protected by appearance patent" | Logo and copyright in the frontend, Apache terms | **STUDY-ONLY**. At most DEPEND on the backend API single-tenant. Never rebrand the UI | Constructor, Crew |
| Haystack (deepset) | https://github.com/deepset-ai/haystack ([LICENSE](https://github.com/deepset-ai/haystack/blob/HEAD/LICENSE)) | `Apache-2.0` | Yes | LICENSE, copyright headers, a change notice on modified files, NOTICE if one ships (none at repo root). No trademark grant (Apache section 6) | **DEPEND** (`haystack-ai` pip) | Cortex (RAG / context assembly), DMS ingest |
| LangChain deepagents | https://github.com/langchain-ai/deepagents ([LICENSE](https://github.com/langchain-ai/deepagents/blob/HEAD/LICENSE)) | `MIT` | Yes | Copyright and permission notice in copies | **DEPEND** | Crew |
| "openwork": Different AI | https://github.com/different-ai/openwork ([LICENSE](https://github.com/different-ai/openwork/blob/HEAD/LICENSE)) | `MIT` outside `/ee`. `/ee` is under the proprietary OpenWork EE License (earlier `/ee` versions under `FSL-1.1-MIT`) | Yes for non-`/ee` code. **No** for `/ee` | MIT notice. Leave out `/ee` entirely | **FORK-WITH-ATTRIBUTION** (non-`/ee` only) or STUDY-ONLY | AirGPT / Space (desktop co-worker) |
| Andrew Ng: **OpenWorker** (not "openwork") | https://github.com/andrewyng/openworker ([LICENSE](https://github.com/andrewyng/openworker/blob/HEAD/LICENSE)) | `MIT` (Copyright Andrew Ng) | Yes | MIT notice | **FORK-WITH-ATTRIBUTION** (Tauri shell, approval-gated connectors) | AirGPT / Space. Its `aisuite` dependency fits FreeRoute |
| Perplexity Computer | none. Closed cloud product ([vellum.ai breakdown](https://www.vellum.ai/blog/official-perplexity-computer-breakdown)) | Proprietary | **No** | n/a | **DO-NOT-USE** as code. Competitor analysis only | Crew / AirGPT (analogue only) |
| OpenCode | https://github.com/sst/opencode (redirects to `anomalyco/opencode`; [LICENSE](https://github.com/anomalyco/opencode/blob/HEAD/LICENSE)) | `MIT` | Yes | MIT notice | **DEPEND** (or FORK-WITH-ATTRIBUTION) | Pointer |
| Kilo Code | https://github.com/Kilo-Org/kilocode ([LICENSE](https://github.com/Kilo-Org/kilocode/blob/HEAD/LICENSE)) | `MIT` (copyright Kilo Code 2026 **and** opencode 2025). The Kilo CLI is a fork of OpenCode | Yes | **Both** copyright lines | STUDY-ONLY. Fork OpenCode itself rather than a fork of it | Pointer |
| ZeroClaw | https://github.com/zeroclaw-labs/zeroclaw ([NOTICE](https://github.com/zeroclaw-labs/zeroclaw/blob/HEAD/NOTICE)) | `MIT OR Apache-2.0` | Yes | LICENSE-MIT or LICENSE-APACHE, plus **NOTICE** under the Apache option. The NOTICE says: "Any other repository claiming to be ZeroClaw is unauthorized" (trademark policy) | **FORK-WITH-ATTRIBUTION**. Never call it ZeroClaw | Crew (agent runtime), Netie Control |
| Hermes Agent (Nous Research) | https://github.com/NousResearch/hermes-agent ([LICENSE](https://github.com/NousResearch/hermes-agent/blob/HEAD/LICENSE)) | `MIT` | Yes | MIT notice | **DEPEND** / FORK-WITH-ATTRIBUTION | Crew |
| mem0 | https://github.com/mem0ai/mem0 ([LICENSE](https://github.com/mem0ai/mem0/blob/HEAD/LICENSE)) | `Apache-2.0` | Yes | LICENSE, change notices. No NOTICE at root | **DEPEND** (`mem0ai` pip). Mem0 Platform (cloud) is a separate, paid product | Cortex (memory), Crew |
| OpenWiki: **ambiguous**. Likely `langchain-ai/openwiki` | https://github.com/langchain-ai/openwiki ([LICENSE](https://github.com/langchain-ai/openwiki/blob/HEAD/LICENSE)) | `MIT` | Yes | MIT notice | **DEPEND** (CLI) | DMS (docs), Pointer. Others with the same name: `kdsz001/OpenWiki` (Mac app, not checked), `AsyncFuncAI/deepwiki-open` (not checked) |
| Orca: **ambiguous**, 3 candidates | (a) https://github.com/stablyai/orca: agent dev environment that runs 20+ coding agents in parallel. (b) https://github.com/Nethyric/orca: autonomous desktop agent. (c) https://github.com/Orkas-AI/Orkas: multi-agent desktop ("Orkas") | `MIT` for all three (copyright Lovecast Inc. / Nethyric / Orkas contributors) | Yes | MIT notice | (a) **FORK-WITH-ATTRIBUTION** if the founder meant the fleet orchestrator. (b) and (c) STUDY-ONLY. **Confirm with the founder which one** | (a) Pointer / Netie Control. (b), (c) AirGPT / Crew |
| 9router | https://github.com/decolua/9router ([LICENSE](https://github.com/decolua/9router/blob/HEAD/LICENSE)) | `MIT` | Code: yes. **Business model: no.** It advertises "unlimited FREE" Claude/GPT by relaying consumer subscription OAuth accounts, which likely breaks provider terms of service | MIT notice | **STUDY-ONLY** (format translation, fallback tiers). Do not ship subscription-account pooling | OpenVault / FreeRoute |
| OmniRoute | https://github.com/diegosouzapw/OmniRoute ([LICENSE](https://github.com/diegosouzapw/OmniRoute/blob/HEAD/LICENSE)) | `MIT`. Its README says it "started as a fork of 9router" and ports CLIProxyAPI | Code: yes. The ToS risk is the same as 9router's, plus "TLS fingerprint stealth" | MIT notices for OmniRoute **and** the upstream 9router notice | **STUDY-ONLY**. Too much pooled-account and evasion surface to sell | OpenVault / FreeRoute |
| NadirClaw / NadirRouter | https://github.com/NadirRouter/NadirClaw ([LICENSE](https://github.com/NadirRouter/NadirClaw/blob/HEAD/LICENSE)) | `PolyForm-Noncommercial-1.0.0`. Search snippets still say "MIT", which is **stale**; the LICENSE file is authoritative | **No.** The license says commercial use "requires a separate commercial license" | Required Notice | **DO-NOT-USE** (or buy a license from getnadir.com) | FreeRoute (analogue only) |
| Routerly | https://github.com/Inebrio/Routerly ([LICENSE](https://github.com/Inebrio/Routerly/blob/HEAD/LICENSE)) | `AGPL-3.0` | Only if we publish all source of the combined work, **including to network users** | Full source disclosure of derivatives, AGPL notice | **DO-NOT-USE** in a closed product. STUDY-ONLY for its scoring policies | FreeRoute |
| auto_ai_router | https://github.com/MiXaiLL76/auto_ai_router ([LICENSE](https://github.com/MiXaiLL76/auto_ai_router/blob/HEAD/LICENSE)) (original. Forks such as `Vadzimik977/...` are copies) | `Apache-2.0` | Yes | LICENSE, change notices. No NOTICE file | **DEPEND** (container `ghcr.io/mixaill76/auto_ai_router`) or FORK-WITH-ATTRIBUTION (Go: rate limiting, fail2ban) | FreeRoute |
| Openship | https://github.com/oblien/openship ([LICENSE](https://github.com/oblien/openship/blob/HEAD/LICENSE)) (self-hosted deploy platform. **Not** `openshiporg/openship`, which is e-commerce fulfilment and was not checked) | `Apache-2.0` | Yes | LICENSE, change notices | **DEPEND** | DMS / Cortex deploy (appliance installs), Netie Control |
| "openwillow" | **NOT FOUND.** No repo by this name. Nearest: `HeyWillow/willow` (voice assistant, `Apache-2.0`, [LICENSE.md](https://github.com/HeyWillow/willow/blob/HEAD/LICENSE.md)) and withwillow.ai (a commercial agent-governance SaaS, not OSS) | UNVERIFIED | n/a | n/a | **Ask the founder** for the URL | Netie Control? (if it means Willow governance) |
| Zillow | n/a. A real-estate **company**, not an OSS project | Proprietary. Its name and data are protected | **No** | n/a | **DO-NOT-USE**. If this was a typo, ask the founder | none |
| DeepSeek "harness" | https://github.com/deepseek-ai/deepseek-harness ([LICENSE](https://github.com/deepseek-ai/deepseek-harness/blob/HEAD/LICENSE)) (`dsh`, plugin agent harness on Cordis, developer preview) | `MIT` (copyright DeepSeek) | Yes | MIT notice. The hosted service has its own data-processing terms ([deepseek.com/harness](https://www.deepseek.com/harness/en/data-processing/)) | **DEPEND** / STUDY-ONLY (developer preview, still changing fast) | Crew, Constructor (plugin model) |
| grok-bot-0.18-reconstructed | https://github.com/b-nnett/grok-bot-0.18-reconstructed | **None.** There is no LICENSE file, so all rights are reserved. It is a reconstruction of a proprietary app, and it downloads and extracts the vendor's shipped binary | **No** | n/a | **DO-NOT-USE** (read the design notes only, as ESTATE-GAP says) | Pointer (analogue only) |

## Fastest legal path per Netie product

- **Constructor:** n8n and Dify cannot be rebranded. Build on an MIT/Apache engine and draw the canvas ourselves. The DeepSeek harness plugin model and Haystack pipelines are the substrate. Study n8n's UX only.
- **Crew:** DEPEND on `deepagents` (MIT) plus `hermes-agent` (MIT) plus `mem0` (Apache). Port ZeroClaw modules with LICENSE and NOTICE kept.
- **Pointer:** fork OpenCode (MIT) under a Netie name and keep the opencode copyright line. Take `stablyai/orca` patterns if multi-agent fleets are in scope.
- **OpenVault / FreeRoute:** DEPEND on or port `auto_ai_router` (Apache) for load balancing, rate limiting and bans. Study 9router and OmniRoute for format translation only. Never pool consumer subscriptions. Skip NadirClaw (noncommercial) and Routerly (AGPL).
- **Cortex / DMS:** DEPEND on Haystack and mem0 through pip pins. Docs via `langchain-ai/openwiki` CLI. Appliance deploy via Openship (Apache) as an external tool.
- **AirGPT / Space:** fork `andrewyng/openworker` (MIT) or the non-`/ee` parts of `different-ai/openwork` (MIT), then rebrand the shell and keep both notices.
- **Netie Control:** no direct OSS match was found. The Orca fleet orchestrator (`stablyai/orca`, MIT) is the closest pattern. Resolve "openwillow" with the founder first.
- **Every fork:** add `THIRD_PARTY_NOTICES.md`, keep upstream LICENSE/NOTICE files and headers verbatim, and run a license scanner (e.g. `pip-licenses` / `license-checker`) in CI so a transitive AGPL or noncommercial dependency fails the build.

## Names are trademarks even when the code is permissive

MIT and Apache-2.0 license **copyright**, not **marks**. Apache-2.0 section 6 says so explicitly, and MIT is silent,
which grants nothing. A fork **must not** use the upstream name or logo, e.g. "n8n", "Dify", "OpenCode", "Kilo",
"ZeroClaw", "Hermes", "mem0", "Haystack", "Orca", "9router", "OmniRoute", "DeepSeek", "Perplexity" or "Zillow".
That includes product names, package names, domains and marketing copy like "Netie ZeroClaw". A plain factual
attribution line ("based on OpenCode, MIT") is fine and is required. ZeroClaw's NOTICE states outright that any
other repo claiming the name is unauthorized. Dify's license goes further and forbids removing its logo from the
frontend, so a Dify UI cannot be rebranded at all. "Rebrand" therefore means **new name, new logo, notices kept**:
it never means "their product with our logo".
