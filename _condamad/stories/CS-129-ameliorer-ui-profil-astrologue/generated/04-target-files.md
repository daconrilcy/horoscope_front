# Target Files

## Must read

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-129-ameliorer-ui-profil-astrologue/00-story.md`
- `frontend/package.json`
- `frontend/src/pages/AstrologerProfilePage.tsx`
- `frontend/src/pages/AstrologerProfilePage.css`
- `frontend/src/features/astrologers/components/AstrologerProfileSections.tsx`
- `frontend/src/i18n/astrologers.ts`
- `frontend/src/tests/AstrologersPage.test.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`

## Must search

- `rg -n "AstrologerProfile|profile-|overflow-x|style=" frontend/src frontend/e2e`
- `rg -n "AstrologerProfile|profile-" frontend/src/App.css`
- `rg -n "style=" frontend/src/pages/AstrologerProfilePage.tsx frontend/src/features/astrologers/components/AstrologerProfileSections.tsx`
- `rg -n "overflow-x:\s*hidden" frontend/src/pages/AstrologerProfilePage.css`
- `rg -n "astrologer-card|astrologer-grid|compat|compatibility|legacy|alias|shim" frontend/src/pages/AstrologerProfilePage.css frontend/src/features/astrologers/components/AstrologerProfileSections.tsx frontend/src/pages/AstrologerProfilePage.tsx`

## Likely modified

- `frontend/src/pages/AstrologerProfilePage.tsx`
- `frontend/src/pages/AstrologerProfilePage.css`
- `frontend/src/features/astrologers/components/AstrologerProfileSections.tsx`
- `frontend/src/i18n/astrologers.ts`
- `frontend/src/tests/AstrologersPage.test.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/e2e/astrologer-profile-ui.spec.ts`
- Story evidence files under `_condamad/stories/CS-129-ameliorer-ui-profil-astrologue/`

## Forbidden unless justified

- `frontend/src/App.css`
- `frontend/src/app/routes.tsx`
- `frontend/src/api/astrologers.ts`
- `frontend/src/types/astrologer.ts`
- `frontend/src/pages/AstrologersPage.tsx`
- `frontend/src/features/astrologers/components/AstrologerCard.tsx`
- `backend/**`
