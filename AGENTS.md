# AGENTS.md

## Project: ServicePilot (what / why / how)

**What we build:** ServicePilot — an *Active Evidence Orchestration* layer for technical service (first target: Anadolu Isuzu after-sales). It is **not** an AI fault-diagnosis tool and **not** a chatbot. For each incomplete service case it decides one of three actions:
`ROUTE` (send to the right expert team, hierarchical fallback allowed), `REQUEST_EVIDENCE` (ask the technician for the next most valuable evidence), `ESCALATE` (send to a human expert / ProEye desk).

**Why:** Working MVP for the TÜBİTAK BİGGVADİ competition. The demo must show: Jev typed decisions → RAEP (Risk-Aware Evidence Policy) → operational action, controllable and explainable from the UI.

**How:**
- Jev (TypeSafe System One API) is a *semantic sensor*: it returns probabilities (`choice`, `noul`, `score`). It never makes the final decision.
- RAEP (our code, `app/raep.py`) turns those probabilities + evidence cost model + safety gate into the action. This is the R&D core; keep it pure and tested.
- Stack: Python 3.11+ / FastAPI / SQLite (stdlib) / static vanilla HTML+JS UI (no build step). Run with `uv run uvicorn app.main:app --reload`.
- Text/JSON first. Images and `Box` are out of MVP scope (TypeSafe marks them experimental).
- `TYPESAFE_API_KEY` lives in `.env`. Never commit it, never send it to the browser.

## Spec-Driven Development (mandatory workflow)

Specs live in `specs/` and are the source of truth. Code follows specs, not the other way around.

| File | Purpose |
|---|---|
| `specs/PRD.md` | Product goals, users, scope, non-goals, success metrics |
| `specs/REQUIREMENTS.md` | Numbered functional (FR-x) and non-functional (NFR-x) requirements with acceptance criteria |
| `specs/ARCHITECTURE.md` | Components, data flow, RAEP algorithm, Jev question design |
| `specs/API_SPEC.md` | HTTP endpoints, request/response shapes, data model |
| `specs/PLAN.md` | Milestones and task checklist with status |
| `specs/DECISIONS.md` | Architecture Decision Records (ADR-x): context, decision, consequence |

Rules:
1. Before a change: find the FR/NFR it serves. If none exists, add or update the spec first.
2. A change to endpoints updates `API_SPEC.md`; a change to policy math updates `ARCHITECTURE.md`; a non-obvious choice adds an ADR.
3. After a change: tick the task in `PLAN.md`. Reference requirement IDs in commit messages (e.g. `feat(raep): hierarchical fallback [FR-7]`).
4. Never put unverified numbers (Isuzu costs, accuracy claims) in specs or UI. Mark assumptions as assumptions.

---

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Do not spawn sub-agents

Spawning sub-agents is not allowed. You are the only agent. You do not need help.

## 6. Do not over-engineer

Do not over-engineer solutions. Do not add unnecessary abstractions. Do not add unnecessary features. Do not add unnecessary error handling. Do not add unnecessary logging. Do not add unnecessary test.

## 7. Follow the project description

Read the project description at DESCRIPTION.md and understand the project goals and architecture. Follow the project description when implementing changes.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.