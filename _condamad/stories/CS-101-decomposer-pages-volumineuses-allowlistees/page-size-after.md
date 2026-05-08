<!-- Inventaire final CS-101 des exceptions de taille de pages frontend. -->

# CS-101 Page Size After

Capture: 2026-05-08.

## Final line-counts

| Page | Lines after | Allowlist after | Classification | Canonical owner / no-shim-proof | Decision |
|---|---:|---|---|---|---|
| `frontend/src/pages/AstrologerProfilePage.tsx` | 698 | none | `canonical-active` route shell | metrics, method, reviews and final CTA rendered by `frontend/src/features/astrologers/components/AstrologerProfileSections.tsx`; no compatibility wrapper | remove allowlist entry |
| `frontend/src/pages/BirthProfilePage.tsx` | 689 | none | `canonical-active` route shell | load/geocoding/current-location/generation sections rendered by `frontend/src/features/birth-profile/components/BirthProfileNatalGenerationSection.tsx`; no compatibility wrapper | remove allowlist entry |
| `frontend/src/pages/settings/SubscriptionSettings.tsx` | 700 | none | `canonical-active` route shell | overview and plan cards rendered by `frontend/src/components/settings/SubscriptionPlanGrid.tsx`; no compatibility wrapper | remove allowlist entry |
| `frontend/src/features/admin-prompts/AdminSamplePayloadsAdmin.tsx` | 683 | none | `canonical-active` feature owner after CS-100 prerequisite | former `frontend/src/pages/admin/AdminSamplePayloadsAdmin.tsx` path removed by CS-100; stale governance entry removed only | remove stale allowlist entry |
| `frontend/src/pages/admin/AdminPromptsPage.tsx` | 81 | none | out of scope / already below threshold after CS-100 prerequisite | CS-101 depends on completed CS-100 for this stale exception; no hidden threshold remains | remove stale allowlist entry |

## Allowlist after

`PAGE_SIZE_EXCEPTIONS` is empty. No exception remains for page-size debt outside AdminPrompts, and the completed CS-100 prerequisite leaves `AdminPromptsPage.tsx` below the threshold.

## Known residual in-domain work

None for CS-101. All target pages are at or below the 700-line guard threshold.

## Guard evidence expected

- `npm run test -- page-architecture`
- `npm run test -- AstrologerProfile BirthProfile SubscriptionSettings AdminSamplePayloads`
- `npm run lint`
