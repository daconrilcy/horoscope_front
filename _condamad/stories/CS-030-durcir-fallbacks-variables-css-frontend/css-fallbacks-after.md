<!-- Inventaire final des fallbacks CSS apres durcissement CS-030. -->

# CSS Fallbacks After

Ajouts:

- Registre `frontend/src/styles/css-fallback-allowlist.md`.
- Test `frontend/src/tests/css-fallback-policy.test.ts`.

Guard: `npm run test -- css-fallback`.

Resultat: les fallbacks conserves sont classes, et le lot CS-027 ne conserve
pas les literals `999px`, `8px` ou `12px` comme fallbacks des tokens migres.
