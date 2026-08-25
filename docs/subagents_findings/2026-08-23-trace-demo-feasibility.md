# Trace demo feasibility audit

- Date: 2026-08-23 UTC
- Model: Claude Opus
- Scope: `scripts/trace_number.py`, sample fixtures, existing RM1,500 file-analysis offer
- Keywords: number trace, source trace, evidence demo, reproducible proof, xlsx parsing, shared formulas, number formats, abstain over guess, static hire page, RM 1500 file analysis
- Main idea: `trace_number.py` is safe but not sellable evidence until it resolves shared formulas, labels raw values honestly, resolves inputs, and cleanly refuses unsupported cases. A reproducible synthetic trace page can support the existing RM1,500 service without reviving a low-price headline.

## Current audit

The script accepts a `.csv` or `.xlsx` path plus `F14` or `Sheet1!F14`, emits a fixed human-readable block, and makes no network calls, subprocess calls, writes, telemetry, or temp files. Its standard-library-only design is a strong fit for a local-file evidence tool.

The current output is not reliable enough to sell:

- A shared-formula child can be reported as `typed, no formula` even though it is a formula.
- `Value as shown in the file` is false for formatted dates, currency, percentages, and rounded cells because styles are not applied.
- Inline strings and booleans are mishandled.
- Quoted sheet names and case-insensitive sheet references fail.
- An invalid zip with a `.xlsx` suffix raises a traceback.
- Parser limitations and genuinely untraceable figures collapse into the same response.
- It never lists the cells feeding a `SUM` formula or recomputes the value.

The current fixtures also need replacement or alignment. The xlsx contains sparse cells without business labels; the CSV and xlsx totals do not agree under the shared `sample-outbound` name.

## Recommended artifact

Build one static, buyer-reproducible source-trace page:

1. A synthetic weekly outbound workbook that opens without repair and has headers, labels, a shared `SUM` formula, and one deliberately typed/untraceable figure.
2. The exact downloadable script and workbook.
3. Verbatim captured output for a traced value, including formula, inputs, recomputation, and verdict.
4. A second captured output where the tool visibly refuses a typed figure.
5. A short "verify this in 60 seconds" path and explicit limits.

Primary target: `https://netie.ai/hire/trace/`. It is proof for the existing RM1,500 file-analysis service, not a separate Number Trace product and not a headline price anchor.

## Minimum acceptance bar

- Resolve shared formulas rather than labelling them typed.
- Make raw/display limitations explicit rather than claiming display fidelity.
- Resolve simple `SUM(range)` input cells and compare the sum against the cached value.
- Cleanly reject bad xlsx files, malformed cell refs, unsupported formula shapes, and untraceable values.
- Use nonzero exit status for an untraceable result and a distinct usage-error status.
- Use a synthetic workbook only; make no accuracy, benchmark, client, security, or revenue claim.
- Keep the page static and dependency-free, readable without JavaScript, and link it to the RM1,500 service only after it passes tests.
- Publish both the page and any mirror before adding it as a homepage CTA.

## Landing copy if the artifact passes

Hero secondary CTA:

```html
<a class="btn ghost" href="#proof">See a figure traced</a>
```

Proof block:

```html
<section id="proof">
  <p class="kicker">Reproducible proof</p>
  <h2>One figure, traced to its source.</h2>
  <p class="section-copy">Download the sample workbook, run one command, and get the value, formula, cells that feed it, and a verdict. The page also shows a figure the tool refuses to trace.</p>
  <div class="notice">Synthetic sample data. No client file, no backend, and no accuracy claim. The tool reads .xlsx and .csv only.</div>
  <div class="cta">
    <a class="btn" href="https://netie.ai/hire/trace/">Open the source trace</a>
  </div>
</section>
```

## Risks

- The source-trace proof must remain evidence for the RM1,500 service, not revive a RM300 headline.
- Publishing before shared-formula, input-resolution, and refusal fixes would harm credibility.
- The artifact should explicitly list unsupported formats and formula shapes.
- A dead hosting path would damage trust; verify the deployed URL before linking it from the hire page.
- This work should not displace scheduled weekday outreach.
