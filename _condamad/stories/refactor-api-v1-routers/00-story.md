# Story refactor-api-v1-routers: Organiser les routers API v1 par domaine

Status: ready-for-review

## 1. Objective

Reorganiser `backend/app/api/v1/routers` en modules de routes classes par domaine, en gardant les endpoints publics encore utilises,
en supprimant uniquement les routes prouvees mortes, en deplacant les schemas Pydantic hors des routers, et en deleguant la logique non HTTP
aux couches backend existantes (`services`, `infra`, `domain`) sans duplication.

## 2. Trigger / Source

- Source type: refactor
- Source reference: demande utilisateur du 2026-04-26 sur `backend/app/api/v1/routers`
- Reason for change: le repertoire contient un melange de routers plats, de namespaces deja amorces, de schemas dans les routers, et de logique metier
  directement presente dans des fonctions et helpers de route.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/api/v1/routers`
- In scope:
  - Auditer tous les fichiers Python sous `backend/app/api/v1/routers`.
  - Regrouper les routers dans des sous-dossiers existants ou nouveaux sous `backend/app/api/v1/routers`.
  - Classer les modules par domaine API visible: `admin`, `admin/llm`, `b2b`, `ops`, `internal/llm`, `public`, ou noms equivalents prouves par les prefixes.
  - Extraire les schemas Pydantic declares dans les routers vers des modules dedies sous le meme domaine API.
  - Deplacer la logique non HTTP vers des services, repos ou helpers deja existants, ou vers de nouveaux fichiers strictement necessaires.
  - Supprimer les routes et imports legacy uniquement quand une preuve backend et frontend montre qu'elles ne sont plus consommees.
- Out of scope:
  - Changer les URLs publiques encore consommees.
  - Modifier les contrats de reponse hors extraction de schemas sans changement comportemental.
  - Revoir la logique metier des domaines `billing`, `llm`, `privacy`, `support`, `users`, `predictions`.
  - Ajouter une authentification, une pagination ou une nouvelle politique CORS.
- Explicit non-goals:
  - Ne pas introduire de wrappers de compatibilite entre anciens et nouveaux chemins Python.
  - Ne pas garder deux modules actifs pour le meme router.
  - Ne pas modifier le frontend sauf correction stricte d'un import ou appel prouve obsolète.
  - Ne pas ajouter de dossier de base dans `backend/` hors sous-dossiers du package `app` deja autorise.

## 4. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/api/v1/routers` - l'audit local recense 59 fichiers Python de routers ou namespaces, hors `__pycache__`.
- Evidence 2: `backend/app/api/v1/routers/admin/llm` - un namespace par sous-dossier existe deja, mais ses modules re-exportent encore des routers plats.
- Evidence 3: `backend/app/api/v1/routers/admin_llm.py` - contient le router `/v1/admin/llm`, 24 decorators `@router`, 40 schemas `BaseModel`,
  et plusieurs helpers de logique applicative.
- Evidence 4: `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py` - contient le router `/v1/ops/entitlements`, 17 decorators `@router`,
  et 49 schemas `BaseModel`.
- Evidence 5: `backend/app/api/v1/routers/admin_content.py` - contient le router `/v1/admin/content`, 10 decorators `@router`, et 19 schemas `BaseModel`.
- Evidence 6: `backend/app/main.py` - importe encore de nombreux routers plats comme `admin_ai`, `admin_audit`, `b2b_astrology`,
  `ops_monitoring`, `predictions`, `privacy`, `support` et `users`.
- Evidence 7: `backend/app/api/v1/routers/__init__.py` - expose encore des imports de routers plats, ce qui cree un point de compatibilite implicite.
- Evidence 8: `backend/app/api/v1/routers/admin\llm\__init__.py` - importe les anciens modules `admin_llm*`, signe d'une transition non terminee.
- Evidence 9: `backend/tests/integration/test_admin_llm_catalog.py` et `backend/app/tests/integration/test_daily_prediction_api.py` - patchent
  des symboles situes dans des routers, ce qui prouve que certains tests encodent la logique dans la couche route.
- Evidence 10: `frontend/src` - les appels frontend doivent etre audites par URL HTTP, car l'usage d'un endpoint ne se deduit pas des noms Python.

