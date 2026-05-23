<!-- Registre vivant des invariants protegeant les stories CONDAMAD deja livrees ou pretes a implementer. -->

# CONDAMAD Regression Guardrails

Ce document est la reference commune que chaque nouvelle story doit consulter,
citer et enrichir avant d'etre marquee `ready-for-dev`.

Son objectif est d'eviter qu'une story locale casse un comportement, un contrat
ou une decision d'architecture acquis par une story precedente.

## Usage obligatoire pour une nouvelle story

Toute nouvelle story sous `_condamad/stories/<story-key>/00-story.md` doit:

1. Lire ce registre avant de definir son scope.
2. Ajouter dans sa section `Current State Evidence` une preuve de consultation:
   - `Evidence N: _condamad/stories/regression-guardrails.md - invariants consultes avant cadrage.`
3. Ajouter dans `Explicit non-goals` les invariants applicables qu'elle ne doit pas changer.
4. Ajouter dans `Acceptance Criteria` au moins un AC de non-regression quand un invariant applicable existe.
5. Ajouter dans `Validation Plan` les commandes de garde correspondantes.
6. Enrichir ce registre si la story cree un nouvel invariant durable.

Une story qui modifie une surface couverte par ce registre doit capturer un
baseline avant/apres et documenter les differences autorisees dans son dossier.

## Controle avant ready-for-dev

Avant de passer une story a `ready-for-dev`, verifier:

- Le domaine de la story est unique et ne contourne pas un proprietaire canonique existant.
- Les stories precedentes impactables sont listees dans la story.
- Les invariants applicables ci-dessous sont cites comme non-goals ou AC.
- Les snapshots avant/apres sont prevus pour les routes, l'OpenAPI, les imports ou les contrats touches.
- Les guards anti-reintroduction sont deterministes: test AST, inventaire runtime, diff OpenAPI ou scan cible.
- Aucune compatibilite transitoire, alias, fallback ou re-export legacy n'est autorise sans decision explicite.

## Invariants actifs

| ID | Source story | Surface protegee | Invariant | Guard attendu |
|---|---|---|---|---|
| RG-002 | `bootstrap-backend-layout` | Structure backend racine | Les nouveaux modules backend doivent rester dans une structure explicite `backend/app` et `backend/tests`, sans racine ad hoc. | Revue des chemins modifies + tests backend cibles. |
| RG-003 | `bootstrap-api-boundary` | `backend/app/api` | Les routes API doivent rester des adaptateurs HTTP sans logique metier, persistance ou orchestration lourde. | Revue `backend/app/api` + tests API. |
| RG-007 | `bootstrap-api-contracts` | Contrats API | Tout contrat API public doit declarer methode, chemin, status et JSON attendus, avec preuve OpenAPI ou test API. | `app.openapi()` ou snapshot OpenAPI + test API. |
| RG-020 | `bootstrap-auth-security` | Authentification et autorisation | Les routes protegees doivent rester couvertes par les controles auth/permission canoniques. | Tests auth/permission + revue des dependencies route. |
| RG-022 | `bootstrap-tests` | Topologie des tests Python | Les tests backend doivent vivre dans des dossiers collectes par pytest et rester executables localement. | `pytest --collect-only` ou test cible sous `backend/tests`. |
| RG-041 | `bootstrap-build` | Build Vite | La configuration Vite doit rester minimale et explicite; les aliases, plugins et variables frontend doivent etre documentes. | `npm run build` + revue `vite.config.*`, `tsconfig*.json`, `.env*`. |
| RG-047 | `bootstrap-local-validation` | Validation locale sans CI | Une story ready doit fournir des commandes locales executables et une preuve persistante quand le scope le demande. | `condamad_story_validate.py`, `condamad_story_lint.py --strict`, tests cibles. |
| RG-052 | `bootstrap-no-legacy` | No Legacy | Aucun shim, alias, wrapper, fallback, re-export, namespace legacy ou vocabulaire legacy ne doit etre cree pour eviter une vraie migration. | Scan cible `legacy|compat|fallback|alias|shim|deprecated` + revue des chemins modifies. |
| RG-053 | `health-endpoint` | `GET /health` backend API | Le contrat public de health check doit rester limite a `GET /health` avec reponse JSON exacte `{"status":"ok"}`; aucun chemin `/api/health`, `/healthz`, `/ready` ou `/status` ne doit etre cree sans decision explicite. | Test API cible + assertion runtime `app.routes`/`app.openapi()` + scan cible des chemins interdits. |

## Format d'enrichissement

Quand une story cree un invariant durable, ajouter une ligne a `Invariants actifs`
avec:

- `ID`: prochain identifiant `RG-XXX`.
- `Source story`: dossier de story.
- `Surface protegee`: route, module, contrat, ownership, comportement ou artefact.
- `Invariant`: regle stable a proteger.
- `Guard attendu`: preuve executable ou audit determine qui echoue en cas de regression.

L'invariant doit etre concret. Eviter les formulations vagues comme "ne pas
casser l'existant"; nommer le contrat, le proprietaire, le chemin, le module ou
le symbole protege.

## Snippet a copier dans les nouvelles stories

```md
## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-XXX` - <raison concrete pour laquelle l'invariant s'applique>
- Non-applicable invariants:
  - `RG-YYY` - <raison concrete pour laquelle la story ne touche pas cette surface>
- Required regression evidence:
  - <test, scan, snapshot, diff ou audit>
- Allowed differences:
  - <differences explicitement autorisees, ou "none">
```

## Commandes de controle recommandees

Adapter les commandes au scope de la story. Les commandes Python doivent etre
executees apres activation du venv.

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/<story-key>/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/<story-key>/00-story.md
```

Commandes indicatives selon les surfaces touchees:

```powershell
rg "<forbidden-symbol-or-import>" <paths>
```
