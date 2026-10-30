# MVP flow refactor

## Scope and behavior lock
- Requirements: FR-9, FR-12, FR-15–20, NFR-5–8; add FR-21 for the visible Jev/RAEP decision trace.
- Keep Python RAEP math, API actions, evidence validation, human review, drafts, local storage, replay and all five screens.
- Touch the three static assets, signal provenance in API/seed steps, regression tests, and their specifications. No framework, new runtime dependency, database migration or production deployment.
- Baseline: `uv run pytest -q`: 18 passed (2026-10-30 local date).
- Add dependency-free JS regression checks before replacing the case renderer. Use real browser flows afterward.

## Cleanup order
1. Preserve API failure escalation and explicit static-demo mode. They are grounded fail-safe/compatibility paths, not fallbacks to delete.
2. Replace repeated next-action, missing-evidence and approval panels with one operational action. Never call an uncertain or escalated case “evidence sufficient”.
3. Surface Jev probabilities and RAEP's selected evidence/value calculation separately. Keep full distributions, skipped evidence, settings snapshot and append-only history under native disclosures.
4. Simplify overview and form copy. Give demo users direct, real case creation for the three policy outcomes. Keep the normal three-step form.
5. Consolidate obsolete detail CSS, then browser-test desktop/mobile, evidence, review, errors, persistence and policy replay.

## Plan review (separate review pass)
- Do not turn the demo into diagnosis, simulated live inference, or a landing page.
- Do not hide critical warnings or the next action behind technical disclosures.
- Show the source per step: live Jev, fixture/local demo, safety bypass, or unknown legacy source. Do not present seeded latency as measured API performance.
- Preserve historical policy settings; show current settings only for a requested recompute.
- Existing `.gitignore` edit belongs to the user and stays outside commits.


## Live Jev extension — 2026-10-30 [FR-22]
Scope: stateless Worker, exported Python questions, localApi creation/evidence/recompute provenance, connection dialog, deployment config/docs and tests. No persistence migration or FastAPI behavior change. Lock security boundaries with Worker tests and failed-write/history tests before integration. Then review secrets, payload minimization, safety bypass, no fake fixture fallback, rate-limit caveat and deployed asset parity separately.


## Public sensor correction — 2026-10-30 [FR-22]
Remove the rejected access-code layer, not the secret boundary: callers, Worker routing/CORS, browser bootstrap/header/modal, tests, specs and operator docs. First change anonymous-request regressions, then delete the gate. Review anonymous live behavior, no Authorization/token in browser, existing failure/safety/history tests and production source parity. No new dependencies, storage or policy math.