## 5. Target State

After implementation:

- Chaque router actif a un emplacement canonique unique dans un sous-dossier de `backend/app/api/v1/routers` correspondant a son domaine API.
- `backend/app/main.py` importe les routers depuis les chemins canoniques, sans re-export par ancien module plat.
- Les schemas Pydantic utilises par les endpoints vivent dans des fichiers dedies du domaine API concerne.
- Les fonctions de route contiennent uniquement la lecture des dependances FastAPI, l'appel au service ou composant backend approprie,
  la traduction HTTP des erreurs, et la construction finale de la reponse.
- Les routes supprimees sont accompagnees d'une preuve negative d'usage backend et frontend.
- Des tests d'architecture empechent le retour des imports legacy, des schemas `BaseModel` dans les routers, et des gros blocs de logique dans les routes.

## 6. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Inventaire complet: fichier, prefixe, endpoints, schemas et usages. | `rg -n "APIRouter\(|@router\.|/v1/" backend/app frontend/src` plus audit versionne. |
| AC2 | Tous les routers actifs sont classes par domaine API. | `rg -n "from app\.api\.v1\.routers\.[a-z0-9_]+ import router" backend/app backend/tests`. |
| AC3 | Aucun ancien module plat ne reste comme wrapper, alias, fallback ou re-export. | `rg -n "admin_llm|admin_|b2b_|ops_" backend/app/main.py backend/tests`. |
| AC4 | Les schemas Pydantic des routers migres vivent dans des fichiers dedies. | `rg -n "class .*\(BaseModel\)" backend/app/api/v1/routers --glob "*.py"`. |
| AC5 | La logique non HTTP des routers migres sort vers une couche backend canonique. | `pytest -q backend/app/tests/unit/test_api_router_architecture.py`. |
| AC6 | Les routes legacy ou inutilisees sont supprimees apres preuve negative. | `pytest -q backend/app/tests/integration` plus audit de suppression versionne. |
| AC7 | Les endpoints conserves gardent URLs, tags, status codes et OpenAPI. | `pytest -q backend/app/tests/integration/test_api_v1_router_contracts.py`. |
| AC8 | Le backend passe lint et tests cibles dans le venv Windows. | `.\.venv\Scripts\Activate.ps1; cd backend; ruff format .; ruff check .; pytest -q`. |

## 7. Implementation Tasks

- [x] Task 1 - Produire l'audit route par route avant modification (AC: AC1, AC6)
  - [x] Subtask 1.1 - Lister tous les fichiers sous `backend/app/api/v1/routers`, leurs prefixes `APIRouter`, decorators, schemas et helpers.
  - [x] Subtask 1.2 - Croiser chaque route avec `backend/app/main.py`, `backend/tests`, `backend/app/tests` et `frontend/src`.
  - [x] Subtask 1.3 - Ecrire l'audit et les candidats a suppression sous `_condamad/stories/refactor-api-v1-routers/`.

- [x] Task 2 - Definir et appliquer la structure canonique des sous-dossiers (AC: AC2, AC3, AC7)
  - [x] Subtask 2.1 - Reutiliser `backend/app/api/v1/routers/admin/llm` et `backend/app/api/v1/routers/internal/llm`.
  - [x] Subtask 2.2 - Creer uniquement les sous-dossiers necessaires sous `backend/app/api/v1/routers` pour `admin`, `b2b`, `ops` et routes publiques.
  - [x] Subtask 2.3 - Mettre a jour `backend/app/main.py` pour importer les routers depuis les chemins canoniques.
  - [x] Subtask 2.4 - Supprimer les wrappers ou re-exports plats remplaces par les chemins canoniques.

- [x] Task 3 - Extraire les schemas Pydantic des routers migres (AC: AC4, AC7)
  - [x] Subtask 3.1 - Creer des modules de schemas par domaine API sous les sous-dossiers concernes.
  - [x] Subtask 3.2 - Remplacer les definitions locales `BaseModel` par des imports depuis ces modules.
  - [x] Subtask 3.3 - Ajouter un test d'architecture qui echoue si un router migre declare de nouveaux schemas localement.

