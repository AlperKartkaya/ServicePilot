# Scroll landing — FR-23 / NFR-10

`static/index.html` is an independent, local-only narrative. `demo/index.html` preserves the operational MVP at `demo/`; old app hashes and `app.html` redirect there with query/hash intact. No endpoint or persistence contract changes. The local preview is `python3 -m http.server 5187 --bind 127.0.0.1 --directory static`.

## Reference coding

Before implementation, the local XERJ project index and cloned Lenis/GSAP indexes were queried for ticker integration, ScrollTrigger scrub and matchMedia cleanup. See [reference setup](REFERENCE_CODING.md) and `static/vendor/README.md` for versions and licenses. Lenis uses GSAP's ticker, not a competing animation loop; `syncTouch` remains off. The narrative is native sticky positioning plus one scrubbed timeline. GSAP matchMedia restores linear reading on reduced motion or short screens; unavailable animation scripts also leave a complete reading view.

## Product boundaries

The synthetic CAN case comes from the existing application fixture. `landing-case.js` invokes the actual shared `jsDecide` policy for the evidence request, final route and safety counterfactual. The application bootstrap exits on pages without `.app-shell`. Landing replay neither calls Jev nor saves/overwrites cases. The displayed probabilities are fixture values, not model accuracy. Photo/multimodal analysis is a product direction, not a claimed shipped capability. Anadolu Isuzu PoC is a target, not a completed collaboration. The risk alternative starts again from the first note and bypasses Jev; no real expert receives a handoff.

## Assets

- `assets/logo.svg`: existing user-provided root logo, copied without changing the source.
- Manrope variable Latin/Latin-ext fonts: Google Fonts Manrope v23, self-hosted; OFL text in `assets/Manrope.LICENSE.txt`.
- `assets/service-truck.webp`: original AI-generated unbranded concept vehicle, not an actual partner vehicle. Generated at 1536×1024, converted with `cwebp -q 86`; exact prompt below. No third-party stock image or vehicle endorsement.

### Exact image-generation prompt

Create a premium automotive studio photograph for the ServicePilot startup landing page, a commercial vehicle technical-service decision system. Wide landscape 1536x1024 composition. A single completely unbranded contemporary silver graphite medium-duty commercial rigid truck, short modern cab, large clean enclosed cargo body, three-quarter FRONT LEFT view, vehicle facing LEFT. Not a pickup or semi trailer. Object occupies the right 75% and bottom 75% of the image with generous black negative space in the upper left. Extreme dark studio backdrop, near-black (#080b0c) ground and background blend together, no visible horizon. Beautiful realistic brushed silver metal, tightly controlled pale mint rim light along cab and box upper edges, soft neutral white key light on front, understated tire and headlight detail, subtle grounding shadow, no glossy mirror-floor reflection. Elegant cinematic industrial photography, high-end physical product launch, crisp believable mechanical forms. Nothing written anywhere, no badges no car brand logos, no floating graphics, no grids no UI, no roads no humans no scenery, no neon glow or sci-fi objects. This is a concept illustration, not a photo of an actual partner vehicle. Save usable standalone website raster asset.

## Verification

Fresh local results: 24 JS tests and 23 Python tests pass (one existing Starlette/httpx deprecation warning). Chromium passes six-step narrative, keyboard risk toggle/chapter links, reverse navigation, 390/768/1440px layouts, reduced-motion preference changes, short-screen linear reading, unavailable vendors, no-JS reading and legacy deep links, both demo CTAs and the new demo directory asset paths. Existing static, isolated API-fixture and mocked-public-Jev application browser suites pass. Root and `/servicepilot/` backend paths were smoke-checked. These local checks do not establish live provider availability or successful deployment.

```sh
node --test tests/test_frontend.mjs tests/test_landing.mjs tests/test_worker.mjs
uv run pytest -q
# With loopback static server on 5187:
uv run --with playwright python tests/browser_landing.py
uv run --with playwright python tests/browser_smoke.py
uv run --with playwright python tests/browser_jev_smoke.py
```

Browser fixtures/mocked provider responses do not establish live Jev availability, deployment or field performance. Screenshot artifacts are ignored under `.impeccable/review/`.
