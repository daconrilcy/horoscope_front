# Auth API Containers After - CS-117

## Commandes executees

- `npm run test -- SignInForm SignUpForm App router` depuis `frontend/` - PASS, 7 fichiers, 99 tests.
- `npm run test -- component-architecture page-architecture` depuis `frontend/` - PASS, 2 fichiers, 25 tests apres ajout du guard anti-retour auth.
- `npm run lint` depuis `frontend/` - PASS.
- `rg -n "components/SignInForm.tsx" frontend/src/tests/component-architecture-allowlist.ts` - PASS zero hit, code retour `1`.
- `rg -n "components/SignUpForm.tsx" frontend/src/tests/component-architecture-allowlist.ts` - PASS zero hit, code retour `1`.
- `rg -n "components/SignInForm|components/SignUpForm|\.\./components/SignInForm|\.\./components/SignUpForm" frontend/src -g "*.ts" -g "*.tsx"` - PASS zero hit, code retour `1`.
- `rg -n "export .*SignInForm|export .*SignUpForm" frontend/src/components -g "*.ts" -g "*.tsx"` - PASS zero hit, code retour `1`.
- `rg -n "Sign(In|Up)Form" frontend/src/components` - PASS zero hit, code retour `1`.
- `rg -n "@ts-nocheck" frontend/src/components -g "*.ts" -g "*.tsx"` - PASS zero hit, code retour `1`.
- `rg -n "style=" frontend/src/features/auth -g "*.tsx"` - PASS zero hit, code retour `1`.
- `rg -n "\bany\b" frontend/src/features/auth -g "*.ts" -g "*.tsx"` - PASS zero hit, code retour `1`.
- `rg -n "components/SignInForm\.tsx|components/SignUpForm\.tsx" frontend/src/tests/component-architecture-allowlist.ts frontend/src/tests/component-architecture-guards.test.ts` - PASS zero hit, code retour `1`.
- `rg -n "from [\"']\.\./components/SignInForm[\"']|from [\"']\.\./components/SignUpForm[\"']" frontend/src -g "*.ts" -g "*.tsx"` - PASS zero hit, code retour `1`.

## Constats apres migration

| Surface | Etat apres |
|---|---|
| `frontend/src/features/auth/SignInForm.tsx` | owner canonique du container de connexion. |
| `frontend/src/features/auth/SignUpForm.tsx` | owner canonique du container d'inscription. |
| `frontend/src/features/auth/SignUpForm.css` | CSS auth colocated avec le container feature. |
| `frontend/src/pages/LoginPage.tsx` | importe `SignInForm` depuis `../features/auth/SignInForm`. |
| `frontend/src/pages/RegisterPage.tsx` | importe `SignUpForm` depuis `../features/auth/SignUpForm`. |
| `frontend/src/tests/SignInForm.test.tsx` | importe le nouvel owner auth. |
| `frontend/src/tests/SignUpForm.test.tsx` | importe le nouvel owner auth. |
| `frontend/src/tests/component-architecture-allowlist.ts` | les deux exceptions auth ont ete supprimees; les autres lignes restent. |
| `frontend/src/tests/component-architecture-guards.test.ts` | guard persistant anti-retour pour les anciennes exceptions et imports auth. |
| `frontend/src/tests/design-system-guards.test.ts` | l'exception CSS existante pointe vers le chemin auth canonique. |

## Classification apres migration

| Item | Classification | Consumers | Decision | Proof | Risk |
|---|---|---|---|---|---|
| `frontend/src/components/SignInForm.tsx` | `historical-facade` apres repointage | aucun | `delete` | scans zero-hit + tests auth | faible |
| `frontend/src/components/SignUpForm.tsx` | `historical-facade` apres repointage | aucun | `delete` | scans zero-hit + tests auth | faible |
| `frontend/src/components/SignUpForm.css` | `historical-facade` apres repointage | aucun | `delete` | scan components + lint | faible |

## Source finding

La tranche auth de `F-001` est fermee: les containers auth ne sont plus sous
`frontend/src/components/**`, les exceptions auth sont retirees et aucun ancien
chemin auth n'est preserve. Les domaines enterprise/B2B, ops/support,
settings/privacy, layouts, dashboard et natal restent hors scope de CS-117.