- [x] Task 4 - Sortir la logique non HTTP des routes (AC: AC5, AC7)
  - [x] Subtask 4.1 - Identifier les helpers prives des routers qui calculent, filtrent, ecrivent en base, appellent un gateway ou composent une reponse metier.
  - [x] Subtask 4.2 - Reutiliser les services, repos et fonctions existants avant de creer un nouveau fichier.
  - [x] Subtask 4.3 - Creer les fichiers manquants seulement dans le domaine backend approprie avec commentaire global et docstrings en francais.
  - [x] Subtask 4.4 - Adapter les tests qui patchent des symboles dans les routers pour cibler les services canoniques.

- [x] Task 5 - Supprimer les routes prouvees mortes (AC: AC1, AC6)
  - [x] Subtask 5.1 - Pour chaque suppression candidate, fournir une preuve `rg` backend et frontend dans l'audit.
  - [x] Subtask 5.2 - Supprimer le route handler, le schema dedie, l'import `include_router` et les tests nominaux associes a l'ancien comportement.
  - [x] Subtask 5.3 - Garder un test negatif ou une note d'audit pour chaque URL supprimee si le risque de retour legacy est eleve.

- [x] Task 6 - Ajouter les garde-fous et lancer la validation (AC: AC2, AC3, AC4, AC5, AC7, AC8)
  - [x] Subtask 6.1 - Ajouter ou mettre a jour `backend/app/tests/unit/test_api_router_architecture.py`.
  - [x] Subtask 6.2 - Ajouter ou mettre a jour `backend/app/tests/integration/test_api_v1_router_contracts.py`.
  - [x] Subtask 6.3 - Lancer lint, tests cibles, puis suite backend selon le temps disponible, toujours apres activation du venv.

## 8. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/api/v1/routers/admin/llm` pour les routes Admin LLM deja amorcees.
  - `backend/app/api/v1/routers/internal/llm` pour les routes QA internes LLM.
  - `backend/app/services` avant tout nouveau service.
  - `backend/app/infra` avant tout nouveau repository ou client externe.
  - `backend/app/domain` avant toute nouvelle regle metier locale au router.
- Do not recreate:
  - Gestion des roles, rate limits, audit events, erreurs standard et acces DB si une fonction ou classe existe deja.
  - Schemas identiques dans deux fichiers.
  - Tests qui patchent un ancien chemin Python et un nouveau chemin Python pour la meme responsabilite.
- Shared abstraction allowed only if:
  - Au moins deux routers actifs utilisent la meme responsabilite.
  - Aucun module existant ne porte deja cette responsabilite.
  - Le fichier cree est dans le domaine canonique et documente son intention en francais.

## 9. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- `backend/app/api/v1/routers/admin_llm.py` comme source canonique si son contenu est migre sous `admin/llm`.
- `backend/app/api/v1/routers/admin_llm_assembly.py` comme wrapper de `admin/llm/assemblies.py`.
- `backend/app/api/v1/routers/admin_llm_consumption.py` comme wrapper de `admin/llm/consumption.py`.
- `backend/app/api/v1/routers/admin_llm_release.py` comme wrapper de `admin/llm/releases.py`.
- `backend/app/api/v1/routers/admin_llm_sample_payloads.py` comme wrapper de `admin/llm/sample_payloads.py`.
- Imports applicatifs depuis `app.api.v1.routers` pour contourner le chemin canonique.

## 10. Files to Inspect First

Codex must inspect before editing:

- `backend/app/main.py`
- `backend/app/api/v1/routers`
- `backend/app/api/v1/routers/__init__.py`
- `backend/app/api/v1/routers/admin/llm/__init__.py`
- `backend/app/api/v1/routers/admin_llm.py`
- `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py`
- `backend/app/api/v1/routers/admin_content.py`
- `backend/app/services`
- `backend/app/infra`
- `backend/app/domain`
- `backend/app/tests/integration`
- `backend/tests/integration`
- `frontend/src/api`
- `frontend/src/pages`
- `frontend/src/components`

## 11. Expected Files to Modify

Likely files:

