<!-- Inventaire initial CS-101 des exceptions de taille de pages frontend. -->

# CS-101 Page Size Before

Capture: 2026-05-08.

## Baseline line-counts

| Page | Lines before | Allowlist before | Classification | Target owner | Decision |
|---|---:|---|---|---|---|
| `frontend/src/pages/AstrologerProfilePage.tsx` | 813 | `maxLines: 900` | `extractable` | `frontend/src/features/astrologers/components/AstrologerProfileSections.tsx` | decompose reviews and final CTA, then remove allowlist entry |
| `frontend/src/pages/BirthProfilePage.tsx` | 714 | `maxLines: 800` | `extractable` | `frontend/src/features/birth-profile/components/BirthProfileNatalGenerationSection.tsx` | decompose status/generation rendering, then remove allowlist entry |
| `frontend/src/pages/settings/SubscriptionSettings.tsx` | 751 | `maxLines: 850` | `extractable` | `frontend/src/components/settings/SubscriptionPlanGrid.tsx` | decompose plan grid, then remove allowlist entry |
| `frontend/src/pages/admin/AdminSamplePayloadsAdmin.tsx` | 683 | `maxLines: 780` | `dead` / stale allowlist entry | existing page remains active | remove stale allowlist entry only |

## Allowlist before

`PAGE_SIZE_EXCEPTIONS` contained exact entries for:

- `pages/admin/AdminPromptsPage.tsx` - out of scope, retained for CS-100.
- `pages/AstrologerProfilePage.tsx` - temporary decomposition debt.
- `pages/BirthProfilePage.tsx` - temporary decomposition debt.
- `pages/admin/AdminSamplePayloadsAdmin.tsx` - stale, below threshold.
- `pages/settings/SubscriptionSettings.tsx` - temporary decomposition debt.

## Guardrails

- `RG-064`: page architecture exceptions must remain exact.
- `RG-066`: page-size exceptions outside AdminPrompts must be closed, exact, or permanent route-only.
- `RG-047`: extracted TSX must not introduce inline static styles.
- `RG-049`: no CSS ownership movement in this story; non-applicable after inspection.
