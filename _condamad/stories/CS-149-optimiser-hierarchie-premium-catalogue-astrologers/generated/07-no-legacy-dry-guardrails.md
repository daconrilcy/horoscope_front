# No Legacy / DRY Guardrails

## Canonical owners

- Route/header/loading/error: `frontend/src/pages/AstrologersPage.tsx`
- Grid/empty state: `frontend/src/features/astrologers/components/AstrologerGrid.tsx`
- Card hierarchy/CTA/badges: `frontend/src/features/astrologers/components/AstrologerCard.tsx`
- Localized visible copy: `frontend/src/i18n/astrologers.ts`
- Catalogue grid/cards/CTA CSS: `frontend/src/styles/app/cards.css`
- Media/reduced motion: `frontend/src/styles/app/media.css`

## Forbidden

- `frontend/src/App.css` active catalogue styles.
- `.astrologer-*` selectors.
- `style=` in route/card/grid feature files.
- `featured={index === 0}`.
- `.person-card--featured`.
- Nested `button`, `a`, or role button inside `.person-card`.
- `height: 244px` or `height: 256px` for catalogue cards.
- Duplicate card/grid component.
- New dependency.

## Required evidence

- Targeted tests.
- Zero-hit scans from `06-validation-plan.md`.
- Diff review confirming no unrelated files changed.
