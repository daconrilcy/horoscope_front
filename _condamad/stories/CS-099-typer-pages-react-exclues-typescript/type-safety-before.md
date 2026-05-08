# CS-099 before inventory

- `@ts-nocheck` before:
  - `frontend/src/pages/AstrologerProfilePage.tsx`
  - `frontend/src/pages/ConsultationResultPage.tsx`
  - `frontend/src/pages/NotFoundPage.tsx`
- TS_NOCHECK_PAGE_EXCEPTIONS before:
  - `pages/AstrologerProfilePage.tsx`
  - `pages/ConsultationResultPage.tsx`
  - `pages/NotFoundPage.tsx`
- Typing assumptions:
  - `AstrologerProfilePage`: icon types and button variants must match UI component contracts.
  - `ConsultationResultPage`: consultation result, sections, precision and fallback types must be explicit.
  - `NotFoundPage`: `AuthLayout` must accept route-support children without bypass.

