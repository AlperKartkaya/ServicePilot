# Final MVP refactor validation

2026-10-30 · solo, spec-driven local execution. Requirements: FR-9/12/14/17–21, NFR-2/4/5/7/8.

## Verified
- `uv run pytest -q`: **22 passed**. Pure RAEP, API transitions, safety gate, immutable history/human assignment, source labels and legacy source handling. API regressions now use a temporary SQLite database per test.
- `node --test tests/test_frontend.mjs`: **8 passed**. Local policy/lifecycle, confirmed seed, append-only evidence, recompute lock, safe HTML and source/snapshot rendering.
- `node --check static/app.js`, `uv run python -m compileall -q app tests`, `git diff --check -- app static specs README.md docs tests`: pass.
- Real headless Chromium: static root, isolated FastAPI fixture, and `/servicepilot/` static subpath. Each covers all seven route/subviews at **390 / 768 / 1440 px**, without document overflow or uncaught JavaScript errors.
- Browser interactions: all three direct demo buttons create real cases; evidence → new decision → human confirmation; reload persistence; historical trace/recompute; critical target and reason validation; dangerous evidence excluded; wizard validation/draft/creation; unknown case; 13-row replay; API 503 retains entered evidence and API mode without fake success.
- Keyboard: skip link preserves route, mobile drawer focus and Escape return; reduced-motion path plus a separate normal-motion drawer check. Mobile primary submit is at least 40 px high and precedes technical explanations.
- Rendered desktop/phone screenshots inspected. Artifacts: `/tmp/servicepilot-browser/`, `/tmp/servicepilot-browser-api/`, `/tmp/servicepilot-browser-pages/`. These are local evidence, not deployed screenshots.
- XERJ uses only `127.0.0.1:9327`, with feedback disabled. Project and both pinned reference repos indexed; see REFERENCE_CODING.md. Five local skills installed and used, including three frontend skills.

## Review pass and simplifications
The behavior-lock/writer plan in REFACTOR_PLAN.md preceded edits; a separate final review checked the built result against that plan.
- Removed repeated decision/evidence/approval panels and duplicate review-card detail. One main operational action remains, with complete details in native disclosures.
- Preserved static-demo compatibility and API-error fail-safe behavior; neither is an excuse to fabricate live inference or silently accept a failed write.
- Retained full signals, candidates, skipped evidence, historical settings and audit records. Unknown legacy provenance stays unknown, even on a demo case.
- Fixed the confirmed local seed reverting to pending, critical dialog's misleading optional reason/default team, mobile policy overflow, mobile submit collapse, route scroll retention, and drawer focus blocked by visibility transitions.
- Impeccable detector and Web Interface Guidelines were reviewed. Removed thick card side accents/empty preview src; retained intentional incumbent typography, native required labels, active-navigation indicator and modal elevation. This is not a claim of zero heuristic warnings or full WCAG certification.
- `app/raep.py`, `app/jev.py`, `app/store.py`, `pyproject.toml` and `uv.lock` unchanged. No framework, runtime dependency, migration or deployment added.

## Limits and incident disclosure
- **The first baseline run of the existing API tests reseeded/modified the developer's local demo database before isolation was added. No before-run backup was available.** Subsequent tests and browser runs were isolated; no later reset of that database was performed. This affects local demo records, not a deployed service.
- API browser tests use explicitly labelled fixture signals and temporary storage. They prove UI/API integration, **not a live Jev provider call**, provider latency or model quality.
- Vendored skills retain upstream whitespace and Windows CRLF; the full initial vendor diff has whitespace warnings. Application/docs/tests diff checks pass; upstream source was not reformatted.
- Existing Starlette/httpx deprecation warning remains. No project linter, TypeScript typecheck or frontend build is configured; syntax, tests and browser checks are the available gates. No tools were upgraded to silence the warning.
- No production deployment, GitHub Pages publication, Safari/device verification, real Isuzu data calibration, ProEye/DMS integration or field safety certification. Cost/reliability assumptions remain labelled assumptions.
- User's pre-existing `.gitignore` edit is preserved and excluded from commits.