- `backend/app/main.py` - importer et inclure les routers depuis les chemins canoniques.
- `backend/app/api/v1/routers/admin/llm` - remplacer les re-exports par les modules canoniques.
- `backend/app/api/v1/routers/admin` - accueillir les routers admin hors LLM.
- `backend/app/api/v1/routers/b2b` - accueillir les routers B2B publics et ops B2B selon l'audit.
- `backend/app/api/v1/routers/ops` - accueillir les routers operationnels.
- `backend/app/api/v1/routers/public` - accueillir les routes publiques ou utilisateur si ce nom est confirme par l'audit.
- `backend/app/api/v1/routers/*/schemas.py` - recevoir les schemas Pydantic extraits.
- `backend/app/services` - recevoir seulement les cas d'usage manquants apres recherche DRY.
- `backend/app/infra` - recevoir seulement les acces techniques manquants apres recherche DRY.
- `_condamad/stories/refactor-api-v1-routers/router-audit.md` - documenter l'inventaire et les suppressions.

Likely tests:

- `backend/app/tests/unit/test_api_router_architecture.py` - garde imports legacy, schemas dans routers, wrappers et logique locale.
- `backend/app/tests/integration/test_api_v1_router_contracts.py` - garde les endpoints conserves et OpenAPI.
- `backend/app/tests/integration/test_daily_prediction_api.py` - adapter les patchs qui ciblent `routers.predictions` si le domaine bouge.
- `backend/tests/integration/test_admin_llm_catalog.py` - adapter les patchs qui ciblent `routers.admin_llm` si Admin LLM bouge.
- `backend/tests/unit/test_admin_manual_execute_response.py` - adapter les imports de helpers si leur responsabilite sort du router.

Files not expected to change:

- `backend/pyproject.toml` - aucune dependance nouvelle n'est autorisee.
- `frontend/package.json` - aucun changement frontend structurel n'est requis.
- `backend/alembic` - aucune migration DB n'est attendue.
- `backend/app/infra/db/models` - aucun modele DB ne doit etre modifie pour ce rangement API.

## 12. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 13. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q backend/app/tests/unit/test_api_router_architecture.py
pytest -q backend/app/tests/integration/test_api_v1_router_contracts.py
pytest -q backend/app/tests/integration
pytest -q backend/tests/integration
rg -n "from app\.api\.v1\.routers\.[a-z0-9_]+ import router|from app\.api\.v1\.routers import .*_router" backend/app backend/tests
rg -n "class .*\(BaseModel\)" backend/app/api/v1/routers --glob "*.py"
```

Si une suite complete est trop longue, enregistrer dans le recap les suites lancees, les suites non lancees, et le risque residuel.

## 14. Regression Risks

- Risk: casser un endpoint encore appele par le frontend parce que le nom Python semblait legacy.
  - Guardrail: supprimer seulement apres audit URL dans `frontend/src` et audit `include_router` dans backend.
- Risk: remplacer une duplication apparente par un nouveau service alors qu'un service existe deja.
  - Guardrail: rechercher dans `backend/app/services`, `backend/app/domain` et `backend/app/infra` avant creation.
- Risk: perdre des patchs de tests qui ciblaient des helpers de router.
  - Guardrail: adapter les tests vers les services canoniques et ajouter une garde d'import legacy.
- Risk: changer l'OpenAPI sans intention.
  - Guardrail: ajouter un test de contrat sur les routes conservees avant suppression des chemins plats.

## 15. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Respecter l'activation du venv avant toute commande Python: `.\.venv\Scripts\Activate.ps1`.
- Ne pas creer de `requirements.txt`; `backend/pyproject.toml` reste la source des dependances.
- Tout fichier applicatif nouveau ou significativement modifie doit avoir un commentaire global en francais et des docstrings en francais
  pour les fonctions publiques ou non triviales.
- Ne pas ajouter de style frontend ou de dossier racine backend.

## 16. References

- `backend/app/api/v1/routers` - domaine cible de la reorganisation.
- `backend/app/main.py` - point de montage FastAPI des routers v1.
- `backend/app/api/v1/routers/admin/llm` - namespace deja en place a reutiliser.
- `backend/app/api/v1/routers/internal/llm` - namespace interne deja en place a reutiliser.
- `frontend/src` - preuve d'usage ou non-usage des URLs HTTP.
- `backend/app/tests` et `backend/tests` - suites a adapter et validation comportementale.
