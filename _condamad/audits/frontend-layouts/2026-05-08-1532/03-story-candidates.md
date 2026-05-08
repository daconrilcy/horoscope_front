<!-- Candidats de stories issus de l'audit CONDAMAD de suivi frontend-layouts. -->

# Story Candidates - frontend-layouts follow-up

## Candidate Summary

| Candidate ID | Source finding ID | Suggested story title | Suggested archetype | Primary domain | Blockers / user decision |
|---|---|---|---|---|---|
| SC-101 | F-101 | Decider les pages publiques et candidates mortes restantes | ownership-routing-refactor | frontend-layouts | Product decision required for privacy and billing callback public exposure; removal decision required for dead candidates. |

## SC-101 - Decider les pages publiques et candidates mortes restantes

- Candidate ID: SC-101
- Source finding: F-101
- Suggested story title: Decider les pages publiques et candidates mortes restantes
- Suggested archetype: ownership-routing-refactor
- Primary domain: frontend-layouts
- Required contracts: `no-legacy-dry-audit-contract`, `report-output-contract`, existing guardrail `RG-068`.
- Draft objective: resolve the exact `needs-user-decision` and `dead/unmounted-page-candidate` entries left by CS-107 without weakening the page ownership guard.
- Closure intent: `blocked`
- Must include:
  - Product decision for `PrivacyPolicyPage`: route under `LandingLayout`, route under another explicit public owner, keep blocked, or remove through a dedicated removal story.
  - Product/Stripe callback decision for `BillingSuccessPage` and `BillingCancelPage`: route under an explicit layout, keep blocked, or remove through a dedicated removal story.
  - Removal decision for `HomePage` and `TestimonialsSection`, or keep them classified with explicit owner/expiry.
  - No compatibility route, redirect, alias, broad exception, or wildcard page allowlist.
  - Update `PAGE_LAYOUT_OWNER_CLASSIFICATIONS` and `page-layout-owner-after.md` to reflect the chosen decisions.
- Validation hints:
  - `npm run lint`
  - `npm run test -- page-architecture layout`
  - `npm run test -- App router BillingSuccessPage`
  - Targeted scan proving no `needs-user-decision` file was routed without decision evidence.
- Blockers:
  - Required before implementation for privacy/billing public exposure.
  - Required before deletion of dead/unmounted candidates.

### Exhaustive Files To Modify - SC-101

Application files:

- `frontend/src/app/routes.tsx` only if routing decisions are approved.
- `frontend/src/pages/PrivacyPolicyPage.tsx` only if routed or removed by explicit decision.
- `frontend/src/pages/billing/BillingSuccessPage.tsx` only if routed or removed by explicit decision.
- `frontend/src/pages/billing/BillingCancelPage.tsx` only if routed or removed by explicit decision.
- `frontend/src/pages/HomePage.tsx` only if removed by explicit decision.
- `frontend/src/pages/landing/sections/TestimonialsSection.tsx` only if removed or reattached by explicit decision.

Governance/test files:

- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts` only if guard logic must change.
- `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md`
- Optional dedicated removal story artifacts.

Before/after evidence required:

- Before: current `PAGE_LAYOUT_OWNER_CLASSIFICATIONS` rows for the five residual files.
- After: updated classification or route evidence for each residual file.
- Guard: `npm run test -- page-architecture layout` remains green and fails on unclassified additions.

Stop condition:

- No residual file remains `needs-user-decision` unless the explicit user/product decision is to keep it blocked with owner and expiry.
- No `dead/unmounted-page-candidate` remains without a removal/retention decision.

## Closed Candidate

SC-102 was implemented in-place during this audit update: CS-103 through CS-107 now use `Status: done`, so no active story candidate remains for F-102.

## Deferred Non-Domain Context

- Legal policy content and billing provider callback behavior must be decided by product/legal/billing ownership before routing.
- Design-system and CSS token debt remain outside this audit.