## GitHub Pages deployment — 2026-10-30 [NFR-9, FR-20]
- Live URL: https://alperkartkaya.github.io/ServicePilot/ . Personal portfolio repository unchanged.
- Deployment commit: `038c685`; [successful Actions run](https://github.com/AlperKartkaya/ServicePilot/actions/runs/41056043358). Pages source is GitHub Actions; HTTPS enforced. Only `static/` is uploaded.
- Fresh local gates: 22 Python tests, 8 JavaScript tests, JS syntax, workflow YAML/artifact boundary assertions and first-party diff check passed.
- Live HTTPS check: all three assets (`index.html`, `app.js`, `style.css`) match local source SHA-256 hashes. `.env`, `data/servicepilot.db`, `app/jev.py` return HTTP 404.
- Real public Chromium check: labelled static mode; CAN scenario creation, evidence submission, routing confirmation and reload persistence passed. No page JavaScript errors or horizontal overflow at 390/768/1440 px. Only this browser context's local data changed; no server seed/reset was called.
- Screenshots: `/tmp/servicepilot-pages-live-desktop.png`, `/tmp/servicepilot-pages-live-mobile.png`.
- Actions succeeded with runner migration / Node 20 action-runtime deprecation annotations; GitHub ran those actions on Node 24. No app runtime dependencies changed.
- Scope: static, browser-local demo, not live Jev or shared server storage. Cloudflare authentication was checked, but no Worker, public paid-inference proxy, secret upload or paid resource was created. Cloudflare's free hosting does not imply free Jev inference. A live backend needs explicit access/usage limits and persistent storage; CORS alone is not access control.
- Reference: [GitHub's static publishing workflow](https://github.com/actions/starter-workflows/blob/main/pages/static.yml), adapted to upload `static/`, not the entire repository.


## Live Jev Worker extension — 2026-10-30 [FR-22]
- Worker deployed: https://servicepilot-jev.alperkartkaya.workers.dev . Real `/infer` returned HTTP 200 with `signal_source:jev` and typed signals (single diagnostic sample 143 ms, not a latency benchmark). Existing Python client also succeeded. Health/auth and anonymous 401 verified separately.
- Initial deployed call failed closed because Workers rejects Fetch `redirect:error` before sending; official runtime docs confirmed it. Regression now asserts `manual`; non-2xx redirects fail closed without forwarding the key. No provider key or request-body logs added.
- 23 Python tests including generated-contract drift; 12 frontend + 6 Worker Node tests passed. Fixture Chromium live-UI suite passed: opt-in/auth, source/latency, failed evidence write/429 retention and retry, 503 escalation without fixture fallback, safety bypass, reload session, disconnect and no token in localStorage. Static smoke also passed at 390/768/1440 px.
- Code review checked fixed upstream/model/questions, request/response size caps, bounded schema, omitted VIN/location/images, no arbitrary proxy, pre-provider safety/auth/rate checks, atomic evidence commit and recompute provenance. Password input reuses existing field styling after rendered mobile QA exposed missing type coverage.
- Only new external resource: stateless Worker + rate-limit binding; no database/subscription upgrade/add-on. Actual Cloudflare billing plan is not verifiable with current OAuth scope (subscriptions 403); usage model `standard` is verified. No zero-invoice guarantee. See WORKER.md for free-tier assumptions, approximate per-location limit and separate Jev credit cost.
- Public Pages end-to-end verification is recorded after the release below.

### Public end-to-end release verification
- [Successful Pages release](https://github.com/AlperKartkaya/ServicePilot/actions/runs/41058237608), commit `1b1babb`; Worker version `3ce6a5a6-dc9f-4bbb-8577-3db67d10cc82`. All three public assets hash-match source; access code absent from artifacts.
- Real Chromium on public Pages authenticated through the dialog, submitted evidence on the browser-local seeded CAN case, received real Jev HTTP 200 (`signal_source:jev`, single sample 132 ms), confirmed the actual RAEP route and reloaded successfully. A new case also received real live signals. No assertion forced synthetic fixture probabilities onto the provider result.
- Recompute made no new `/infer` call and kept the live provenance/human assignment. Fire scenario bypassed the Worker inference endpoint. No uncaught JS errors or horizontal overflow at 390/768/1440 px. Access code not in localStorage; auth field clears after connect.
- Public screenshots inspected: `/tmp/servicepilot-live-jev-desktop.png`, `/tmp/servicepilot-live-jev-mobile.png`; dialog fixture screenshot `/tmp/servicepilot-jev-dialog-mobile.png`. Only isolated browser-local cases changed, not any shared service database.
- Fresh isolated FastAPI browser smoke passed at all three widths; helper shut down its disposable server. No regression to API mode, and no real provider call in that fixture run.
- XERJ generation 4: 37 indexed files / 398 records, all 18 code files indexed. Only empty `app/__init__.py` is junk (exit 3, `ok=true`). No secrets/case database indexed.
- Operator code exists outside the repository with mode 600; staged actual-secret-value scan passed. Pre-existing `.gitignore` modification remains unstaged/unchanged. No production/shared storage, real customer dataset, Safari/device, rate-limit accuracy or billing invoice validation claimed.
