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
