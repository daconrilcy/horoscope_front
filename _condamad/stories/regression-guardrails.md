<!-- Registre vivant des invariants protegeant les stories CONDAMAD deja livrees ou pretes a implementer. -->

# CONDAMAD Regression Guardrails

Ce document est la reference commune que chaque nouvelle story doit consulter,
citer et enrichir avant d'etre marquee `ready-for-dev`.

Il est gere par le skill `condamad-regression-guardrails` et doit etre cree
depuis son template s'il est absent.

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
| RG-001 | `remove-historical-facade-routes` | Routes historiques / facades | Les facades historiques supprimees ne doivent pas etre reintroduites sous forme de wrapper, alias, fallback ou re-export. | Scan cible des chemins/symboles interdits + test de route runtime si API exposee. |
| RG-002 | `refactor-api-v1-routers` | Routeurs API v1 | Les routeurs API v1 doivent rester organises par responsabilite claire, sans deplacement opportuniste de logique metier dans la couche API. | Tests d'architecture routeurs + revue des imports et du diff des fichiers routeurs touches. |
| RG-003 | `converge-api-v1-route-architecture` | Architecture des routes API v1 | Les routes API v1 doivent rester montees via le mecanisme canonique choisi, sans registre concurrent. | Test d'inventaire runtime `app.routes` + OpenAPI snapshot avant/apres pour les chemins touches. |
| RG-004 | `centralize-api-http-errors` | Erreurs HTTP API | Les erreurs HTTP applicatives doivent rester centralisees: les routes ne reconstruisent pas localement l'enveloppe JSON et les services ne dependent pas de FastAPI. | Tests `test_api_error_*`, scan `HTTPException`, `JSONResponse`, helpers locaux et imports `app.api` depuis `services`. |
| RG-005 | `remove-api-v1-router-logic` | Frontiere API / services | La couche API ne doit pas redevenir proprietaire de logique metier ou de persistance. | Tests d'architecture + scan des imports infra/service et revue des handlers touches. |
| RG-006 | `api-adapter-boundary-convergence` | Frontiere adaptateur API | `backend/app/api` reste un adaptateur HTTP strict; les schemas restent des contrats purs et les couches non-API n'importent pas `app.api`. | Guards AST sur imports interdits + scans cibles `backend/app/services`, `backend/app/domain`, `backend/app/infra`, `backend/app/core`. |
| RG-007 | `converge-admin-llm-observability-router` | Endpoints admin LLM observability | `backend/app/api/v1/routers/admin/llm/observability.py` reste l'unique proprietaire runtime des endpoints observability, avec chemins et schemas preserves. | Inventaire runtime des proprietaires de routes + diff OpenAPI filtre + scan anti-retour des handlers dans `prompts.py`. |
| RG-008 | `harden-api-adapter-boundary-guards` | Exceptions de montage API et dette SQL routeurs | Les routes hors registre API v1 et les usages SQL directs restants dans les routeurs doivent rester exacts, justifies et bloques contre toute croissance silencieuse. | Inventaire runtime des routes + allowlist SQL exacte + garde AST anti-nouveaux imports/appels DB dans `backend/app/api/v1/routers` et `backend/app/api/dependencies`. |
| RG-009 | `api-adapter-boundary-convergence` | Package legacy `backend/app/api/v1/schemas` | L'ancien package `app.api.v1.schemas` ne doit pas etre recree comme facade vide, wrapper ou re-export; les contrats partages restent sous `app.services.api_contracts`. | Garde AST/fichier `test_api_v1_schemas_package_is_removed` + scan zero-hit `app.api.v1.schemas` dans `backend/app` et `backend/tests`. |
| RG-010 | `converge-backend-test-topology` | Topologie des tests backend | Les fichiers de tests backend doivent rester sous les racines documentees et collectees par `backend/pyproject.toml`; aucun test embarque sous `backend/app/**/tests` hors `backend/app/tests` ne doit revenir. | `pytest -q app/tests/unit/test_backend_test_topology.py` + `pytest -q app/tests/unit/test_backend_pytest_collection.py` + collecte pytest standard. |
| RG-011 | `converge-db-test-fixtures` | Harnais DB des tests backend | Les nouveaux tests backend ne doivent pas importer directement `SessionLocal` ou `engine` depuis `app.infra.db.session`; ils doivent passer par les helpers/fixtures DB canoniques ou par une exception allowlistee. | `pytest -q app/tests/unit/test_backend_db_test_harness.py` + inventaire `rg` des imports DB directs. |

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
rg "HTTPException|JSONResponse|def _error_response|api_error_response" backend/app/api backend/app/services
rg "from app\.api|import app\.api" backend/app/services backend/app/domain backend/app/infra backend/app/core
rg "list_call_logs|get_dashboard|replay_request|purge_logs" backend/app/api/v1/routers/admin/llm
```
