<!-- Candidats de stories issus de l'audit CONDAMAD de continuite frontend-layouts. -->

# Story Candidates - frontend-layouts continuity

## Candidate Summary

| Candidate ID | Source finding ID | Suggested story title | Suggested archetype | Primary domain | Blockers / user decision |
|---|---|---|---|---|---|
| SC-201 | F-201 | Fermer les decisions residuelles de pages layout | ownership-routing-refactor | frontend-layouts | Closed by CS-109 after named user decisions on 2026-05-08. |

## SC-201 - Fermer les decisions residuelles de pages layout

- Candidate ID: SC-201
- Source finding: F-201
- Suggested story title: Fermer les decisions residuelles de pages layout
- Suggested archetype: ownership-routing-refactor
- Primary domain: frontend-layouts
- Required contracts: `no-legacy-dry-audit-contract`, `report-output-contract`, existing guardrail `RG-068`.
- Draft objective: close the exact CS-108 residual decisions by applying named user/product/legal/billing decisions to the five retained page surfaces.
- Closure intent: `closed-by-CS-109`
- Must include:
  - For `PrivacyPolicyPage`: record a named legal/product decision to route under `LandingLayout` or another explicit public owner, keep blocked with renewed expiry, or open a dedicated removal story.
  - For `BillingSuccessPage` and `BillingCancelPage`: record a named billing/Stripe decision to route callback pages under an explicit owner, keep blocked with renewed expiry, or open a dedicated removal story.
  - For `HomePage` and `TestimonialsSection`: record a named product/removal decision to delete through a dedicated story, retain with explicit owner/expiry, or reattach `TestimonialsSection` to `LandingPage` with product evidence.
  - Preserve `RootLayout` and the existing route-family owners.
  - Preserve `PAGE_LAYOUT_OWNER_CLASSIFICATIONS` as the executable registry; do not create a second registry.
  - No route, redirect, alias, shim, fallback, re-export, or wildcard exception may be introduced.
- Validation hints:
  - `npm run lint`
  - `npm run test -- page-architecture layout`
  - `npm run test -- App router BillingSuccessPage`
  - Targeted scan: `rg -n "PrivacyPolicyPage|BillingSuccessPage|BillingCancelPage|HomePage|TestimonialsSection" frontend/src/app/routes.tsx frontend/src/pages/index.ts frontend/src/tests/page-architecture-allowlist.ts`
- Blockers:
  - None active after CS-109. The user supplied named decisions for privacy, billing callbacks, `HomePage`, and `TestimonialsSection` on 2026-05-08.

## Exhaustive Files To Modify - SC-201

Application files:

- `frontend/src/app/routes.tsx` only if routing is explicitly approved.
- `frontend/src/pages/PrivacyPolicyPage.tsx` only if routed, retained with content/owner change, or removed by dedicated story.
- `frontend/src/pages/billing/BillingSuccessPage.tsx` only if routed, retained with owner change, or removed by dedicated story.
- `frontend/src/pages/billing/BillingCancelPage.tsx` only if routed, retained with owner change, or removed by dedicated story.
- `frontend/src/pages/HomePage.tsx` only if a dedicated removal story approves deletion or retention changes.
- `frontend/src/pages/landing/sections/TestimonialsSection.tsx` only if a dedicated removal story approves deletion or a product decision approves reattachment.

Governance/test files:

- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts` only if a new decision state needs guard support.
- `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/page-decisions-after.md` or a successor decision artifact.
- `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md` if the historical inventory must be synced.

## Before / After Evidence Required

- Before: current CS-108 decision rows for the five residual files.
- Before: route scan proving the three blocked public pages are not routed.
- Before: runtime import scan proving dead candidates are not reattached.
- After: updated executable allowlist row for every changed decision.
- After: route tree evidence for every routed page.
- After: removal evidence for every deleted surface, with no compatibility wrapper or re-export.
- Guard: `npm run test -- page-architecture layout` remains green and fails if a blocked file is routed without decision metadata.

## Stop Condition

The finding is fully closed because one of these states is true for each of the five files:

- route exists under an explicit layout owner and the executable guard proves it;
- file is removed by a dedicated removal story with no wrapper, route, alias, fallback, or re-export;
- no file remains blocked inside the repository domain after CS-109.

## Deferred Non-Domain Context

- Legal policy content.
- Stripe/billing provider callback contract and external dashboard configuration.
- Product decision on whether the old home page or testimonials section should exist.
- Design-system and CSS token cleanup.
