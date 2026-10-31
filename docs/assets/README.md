# README media

- `servicepilot-mark.svg`: existing `static/assets/logo.svg` monogram, unchanged paths, on a dark tile for GitHub light/dark readability. No new brand mark.
- `landing.webp`: unaltered viewport screenshot of the published landing, 1440×960, captured 2026-10-31 during release verification of `0228975`. WebP quality 92.
- `live-demo.webp`: unaltered viewport screenshot of the same published release's operational demo, 1440×960. One synthetic CAN case received real anonymous Jev HTTP 200 (`signal_source:jev`). WebP quality 94. Displayed probability and latency belong to that single illustrative case, not a performance/accuracy benchmark. No real customer data.
- `decision-flow.svg`: original hand-authored vector description of the existing `app/jev.py`, `app/raep.py` and static/Worker flow. No measured results or performance figures. Safety rules bypass Jev; ordinary evidence updates re-enter the safety check and sensor/policy loop. ROUTE is an expert-team recommendation requiring confirmation, not automatic diagnosis or repair.

Screenshots are re-used from the verified release captures `/tmp/servicepilot-release-landing.png` and `/tmp/servicepilot-release-demo.png`; they were not generated or reconstructed. No further provider request was made to create README media. The landing's representative truck is an original generated concept image; its prompt provenance is in `static/assets/service-truck.webp.json`.

## Regenerate

The original README flow SVG is preserved. Architecture diagrams use native Mermaid blocks; formulas use Typst 0.14.2 (embedded Libertinus Serif / New Computer Modern Math; Arial for headings). The calligraphic `𝒮_e` is the evidence leaf set; plain `S_e` is the safety/operation cost. This disambiguates the notation without changing RAEP.

```sh
typst compile docs/assets/raep-formulas.typ 'docs/assets/raep-formula-{p}.svg'
# Mermaid CLI 11.12.0 (documentation tooling only, not an app dependency):
npx --yes @mermaid-js/mermaid-cli@11.12.0 \
  -i specs/ARCHITECTURE.md -o /tmp/servicepilot-architecture.svg
```

For an existing Chrome/Chromium installation, pass `-p /path/to/puppeteer.json` containing `{"executablePath":"/absolute/path/to/chrome"}`. No browser path or tooling dependency is added to the app. Native Mermaid blocks in `specs/ARCHITECTURE.md` render directly on GitHub.

Sources: [Typst math](https://typst.app/docs/reference/math/), [Mermaid flowcharts](https://mermaid.js.org/syntax/flowchart.html), [Mermaid CLI](https://github.com/mermaid-js/mermaid-cli).

## Verification

Screenshot provenance above is unchanged. Formula SVGs compile from the checked-in Typst source; both architecture Mermaid blocks render through Mermaid CLI. The README decision SVG retains its original design. Relative links and SVG XML are checked. Light/dark and mobile local GitHub-Markdown previews are reviewed; runtime files are unchanged. Fresh checks: 23 Python tests and 24 Node tests passed; one existing Starlette/httpx deprecation warning. Both Mermaid blocks render, the three Typst SVGs reproduce byte-for-byte, relative links resolve, and all images load in light/dark previews at 1000px and 390px without document overflow. These are local GFM previews, not a live-browser release check.
