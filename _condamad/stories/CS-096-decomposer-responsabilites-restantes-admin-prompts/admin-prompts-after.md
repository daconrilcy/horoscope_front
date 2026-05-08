# CS-096 after inventory

- line-count: `frontend/src/pages/admin/AdminPromptsPage.tsx` = 2668 lignes apres extraction.
- extracted-owner-path: `frontend/src/features/admin-prompts/adminPromptsPageParts.tsx`.
- PAGE_SIZE_EXCEPTIONS: `pages/admin/AdminPromptsPage.tsx`, `maxLines: 2700`, rationale resserree au conteneur route catalogue/archive.
- page-absence-proof:
  - `AdminPromptsPage.tsx` importe les fragments depuis `features/admin-prompts/adminPromptsPageParts.tsx`.
  - Les definitions locales extraites ne sont plus definies dans la page route.
  - `rg -n "@ts-nocheck|@ts-ignore|apiFetch\\(" src/pages src/features/admin-prompts -g "*.tsx"` retourne zero hit.
- Remaining closure map:
  - extracted: helpers, modales rollback/manual execution, disclosure, presentation erreurs et rows diff.
  - route-only: selection active d'onglet, state route, orchestration queries et navigation route.
  - remaining-next-slice: sections JSX catalogue, consommation et release encore volumineuses mais gardees par `PAGE_SIZE_EXCEPTIONS`.

