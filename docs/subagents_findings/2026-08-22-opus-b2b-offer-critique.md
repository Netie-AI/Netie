# Opus B2B AI offer critique

- Date: 2026-08-22 UTC
- Model: Claude Opus
- Scope: `docs/pay.html`, resume-backed service positioning, public-demo honesty
- Keywords: b2b-positioning, landing-page-critique, netie-hire-page, pay.html, evidence-led-claims, rag-document-search, constructor-dag, screenshot-gallery, demo-honesty, penang-sme, stripe-pricing, scope-boundaries, overclaim-removal
- Main idea: Position Jian as a one-engineer provider of small, evidence-led AI systems over customer documents and processes. Sell only what the resume and public artifacts support; label public concepts as concepts; put proof before payment.

## Critical evidence found

- Constructor on GitHub Pages is browser-only and its status says `Sketch (no fetch)` when not running on its backend origin. It should be called an interactive process sketch, not an executing production agent.
- `app.netie.ai/cortex` returned 404. The `Chat with Cortex` control on the public Netie site does not establish a public live agent demo.
- Cassandra self-labels as illustrative until archives are wired.
- AIM is a file-intake surface, not public proof of cited retrieval.
- ASA is a pre-order landing page with checkout, so it is useful proof of landing-page craft, not proof of product delivery or buyer adoption.
- The public Netie homepage contains enterprise and performance assertions that should not be used as the primary proof destination until separately reconciled.

## Positioning statement

I build small, private AI systems over your own documents and processes for Penang SMEs and manufacturers: search that cites its source, workflows you can dry-run before you fund a build, and pages that say what your company actually does, delivered as files you own.

## Three credible buyer problems

### 1. Find the spec, not the folder

- Buyer: engineering, QA, or applications managers at Penang E&E suppliers, distributors, or contract manufacturers with PDF-heavy shared drives.
- Deliverable: private search-and-answer app over an agreed PDF corpus, FastAPI plus retrieval plus web UI, Dockerized for a customer machine. Answers return file name, page, quoted line, or abstain.
- Boundary: one corpus, up to 500 documents, one source folder/export. No ERP/PLM writes, fine-tuning, SSO, uptime SLA, or unattended re-indexing.
- Truthful evidence: Jumpwin datasheet RAG experience is resume-backed. AIM is only a public intake-surface sample, not a public retrieval demo.
- Landing headline: `Find the spec, not the folder.`
- Copy: `Point it at your datasheet drive. Ask in plain English. Every answer comes back with the file, the page, and the exact line. If the answer is not in your documents, it says so instead of inventing one.`

### 2. See the system before you pay for the system

- Buyer: operations managers or owner-directors of Malaysian SMEs that run a process through spreadsheets, WhatsApp, and individual memory.
- Deliverable: one process mapped as a runnable decision graph in Constructor, dry-run against 20-30 sample records, plus a written spec of tables, screens, roles, and failure cases plus exported JSON.
- Boundary: one process, up to 12 nodes, sample records only. No production deployment, integration, or migration in this stage.
- Demo: https://netie-ai.github.io/constructor/
- Landing headline: `See the system before you pay for the system.`
- Copy: `I map one real process as a graph you can open, edit, and dry-run. You get the spec, the failure cases, and the JSON. If the build is wrong, you find out here, not after RM 20,000.`

### 3. A page that says what you sell

- Buyer: Malaysian SME owners or marketing leads with an outdated site or a product needing a credible first landing page.
- Deliverable: one hand-coded responsive page from published facts, with enquiry form or Stripe button, files handed over, one revision.
- Boundary: one page, no CMS, no blog, no hosting, no invented claims, one revision within seven days.
- Demo: https://netie.ai/asa/ and the hire page itself.
- Landing headline: `A page that says what you sell, and takes the money.`
- Copy: `One page, written from facts already on your site, with a working enquiry form or Stripe button. Hand-coded HTML, no template. You get the files and host them yourself. One revision. RM 500.`

## Paste-ready hero and proof copy

Kicker:

`PENANG, MALAYSIA - JIAN HONG OO`

Hero:

`AI that shows you where the answer came from.`

Subhead:

`I build three things for Malaysian SMEs and manufacturers: private search over your own documents that cites the file and page, process prototypes you can dry-run before funding a build, and one-page sites that state what you actually sell. One engineer, fixed scope, files handed to you.`

Micro-proof line:

`Everything below links to something you can open right now. Where a demo is a sketch or a mock, the caption says so.`

Proof heading:

`Open the work. Including the parts that are not finished.`

Proof subhead:

`Real screenshots, each linked to the live page. No stock mockups.`

Suggested CTA labels:

- `Request a written scope`
- `Open the live demos`
- `Send 5 files, get a sample answer`
- `Map one process`
- `Buy the RM 500 page`
- `Discuss the system`
- `WhatsApp me the brief`

## Claims and content to remove or soften

- Replace `Your AI solution company` with a buyer outcome.
- Use `I` for Jian's delivery rather than `we` and remove `the model`, which implies model training that is not demonstrated.
- Remove `Every product below has a public demo URL`; a clickable URL is not necessarily a production demo.
- Describe Cortex only as a product-interface concept until a verifiable public execution URL exists.
- Describe Constructor as a browser-based process sketch / dry-run, not an agent runner.
- Do not use Cassandra as proof of analytics delivery because it labels itself illustrative.
- Use ASA only as proof of a landing page with a checkout / intake interaction, explicitly noting it is an unreleased pre-order.
- Treat AIM as a file-intake UI sample, not proof of a working retrieval backend.
- Do not link the primary CTA to a page containing unsupported performance, security, or enterprise claims.
- Remove the Twine day rate from beside high-ticket price buttons, because it creates an unhelpful comparison.
- Replace CSS mockups with real screenshots.
- Move proof above payment. Do not invite a stranger to card RM20,000 before a written scope.
- Add delivery windows, acceptance terms, and any explicit refund / correction policy that Jian can actually honor.
- Keep text laptop-ASCII.

## Screenshot gallery plan

| Source | Capture | Honest caption | Supports |
|---|---|---|---|
| https://netie-ai.github.io/constructor/ | Canvas with nodes wired and inspector visible | `Constructor: a process graph you can drag, rewire, and read. Open the live browser sketch.` | Process prototype |
| https://netie-ai.github.io/constructor/ | Audit / ghost-run area and export UI | `Ghost run and audit surface. This public build runs in your browser and makes no server calls.` | Process prototype |
| https://netie.ai/aim/ | Digital Twin Intake upload block | `File-intake surface I built. It shows the front door of a document workflow; the retrieval engine is not public.` | Document-search quote |
| https://netie.ai/asa/ | Pre-order card with details form and checkout CTA | `Landing page with working intake and checkout. This is an unreleased product pre-order, not a record of sales.` | RM500 landing page |
| https://netie.ai/ | Cortex / node-flow panel | `Public product-interface concept I designed. This marketing-site panel is scripted, not a live agent run.` | Page / interface craft |

The strongest future proof image would be a real source-trace result over a public spreadsheet or datasheet, showing file, sheet/page, formula/quote, inputs, and verdict. It does not yet exist as a truthful public demo.
