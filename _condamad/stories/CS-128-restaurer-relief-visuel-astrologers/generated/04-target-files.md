# Target Files

<!-- Carte des fichiers a lire, modifier et proteger pour CS-128. -->

## Must Read

- `frontend/src/pages/AstrologersPage.tsx`
- `frontend/src/features/astrologers/components/AstrologerCard.tsx`
- `frontend/src/features/astrologers/components/AstrologerGrid.tsx`
- `frontend/src/styles/app/tokens.css`
- `frontend/src/styles/app/cards.css`
- `frontend/src/styles/app/media.css`
- `frontend/src/tests/AstrologersPage.test.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`
- `_condamad/stories/regression-guardrails.md`

## Must Search

- `rg -n "people-page|person-card|astrologer-" frontend/src/App.css frontend/src/styles/app frontend/src/features/astrologers`
- `rg -n "style=" frontend/src/pages/AstrologersPage.tsx frontend/src/features/astrologers/components`
- `rg --files frontend/src/styles/app`

## Likely Modified

- `frontend/src/styles/app/cards.css`
- `frontend/src/styles/app/media.css`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`
- `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/astrologers-visual-before.md`
- `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/astrologers-visual-after.md`
- `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/validation-evidence.md`

## Forbidden Unless Explicitly Justified

- `frontend/src/App.css`
- `frontend/package.json`
- `backend/**`
- new files under `frontend/src/styles/app/`
- API, route or profile page files.
