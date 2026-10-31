# Documentation media

- `servicepilot-mark.svg`: existing `static/assets/logo.svg` monogram on a dark tile. Original paths; no new brand mark.
- `landing.webp`: actual **local** Chromium screenshot at `http://127.0.0.1:5187/`, 1440×960, captured 2026-11-01 with the selected headline **HER DURUMDA, HIZLA SIRADAKİ ADIMA**. Refined headline: 69.12px at 1440px viewport (line-height 1.14), 38.22px at 390px (line-height 1.16). WebP quality 92. No compositing or UI reconstruction; this is not a published-release capture.
- `live-demo.webp`: unchanged screenshot of published release `0228975`, 1440×960, captured 2026-10-31. One synthetic CAN case received real anonymous Jev HTTP 200 (`signal_source:jev`). Probability and latency describe that single example, not accuracy/speed benchmarks. WebP quality 94; no real customer data.
- `decision-flow.svg`: **original README flow design, unchanged**. Jev produces signals; RAEP selects the action; safety rules bypass Jev. Expert diagnosis, human confirmation and actual delivery are not automated by this diagram.
- `architecture-components.svg` and `architecture-decision.svg`: custom vector diagrams with plain Turkish labels, authored against `app/main.py`, `app/jev.py`, `app/catalog.py` and `app/raep.py`. No Mermaid. Avenir Next with Arial/sans-serif fallbacks; warm paper, green for useful progress, amber for a check and coral for human intervention. Safety, unavailable inference, evidence loop, request limit and hierarchical fallback remain explicit.
- `architecture-*.png`: 2× raster renders of those SVG sources, embedded directly in `specs/ARCHITECTURE.md` for Markdown-preview compatibility. PNG metadata records source and render provenance. Use the linked SVG to inspect at any zoom.

The landing screenshot is sourced from `/tmp/servicepilot-new-heading-1440.png`; the unchanged demo screenshot was sourced from `/tmp/servicepilot-release-demo.png`. No provider call was needed for this update. The truck is a labelled generated concept visual, not a partner vehicle; its original prompt is in `static/assets/service-truck.webp.json`.

## Regenerate

Formulas use Typst 0.14.2 with embedded Libertinus Serif / New Computer Modern Math and Arial headings. Calligraphic `𝒮_e` is the evidence leaf set; plain `S_e` is safety/operation cost. The notation does not change RAEP.

```sh
typst compile docs/assets/raep-formulas.typ 'docs/assets/raep-formula-{p}.svg'
# librsvg 2.62.0; Avenir Next installed on the macOS rendering host:
for name in architecture-components architecture-decision; do
  rsvg-convert --zoom 2 "docs/assets/$name.svg" -o "docs/assets/$name.png"
done
```

Edit the SVG sources directly, then regenerate the PNGs; keep the source/render provenance in PNG metadata via `impeccable embed-prompt` after rendering. No diagram dependency or build step is added to the app. See [Typst math](https://typst.app/docs/reference/math/) for formula syntax.

## Verification

2026-11-01: 23 Python and 25 Node tests passed (one existing Starlette/httpx deprecation warning). Landing browser checks passed at 1440/768/390px, including six chapters, safety toggle, reverse navigation, reduced motion, short screens, missing JS/vendors and old demo links; zero provider calls. The new headline also fits at 320px. Diagram text containment, SVG XML, PNG sizes, image links and local GFM light/dark previews at 1000px and 390px are checked. The original README decision-flow SVG is unchanged. These checks do not prove a public deployment.
