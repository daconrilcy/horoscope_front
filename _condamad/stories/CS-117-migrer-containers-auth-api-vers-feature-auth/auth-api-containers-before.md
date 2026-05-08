# Auth API Containers Before - CS-117

## Commandes executees

- `rg -n "components/SignInForm|components/SignUpForm|\.\./components/SignInForm|\.\./components/SignUpForm" frontend/src -g "*.ts" -g "*.tsx"`
- `rg -n "Sign(In|Up)Form" frontend/src/components frontend/src/pages frontend/src/tests -g "*.ts" -g "*.tsx" -g "*.css"`
- `rg -n "components/SignInForm.tsx|components/SignUpForm.tsx" frontend/src/tests/component-architecture-allowlist.ts`

## Constats

| Surface | Etat avant |
|---|---|
| `frontend/src/pages/LoginPage.tsx` | importe `SignInForm` depuis `../components/SignInForm`. |
| `frontend/src/pages/RegisterPage.tsx` | importe `SignUpForm` depuis `../components/SignUpForm`. |
| `frontend/src/tests/SignInForm.test.tsx` | importe `SignInForm` depuis `../components/SignInForm`. |
| `frontend/src/tests/SignUpForm.test.tsx` | importe `SignUpForm` depuis `../components/SignUpForm`. |
| `frontend/src/tests/component-architecture-allowlist.ts` | contient les exceptions exactes `components/SignInForm.tsx` et `components/SignUpForm.tsx`. |
| `frontend/src/components/SignInForm.tsx` | owner actif avant migration. |
| `frontend/src/components/SignUpForm.tsx` | owner actif avant migration. |
| `frontend/src/components/SignUpForm.css` | CSS actif importe par `SignUpForm.tsx`. |

## Classification avant migration

| Item | Classification | Consumers | Decision |
|---|---|---|---|
| `frontend/src/components/SignInForm.tsx` | `canonical-active` avant repointage | page login, test SignInForm | `replace-consumer` puis `delete` |
| `frontend/src/components/SignUpForm.tsx` | `canonical-active` avant repointage | page register, test SignUpForm | `replace-consumer` puis `delete` |
| `frontend/src/components/SignUpForm.css` | `canonical-active` avant repointage | `SignUpForm.tsx` | `replace-consumer` puis `delete` |

## Residuel hors scope

Le hit `frontend/src/tests/design-system-guards.test.ts` mentionne
`components/SignUpForm.css` comme exception de garde design-system preexistante;
il devra etre retire ou ajuste par la migration auth si stale.
