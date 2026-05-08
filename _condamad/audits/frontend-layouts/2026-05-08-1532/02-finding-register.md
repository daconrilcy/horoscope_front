<!-- Registre des constats de l'audit CONDAMAD de suivi frontend-layouts. -->

# Finding Register - frontend-layouts follow-up

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-101 | Medium | High | needs-user-decision | frontend-layouts | E-005, E-008, E-009 | The layout implementation is guarded, but CS-107 intentionally leaves privacy, billing callback, and dead/unmounted page candidates blocked by product/removal decisions. | Decide route ownership or removal for the exact residual files; do not route or delete them silently. | yes |

## Finding Details

### F-101 - Residual page candidates require explicit decisions

- Severity: Medium
- Confidence: High
- Category: needs-user-decision
- Domain: frontend-layouts
- Evidence: E-005, E-008, E-009.
- Expected rule: every page file is either fully routed/owned, classified as page-adjacent with owner, removed by explicit story, or blocked by a named decision.
- Actual state: `PAGE_LAYOUT_OWNER_CLASSIFICATIONS` correctly classifies all files, but keeps `PrivacyPolicyPage`, `BillingSuccessPage`, and `BillingCancelPage` as `needs-user-decision`; `HomePage` and `TestimonialsSection` are `dead/unmounted-page-candidate`.
- Impact: The layout implementation is guarded, but CS-107 intentionally leaves privacy, billing callback, and dead/unmounted page candidates blocked by product/removal decisions.
- Recommended action: Decide route ownership or removal for the exact residual files; do not route or delete them silently.
- Story candidate: yes
- Suggested archetype: ownership-routing-refactor
- Closure classification: blocked.

## Closed Prior Findings

| Prior finding | Closure evidence | Guardrail |
|---|---|---|
| 2026-05-08-1405 F-001 | E-001, E-002, E-006, E-010 | RG-068 |
| 2026-05-08-1405 F-002 | E-001, E-003, E-006, E-011 | RG-068 |
| 2026-05-08-1405 F-003 | E-001, E-004, E-006, E-007 | RG-068 |
| 2026-05-08-1405 F-004 | E-005, E-006, E-007 | RG-068 |
| 2026-05-08-1405 F-005 | E-005, E-008, E-009 | RG-068 |
| 2026-05-08-1532 F-102 | E-013, E-014 | RG-068 |

## Exhaustive Active Surface

Application files with pending decision only:

- `frontend/src/pages/PrivacyPolicyPage.tsx`
- `frontend/src/pages/billing/BillingSuccessPage.tsx`
- `frontend/src/pages/billing/BillingCancelPage.tsx`
- `frontend/src/pages/HomePage.tsx`
- `frontend/src/pages/landing/sections/TestimonialsSection.tsx`

Governance files with pending work: none.

Deferred non-domain context:

- Legal policy content and billing callback contract ownership.
- CSS design-system cleanup outside layout hierarchy.
