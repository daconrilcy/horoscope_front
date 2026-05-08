# Final Evidence - CS-117

## Statut

Done; revue CONDAMAD finale `CLEAN`.

## AC par AC

| AC | Statut | Evidence |
|---|---|---|
| AC1 | PASS | `SignInForm` et `SignUpForm` sont sous `frontend/src/features/auth/`; scans zero-hit des anciens imports `components/Sign(In|Up)Form`. |
| AC2 | PASS | `npm run test -- SignInForm SignUpForm App router` PASS, 99 tests; `npm run lint` PASS. |
| AC3 | PASS | Les deux lignes auth sont retirees de `COMPONENT_API_IMPORT_EXCEPTIONS`; `npm run test -- component-architecture page-architecture` PASS; scans allowlist zero-hit. |
| AC4 | PASS | Les anciens fichiers sous `frontend/src/components` sont supprimes; `rg -n "Sign(In\|Up)Form" frontend/src/components` zero hit. |
| AC5 | PASS | `auth-api-containers-before.md`, `auth-api-containers-after.md` et cette evidence existent. |

## Fichiers modifies

- `frontend/src/features/auth/SignInForm.tsx`
- `frontend/src/features/auth/SignUpForm.tsx`
- `frontend/src/features/auth/SignUpForm.css`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/pages/RegisterPage.tsx`
- `frontend/src/tests/SignInForm.test.tsx`
- `frontend/src/tests/SignUpForm.test.tsx`
- `frontend/src/tests/component-architecture-allowlist.ts`
- `frontend/src/tests/component-architecture-guards.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `_condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth/auth-api-containers-before.md`
- `_condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth/auth-api-containers-after.md`
- `_condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth/generated/*.md`
- `_condamad/stories/story-status.md`

## Fichiers supprimes

- `frontend/src/components/SignInForm.tsx`
- `frontend/src/components/SignUpForm.tsx`
- `frontend/src/components/SignUpForm.css`

## Validations executees

- `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth/00-story.md` - PASS, venv active.
- `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth/00-story.md` - PASS, venv active.
- `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth/00-story.md` - PASS, venv active.
- `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth/00-story.md` - PASS, venv active.
- `npm run test -- SignInForm SignUpForm App router` - PASS, 7 fichiers, 99 tests.
- `npm run test -- component-architecture page-architecture` - PASS, 2 fichiers, 25 tests apres ajout du guard anti-retour.
- `npm run lint` - PASS.
- Scans A3/no-legacy listes dans `auth-api-containers-after.md` - PASS zero hit.
- `git diff --check` - PASS, warnings CRLF uniquement.

## Validations non executees

- Suite complete `npm run test` - non executee; la story impose les suites ciblees auth/routes/architecture et lint, toutes passees.
- E2E Playwright - non execute; aucun changement de contrat route/browser au-dela du deplacement d'imports, couvert par tests route/app.
- Backend pytest/ruff - non execute; aucun fichier `backend/**` touche.

## Frontend subagent

Le sous-agent `condamad-frontend-dev` a ete utilise pour la tranche frontend et
pour un correctif de revue accepte sur le chemin canonique. Evidence rapportee:
tests auth/routes, architecture/page, layout cible et lint PASS; scans legacy
zero-hit. Il a aussi ete reutilise pour ajouter le guard anti-retour persistant;
`component-architecture page-architecture` et lint repassent. Aucune mise a jour
du registre requise.

## Legacy / DRY

- Aucun wrapper, alias, fallback, re-export ou chemin legacy auth n'a ete cree.
- Les API auth restent consommees via `@api`.
- Le token reste persiste via `frontend/src/utils/authToken.ts`.
- Les autres exceptions composants restent hors scope et non modifiees.
- Le retour des anciennes exceptions auth ou imports `../components/Sign(In|Up)Form`
  est bloque par `component-architecture-guards.test.ts`.

## Source finding closure

`F-001` est `phased-with-map`: la tranche auth est fermee sans residuel
in-domain connu pour `frontend/src/features/auth`. Les autres domaines cites
dans la story restent hors scope et doivent etre traites par stories separees.

## Risques restants

Risque residuel faible: la suite frontend complete et l'E2E navigateur n'ont
pas ete executes, mais les tests ciblees requis par la story et les guards
architecture ont passe.

## Focus reviewer

- Verifier que la suppression des deux exceptions auth est le seul changement
  dans `COMPONENT_API_IMPORT_EXCEPTIONS`.
- Verifier que le chemin auth canonique ne preserve aucun segment legacy
  `components/SignInForm` ou `components/SignUpForm`.
