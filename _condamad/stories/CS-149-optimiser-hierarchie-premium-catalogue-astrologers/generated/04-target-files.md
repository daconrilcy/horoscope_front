# Target Files

## Must inspect

- `frontend/src/pages/AstrologersPage.tsx`
- `frontend/src/features/astrologers/components/AstrologerGrid.tsx`
- `frontend/src/features/astrologers/components/AstrologerCard.tsx`
- `frontend/src/i18n/astrologers.ts`
- `frontend/src/styles/app/cards.css`
- `frontend/src/styles/app/media.css`
- `frontend/src/styles/app/tokens.css`
- `frontend/src/tests/AstrologersPage.test.tsx`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- `_condamad/stories/regression-guardrails.md`

## Must search

- `rg -n "person-card|person-grid|people-page" frontend/src`
- `rg -n "featured=\{index === 0\}|person-card--featured|style=|astrologer-" frontend/src`
- `rg -n "prefers-reduced-motion|person-orbit-drift|animation:" frontend/src/styles/app`

## Likely modified

- `frontend/src/features/astrologers/components/AstrologerCard.tsx`
- `frontend/src/features/astrologers/components/AstrologerGrid.tsx`
- `frontend/src/pages/AstrologersPage.tsx`
- `frontend/src/i18n/astrologers.ts`
- `frontend/src/styles/app/cards.css`
- `frontend/src/styles/app/media.css`
- `frontend/src/tests/AstrologersPage.test.tsx`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- story evidence files

## Forbidden unless explicitly justified

- `frontend/src/App.css`
- `frontend/src/pages/AstrologerProfilePage.tsx`
- `frontend/src/pages/AstrologerProfilePage.css`
- `frontend/src/layouts/RootLayout.tsx`
- `frontend/src/layouts/PageLayout.css`
- `backend/**`
