# No Legacy / DRY Guardrails - CS-117

## Interdits

- `frontend/src/components/SignInForm.tsx`
- `frontend/src/components/SignUpForm.tsx`
- `frontend/src/components/SignUpForm.css`
- Exceptions `components/SignInForm.tsx` ou `components/SignUpForm.tsx`
- Imports `../components/SignInForm` ou `../components/SignUpForm`
- Wrapper, alias, fallback, re-export ou compatibilite de chemin.

## Guards applicables

- `RG-064` - page architecture auth.
- `RG-068` - hierarchie layout login/register.
- `RG-069` - imports API/feature dans `components`.
- `RG-070` - pas de suppression TypeScript sous `components`.

## Evidence requise

Tests `component-architecture`, `page-architecture`, tests auth/routes, lint, et
scans zero-hit des anciens chemins.
