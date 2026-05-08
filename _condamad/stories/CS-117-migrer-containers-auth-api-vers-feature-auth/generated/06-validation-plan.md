# Validation Plan - CS-117

## Frontend

Depuis `frontend/`:

- `npm run test -- SignInForm SignUpForm App router`
- `npm run test -- component-architecture page-architecture`
- `npm run lint`

## Scans requis

Depuis la racine:

- `rg -n "components/SignInForm.tsx" frontend/src/tests/component-architecture-allowlist.ts`
- `rg -n "components/SignUpForm.tsx" frontend/src/tests/component-architecture-allowlist.ts`
- `rg -n "components/SignInForm|components/SignUpForm|\.\./components/SignInForm|\.\./components/SignUpForm" frontend/src -g "*.ts" -g "*.tsx"`
- `rg -n "export .*SignInForm|export .*SignUpForm" frontend/src/components -g "*.ts" -g "*.tsx"`
- `rg -n "Sign(In\|Up)Form" frontend/src/components`

Un code retour `1` de `rg` est attendu et classe PASS quand il signifie zero hit.

## Persistance

Depuis la racine avec le venv active:

- `python -c "from pathlib import Path; b=Path('_condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth'); assert (b/'auth-api-containers-before.md').exists()"`
- `python -c "from pathlib import Path; b=Path('_condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth'); assert (b/'auth-api-containers-after.md').exists()"`
- `python -c "from pathlib import Path; b=Path('_condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth'); assert (b/'generated/10-final-evidence.md').exists()"`
