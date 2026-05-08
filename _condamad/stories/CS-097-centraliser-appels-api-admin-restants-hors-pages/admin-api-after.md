# CS-097 after inventory

- canonical-owner: `frontend/src/api/adminOperations.ts`.
- Migrated endpoint families:
  - admin AI metrics and detail: `useAdminAiMetrics`, `useAdminAiUseCaseDetail`.
  - admin entitlements matrix/update: `useAdminEntitlementsMatrix`, `updateAdminEntitlement`.
  - admin exports: `exportAdminData`.
  - admin support tickets/content: `useAdminSupportTickets`, `useAdminFlaggedContent`, `useReviewFlaggedContent`.
- Direct API scan after:
  - `rg -n "apiFetch\\(" src/pages -g "*.tsx"` retourne zero hit.
- DIRECT_API_PAGE_EXCEPTIONS after:
  - `TS_NOCHECK_PAGE_EXCEPTIONS: []`
  - `DIRECT_API_PAGE_EXCEPTIONS: []`

