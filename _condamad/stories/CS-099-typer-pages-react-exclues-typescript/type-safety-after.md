# CS-099 after inventory

- `@ts-nocheck` after:
  - `rg -n "@ts-nocheck|@ts-ignore" src/pages -g "*.tsx"` retourne zero hit.
- TS_NOCHECK_PAGE_EXCEPTIONS after:
  - `TS_NOCHECK_PAGE_EXCEPTIONS: []`
- Typed pages:
  - `AstrologerProfilePage.tsx`: compile sans bypass; variant de bouton aligne sur `ButtonProps`.
  - `ConsultationResultPage.tsx`: compile sans bypass; types consultation ajoutes a `frontend/src/types/consultation.ts`; guards locaux pour precision/fallback.
  - `NotFoundPage.tsx`: compile sans bypass; `AuthLayout` accepte `children` ou `Outlet`.

