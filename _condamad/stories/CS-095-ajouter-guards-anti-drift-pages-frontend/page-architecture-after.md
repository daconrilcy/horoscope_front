<!-- Audit CS-095 des guards page-architecture. -->

# CS-095 After

Date: 2026-05-08

Guard executable:

- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/tests/page-architecture-allowlist.ts`

Exceptions avec owner:

| Surface | Owner | Sortie |
|---|---|---|
| Pages `@ts-nocheck` restantes | owners exacts par fichier | stories dediees de typage |
| Appels `apiFetch(` pages hors CS-091 | owners exacts par page | stories dediees de centralisation API |
| Pages volumineuses | owners exacts par page + seuil | stories dediees de decomposition |

Preuve: `npm run test -- page-architecture`: 1 file PASS, 8 tests PASS.
