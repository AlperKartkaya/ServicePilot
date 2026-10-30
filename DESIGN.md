# Design

## Source of truth
Active · 2026-10-30 · static application. Based on DESCRIPTION.md, specs/, existing UI and rendered desktop baseline.

## Brand
A calm technical decision desk. Keep the incumbent charcoal/mint identity. Earn trust through visible source, assumptions and human control, not AI claims.

## Product goals
Make the next useful evidence obvious. Show the division of work: Jev measures semantic probabilities; RAEP selects the operational action. Not diagnosis, not chat. Success: the case's next action is visible before optional detail on desktop and mobile.

## Personas and jobs
Technician: submit a case and the requested result. Expert: inspect risk and confirm or override assignment. Jury: inspect real policy calculations and replay without mistaking synthetic signals for live Jev.

## Information architecture
Overview: one product sentence, compact method strip, direct demo, work queue. Cases: searchable triage. New case: vehicle, complaint, evidence/review. Case: compact context, next action, visible Jev/RAEP reasoning, optional technical/history sections. Expert desk: review, teams, policy/replay. Preserve existing hash routes.

## Design principles
One primary operational action per case. Display context once. Short labels; disclose complete calculations on demand. Safety beats flow. Never imply sufficient evidence merely because the case stopped requesting it.

## Visual language
Existing tokens: ground #090D13, surface #0E141C, raised #141C26, ink #F4F7FA, mint #40D9C0. Amber/red are reserved for waiting/risk. Inter for product text, JetBrains Mono only for equations, IDs and measurements. 8px spacing rhythm; restrained 14px surfaces. No new imagery or ornamental motion.

```
Overview: [Product promise + try evidence loop] [Jev → RAEP → operational action]
          [compact counts] [work queue | recent activity]
Case:     [identity + complaint]
          [Jev signals / RAEP calculation | next action + result entry]
          [technical trace] [evidence and decision history] [vehicle / attachments]
Mobile:   [identity] [next action] [Jev / RAEP] [disclosures]
```

## Components
Reuse .btn, status badges, .bars, form fields, dialogs and tables. Use native details/summary for secondary information. The decision workbench owns a single action panel, not nested status cards. CSS tokens remain in static/style.css.

## Accessibility
Target WCAG 2.2 AA, not a certification. Semantic controls, skip link, visible focus, labels, announced errors. Native disclosures and dialog Escape. Focus errors, preserve entered evidence on request failure. Do not use color alone.

## Responsive behavior
Desktop workbench has reasoning and action columns. At 900px, action comes first. Three form steps stay on one row on phones. Optional case metadata never pushes the primary action below the long technical trace. Test 390px, 768px and 1440px.

## Interaction states
Real pending state during requests, no invented progress. Explicit API failure, no silent write fallback. Local demo badge states no live Jev call. Unknown case displays not found. Locked case exposes override but no invalid evidence entry. Destructive demo reset retains confirmation.

## Content voice
Turkish, sentence case. “Kanıt ekle”, “Yönlendirmeyi onayla”, “Uzman kararı ver”. Jev produces probabilities, not calibrated confidence/accuracy. RAEP calculates expected value using assumed evidence costs. ProEye is a handoff label, not a connected integration.

## Implementation constraints
Vanilla HTML/CSS/JS, FastAPI, SQLite. No frontend build or runtime dependency. Keep API actions and policy math. Screenshots and regression checks are required; live-provider success is a separate claim.

## Open questions
- [ ] Real-domain probability calibration and evidence costs: PoC owner; not MVP validation.
