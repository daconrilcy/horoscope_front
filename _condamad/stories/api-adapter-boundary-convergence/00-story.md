# Story api-adapter-boundary-convergence: Converge API Adapter Boundaries And Remove Legacy HTTP Surfaces

Status: completed

## 1. Objective

Converger `backend/app/api` vers une couche adaptateur HTTP stricte, DRY et sans legacy
résiduel. Les schémas API v1 deviennent des contrats Pydantic purs, les couches
non-API ne dépendent plus de `app.api`, les routeurs sont enregistrés via un
registre, et les surfaces d'erreur HTTP legacy sont supprimées ou bloquées par
décision explicite.

## 2. Trigger / Source

- Source type: audit
- Source reference: audit Codex du dossier `backend/app/api` demandé par l'utilisateur le 2026-04-27.
- Reason for change: l'audit a identifié des restes legacy et anti-DRY mesurables:
  FastAPI dans les schémas, dépendances `services vers app.api`, registre de routeurs
  dupliqué dans `main.py`, compatibilité `raise_http_error/detail`, route hors `/v1`
  allowlistée, et garde-fous incomplets.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/api`
- Scope clarification:
  - Le domaine primaire est `backend/app/api`.
  - Les modifications hors `backend/app/api` sont autorisées uniquement pour supprimer
    une dépendance entrante vers l'API depuis `services`, `domain`, `infra` ou `core`.
  - Ces modifications doivent rester limitées aux imports, DTO partagés et exceptions
    applicatives nécessaires.
  - Aucune règle métier hors API ne doit être refactorée.
- In scope:
  - Purifier `backend/app/api/v1/schemas` pour supprimer les imports et objets FastAPI.
  - Déplacer ou créer les contrats partagés nécessaires hors de `app.api` uniquement quand cela sert à supprimer une dépendance entrante des services vers l'API.
  - Mettre à jour les imports des couches non-API concernées qui consomment aujourd'hui
    des contrats ou dépendances `app.api`.
  - Centraliser l'inventaire et l'enregistrement des routeurs API v1 pour réduire la duplication dans `backend/app/main.py`.
  - Remplacer les appels API legacy `raise_http_error` par des erreurs applicatives canoniques.
  - Ajouter ou renforcer les tests d'architecture pour bloquer la réintroduction des surfaces interdites.
- Out of scope:
  - Changer les routes publiques, payloads métier ou comportements fonctionnels hors suppression explicite de surfaces legacy internes.
  - Refactorer les règles métier des services B2B, billing, LLM, entitlement, geocoding, support, privacy ou prediction au-delà des imports/contrats requis.
  - Modifier le frontend.
  - Créer une nouvelle organisation globale du backend hors des chemins nécessaires à cette story.
- Explicit non-goals:
  - Ne pas ajouter de compatibilité transitoire, wrapper, alias, fallback ou re-export.
  - Ne pas renommer les endpoints HTTP canoniques.
  - Ne pas supprimer la route email historique `/api/email/unsubscribe` sans preuve d'absence d'usage externe ou décision utilisateur explicite.
  - Ne pas transformer cette story en refactor général de tous les gros routeurs.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: legacy-facade-removal
- Archetype reason: la story supprime des surfaces de compatibilité HTTP et Python:
  `raise_http_error`, `legacy_detail`, FastAPI dans les schémas, et imports
  `services vers app.api`.
- Behavior change allowed: yes
  - Constrained: allowed only for surfaces classified `dead` or `historical-facade` with no
    external blocker.
  - Any public HTTP payload change, including removal of a top-level error field
    such as `detail`, requires proof of non-consumption or explicit user decision.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: une surface legacy est référencée par un contrat externe
  actif, une documentation publique, un template email, un client généré, ou si sa
  suppression changerait un payload HTTP consommé hors tests internes.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/api/v1/schemas/routers/public/auth.py` - un module de
  schémas importe `APIRouter` et définit un objet `router`.
- Evidence 2: commande audit sur `backend/app/api/v1/schemas` - 39 fichiers de
  schémas contiennent encore des imports ou symboles FastAPI.
- Evidence 3: `backend/app/services/b2b/api_billing.py` et plusieurs services importent `app.api.dependencies.*`, ce qui fait dépendre la couche services de la couche API.
- Evidence 4: `backend/app/services/consultation/precheck_service.py` et plusieurs
  services importent `app.api.v1.schemas.routers.*`.
- Evidence 5: `backend/app/main.py` lignes 20-76 et 647-696 - les imports et
  inclusions de routeurs sont maintenus manuellement.
- Evidence 6: `backend/app/api/errors/raising.py` - `raise_http_error` convertit
  une intention HTTP legacy vers une erreur canonique et conserve `legacy_detail`.
- Evidence 7: `backend/app/api/errors/handlers.py` - `build_error_response`
  réinjecte `content["detail"]` quand `legacy_detail` existe.
- Evidence 8: `backend/app/tests/unit/test_api_router_architecture.py` - des
  garde-fous existent déjà, mais ne bloquent pas FastAPI dans `schemas` ni les
  imports `services vers app.api`.
- Evidence 9: `backend/app/main.py` ligne 696 - `email_router` est monté sous `/api`, exception historique active hors `/v1`.

## 6. Target State

After implementation:

- `backend/app/api/v1/schemas` ne reste pas comme namespace actif. Les contrats
  partagés vivent sous `backend/app/services/api_contracts` et l'ancien package
  `app.api.v1.schemas` est supprimé pour éviter wrapper, facade vide ou re-export.
- `backend/app/services`, `backend/app/domain`, `backend/app/infra` et
  `backend/app/core` n'importent plus `app.api.*`.
- `backend/app/main.py` consomme un registre unique de routeurs API v1 au lieu de maintenir une longue liste d'import/inclusion.
- `raise_http_error`, `legacy_detail` et le champ top-level `detail` des erreurs
  applicatives internes sont supprimés uniquement pour les surfaces prouvées non
  consommées ou après décision utilisateur explicite.
- La route `/api/email/unsubscribe` est conservée comme `external-active` documentée,
  ou traitée seulement après décision utilisateur.
- Les tests d'architecture échouent si les anciennes surfaces reviennent.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `backend/app/api/v1/schemas` est indépendant de FastAPI. | AST guard for forbidden imports/symbols; `rg` scan is indicative only. |
| AC2 | `backend/app/services`, `domain`, `infra` et `core` ne dépendent plus de `app.api`. | AST guard for forbidden imports; targeted `rg` on non-API layers. |
| AC3 | Les contrats déplacés ont un propriétaire canonique unique hors `app.api`. | Targeted `rg` for schema imports in `app/services app/domain app/infra app/core`; audit file. |
| AC4 | Les routeurs API v1 sont enregistrés via un registre unique. | `pytest -q backend/app/tests/unit/test_api_router_architecture.py`; `rg` on `main.py`. |
| AC5 | Les surfaces d'erreur HTTP legacy ne restent pas nominales. | Negative `rg` for legacy error symbols only for `delete` or `replace-consumer`; remaining refs in audit. |
| AC6 | Toute surface historique hors `/v1` est classifiée avant action. | `pytest -q backend/app/tests/unit/test_api_router_architecture.py`; `removal-audit.md`. |
| AC7 | Aucun gros routeur ne reçoit de nouvelle logique métier. | `git diff -- backend/app/api/v1/routers`; targeted `pytest` for touched routers. |
| AC8 | Les garde-fous No Legacy/DRY bloquent toute réintroduction. | `pytest -q backend/app/tests/unit/test_api_router_architecture.py`; AC1/AC2/AC5 scans. |
| AC9 | Le backend démarre et l'OpenAPI reste cohérent. | `python -c "from app.main import app; assert app.openapi()['paths']"`; OpenAPI snapshot before/after. |
| AC10 | Lint, format et tests ciblés passent dans le venv. | `ruff format .`, `ruff check .`, targeted `pytest`, and broader `pytest -q` or skip risk. |

## 8. Implementation Tasks

- [ ] Task 1 - Auditer et classifier les surfaces à déplacer/supprimer (AC: AC1, AC2, AC3, AC5, AC6, AC9)
  - [ ] Subtask 1.1 - Produire `_condamad/stories/api-adapter-boundary-convergence/removal-audit.md` avec la table requise de classification.
  - [ ] Subtask 1.2 - Produire dans le même fichier ou dans une section dédiée l'inventaire des contrats `app.api.v1.schemas.*` consommés par `backend/app/services`.
  - [ ] Subtask 1.3 - Marquer `/api/email/unsubscribe` comme `external-active` sauf preuve contraire explicite.
  - [ ] Subtask 1.4 - Capturer le snapshot OpenAPI des chemins avant modification.

- [ ] Task 2 - Ajouter les garde-fous d'architecture avant refactor (AC: AC1, AC2, AC4, AC6, AC8)
  - [ ] Subtask 2.1 - Ajouter des guards AST pour les imports/symboles interdits dans `schemas`.
  - [ ] Subtask 2.2 - Ajouter des guards AST pour les imports `app.api` depuis `services`, `domain`, `infra` et `core`.
  - [ ] Subtask 2.3 - Ajouter ou ajuster les guards du registre routeur et des endpoints hors `/v1`.

- [ ] Task 3 - Purifier les schémas API v1 (AC: AC1, AC3, AC8)
  - [ ] Subtask 3.1 - Supprimer `APIRouter`, `router`, imports FastAPI et imports de réponses FastAPI des fichiers sous `backend/app/api/v1/schemas`.
  - [ ] Subtask 3.2 - Ne conserver dans ces fichiers que les modèles Pydantic, types, validateurs et docstrings de contrat.

- [ ] Task 4 - Découpler les couches non-API de `app.api` (AC: AC2, AC3, AC8)
  - [ ] Subtask 4.1 - Déplacer les DTO réellement partagés vers un propriétaire canonique hors `app.api`, en privilégiant un namespace existant et proche du domaine consommateur.
  - [ ] Subtask 4.2 - Remplacer les imports depuis `services`, `domain`, `infra`
    et `core` par le propriétaire canonique.
  - [ ] Subtask 4.3 - Ne pas ajouter de re-export sous l'ancien chemin `app.api.*`.

- [ ] Task 5 - Centraliser l'enregistrement des routeurs API v1 (AC: AC4, AC8, AC9)
  - [ ] Subtask 5.1 - Créer ou compléter `backend/app/api/v1/routers/registry.py` sans importer de routeur depuis les schémas.
  - [ ] Subtask 5.2 - Réduire `backend/app/main.py` à l'utilisation du registre pour les routeurs API v1.
  - [ ] Subtask 5.3 - Conserver la logique conditionnelle du routeur interne LLM QA sans l'exposer en production par erreur.
  - [ ] Subtask 5.4 - Ajouter un garde-fou qui compare le registre avec les routes API v1 effectivement montées.

- [ ] Task 6 - Supprimer les surfaces d'erreur legacy internes (AC: AC5, AC8, AC9)
  - [ ] Subtask 6.1 - Dans les routeurs/adaptateurs HTTP, remplacer `raise_http_error` par `raise_api_error`.
  - [ ] Subtask 6.2 - Dans les services, remplacer toute erreur API par des exceptions applicatives typées hors `app.api`.
  - [ ] Subtask 6.3 - Supprimer `raise_http_error`, `legacy_detail`, et l'injection top-level `detail` seulement avec preuve de non-consommation ou décision utilisateur.
  - [ ] Subtask 6.4 - Si un consommateur externe impose encore `detail`, bloquer la
    suppression et demander une décision utilisateur.

- [ ] Task 7 - Traiter explicitement les endpoints hors `/v1` (AC: AC6, AC8)
  - [ ] Subtask 7.1 - Vérifier les consommateurs de `/api/email/unsubscribe` dans templates email, frontend, docs et tests.
  - [ ] Subtask 7.2 - Maintenir l'allowlist exacte si externe-active; sinon escalader avant suppression.
  - [ ] Subtask 7.3 - Empêcher tout endpoint monté hors `/v1` par FastAPI sans entrée dans `NON_V1_ROUTE_EXCEPTIONS`.

- [ ] Task 8 - Validation finale et preuves (AC: AC7, AC8, AC9, AC10)
  - [ ] Subtask 8.1 - Capturer le snapshot OpenAPI après modification, comparer
    avec le snapshot initial, et sauvegarder les deux sorties dans l'audit ou les preuves finales.
  - [ ] Subtask 8.2 - Exécuter les guards AST et scans indicatifs AC1, AC2 et AC5.
  - [ ] Subtask 8.3 - Exécuter tests d'architecture, tests d'erreurs API, et tests des routeurs touchés.
  - [ ] Subtask 8.4 - Exécuter lint/format dans le venv.
  - [ ] Subtask 8.5 - Documenter tout test non exécuté avec raison et risque.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/api/errors/catalog.py` pour résoudre les statuts HTTP depuis les codes applicatifs.
  - `backend/app/api/errors/handlers.py` pour construire l'enveloppe d'erreur canonique.
  - `backend/app/tests/unit/test_api_router_architecture.py` comme emplacement principal des garde-fous API.
  - Les namespaces `backend/app/services`, `backend/app/domain` ou `backend/app/infra` existants selon la responsabilité des contrats déplacés.
- Do not recreate:
  - Un deuxième catalogue d'erreurs.
  - Des wrappers `schemas` qui réexportent les nouveaux contrats.
  - Un deuxième registre de routeurs.
  - Des dépendances d'authentification utilisables par les services hors adaptateur HTTP.
- Shared abstraction allowed only if:
  - Elle remplace une duplication observée par scan.
  - Elle a au moins deux consommateurs réels.
  - Son propriétaire canonique est documenté dans l'audit de cette story.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- `router = APIRouter` sous `backend/app/api/v1/schemas`
- `from fastapi import` sous `backend/app/api/v1/schemas`
- `from fastapi.responses import` sous `backend/app/api/v1/schemas`
- `from app.api` sous `backend/app/services`
- `raise_http_error`
- `legacy_detail`
- `content["detail"]` dans le handler d'erreur canonique
- Nouveaux modules plats sous `backend/app/api/v1/routers/*.py` hors `__init__.py`
  et hors registre explicitement autorisé `registry.py`
- Tout endpoint monté hors préfixe `/v1` par FastAPI sans entrée explicite dans
  `NON_V1_ROUTE_EXCEPTIONS`

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is the canonical owner.
- `external-active`: item is referenced by public docs, email templates, generated links, clients, or audit evidence.
- `historical-facade`: item delegates to a canonical implementation only to preserve an old surface.
- `dead`: item has zero references in production code, tests, docs, generated contracts, and known external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep`, `replace-consumer` | Must not be deleted; consumers may move to canonical owner. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `replace-consumer`, `delete`, `needs-user-decision` | Consumers move first; facade is then deleted when no external blocker remains. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions:

- `keep`
- `delete`
- `replace-consumer`
- `needs-user-decision`

Audit output path when applicable:

- `_condamad/stories/api-adapter-boundary-convergence/removal-audit.md`

The audit must include at minimum:

- `raise_http_error`
- `legacy_detail`
- top-level error `detail`
- FastAPI objects under `backend/app/api/v1/schemas`
- `backend/app/services` imports from `app.api.*`
- `/api/email/unsubscribe`
- any route/schema module discovered as dead during implementation

AC5 exception:

- Negative scans are required only for surfaces classified as `delete` or
  `replace-consumer`.
- If a surface is classified `external-active` or `needs-user-decision`, the
  audit must document the remaining references, the blocker, and the exact guard
  preventing expansion.

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| HTTP routing and FastAPI dependencies | `backend/app/api` route modules and dependency modules | `backend/app/api/v1/schemas` defining routers or FastAPI dependencies |
| API error envelope | `backend/app/api/errors/contracts.py` and `backend/app/api/errors/handlers.py` | `raise_http_error`, `legacy_detail`, top-level `detail` compatibility |
| API v1 route registration | `backend/app/api/v1/routers` registry | manual import/include list in `backend/app/main.py` |
| Service-layer contracts | Canonical non-HTTP namespace selected during audit | `backend/app/api/v1/schemas` imported by services |
| Historical unsubscribe endpoint | `/api/email/unsubscribe` route, classified before action | any endpoint mounted outside `/v1` without allowlist |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to the canonical endpoint
- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated route active
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted. The dev agent must stop or record an explicit user decision with external evidence and deletion risk.

For this story, `/api/email/unsubscribe` starts as presumed `external-active`.
It is a public email link route by audit context assumption. Deletion requires
proof from templates, docs, clients, plus user approval.

## 16. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the removed surface is reintroduced.

The guard must check at least one deterministic source:

- registered router prefixes
- importable Python modules
- generated OpenAPI paths
- forbidden symbols or states
- AST imports in schemas and services

Required forbidden examples:

- `from fastapi` in `backend/app/api/v1/schemas`
- `APIRouter` in `backend/app/api/v1/schemas`
- `from app.api` in `backend/app/services`
- `raise_http_error`
- `legacy_detail`
- endpoints outside `/v1` not listed in `NON_V1_ROUTE_EXCEPTIONS`
- flat router modules under `backend/app/api/v1/routers`, except `__init__.py`
  and the explicitly authorized `registry.py`

## 17. Generated Contract Check

Required generated-contract evidence:

- OpenAPI generation still succeeds after router registry convergence.
- Removed or blocked legacy error fields do not appear in API error response tests unless a user decision preserves them.
- No route path disappears from OpenAPI except a classified `dead` or `historical-facade`
  item with deletion proof and no external blocker.

Snapshot command before and after implementation:

```bash
python -c "from app.main import app; import json; print(json.dumps(sorted(app.openapi()['paths'].keys()), indent=2))"
```

The before/after OpenAPI path outputs must be copied into
`_condamad/stories/api-adapter-boundary-convergence/removal-audit.md` or the final
implementation evidence.

Command shape:

```bash
python -c "from app.main import app; schema = app.openapi(); assert schema['paths']"
```

Run from `backend` after activating `.venv`.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/api/v1/schemas/routers/public/auth.py`
- `backend/app/api/v1/schemas/routers/ops/b2b/reconciliation.py`
- `backend/app/api/v1/schemas/routers/ops/b2b/entitlement_repair.py`
- `backend/app/api/v1/schemas/routers/ops/b2b/entitlements_audit.py`
- `backend/app/api/errors/raising.py`
- `backend/app/api/errors/handlers.py`
- `backend/app/main.py`
- `backend/app/tests/unit/test_api_router_architecture.py`
- `backend/app/tests/unit/test_api_error_contracts.py`
- `backend/app/services/b2b/api_billing.py`
- `backend/app/services/consultation/precheck_service.py`
- `backend/app/services/llm_generation/admin_prompts.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/api/v1/schemas/routers/**/*.py` - remove FastAPI imports/objects and keep Pydantic contracts only.
- `backend/app/services/**/*.py` - replace imports from `app.api` with canonical non-HTTP owners.
- `backend/app/api/v1/routers/registry.py` - explicitly authorized central registry for API v1 routers.
- `backend/app/main.py` - consume the route registry and remove duplicate route list.
- `backend/app/api/errors/raising.py` - remove `raise_http_error` and `legacy_detail` if no external blocker remains.
- `backend/app/api/errors/handlers.py` - remove top-level legacy `detail` injection if no external blocker remains.
- `_condamad/stories/api-adapter-boundary-convergence/removal-audit.md` - implementation audit evidence.

Likely tests:

- `backend/app/tests/unit/test_api_router_architecture.py` - add architecture guards for schemas, services, registry and non-v1 routes.
- `backend/app/tests/unit/test_api_error_contracts.py` - update canonical error contract tests.
- `backend/app/tests/integration/test_api_error_responses.py` - update response-shape expectations if currently checking legacy `detail`.
- Targeted integration tests for any route module whose imports changed.

Files not expected to change:

- `frontend/` - this story is backend API only.
- `backend/pyproject.toml` - no dependency change expected.
- `backend/app/domain/astrology/**` - no astrology behavior change expected.
- `backend/app/infra/db/**` - no database behavior change expected.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped. All Python commands must be executed after activating the venv:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_api_router_architecture.py app/tests/unit/test_api_error_contracts.py
pytest -q app/tests/integration/test_api_error_responses.py
python -c "from app.main import app; schema = app.openapi(); assert schema['paths']"
python -c "from app.main import app; import json; print(json.dumps(sorted(app.openapi()['paths'].keys()), indent=2))"
Test-Path app/api/v1/schemas
rg -n "from app\\.api\\.v1\\.schemas|import app\\.api\\.v1\\.schemas" app/services app/domain app/infra app/core
rg -n "from app\\.api\\.dependencies|from app\\.api\\.errors|import app\\.api" app/services app/domain app/infra app/core
rg -n "raise_http_error|legacy_detail|content\\[\"detail\"\\]" app/api app/tests
```

The `rg` commands are indicative evidence. `Test-Path app/api/v1/schemas` must
return `False` after the follow-up deletion. Deterministic completion requires
AST/file guards in `app/tests/unit/test_api_router_architecture.py` for forbidden
imports, symbols and legacy package reintroduction.

If the full backend suite is feasible, also run:

```powershell
pytest -q
```

If skipped, record exact reason and risk in the final implementation evidence.

## 22. Regression Risks

- Risk: déplacer des DTO hors `app.api.v1.schemas` peut casser des imports nombreux.
  - Guardrail: déplacer par propriétaire canonique, mettre à jour tous les consommateurs par scan, puis lancer les tests ciblés des domaines touchés.
- Risk: supprimer `detail` peut casser un client externe qui dépend encore de l'ancien format d'erreur.
  - Guardrail: bloquer si une preuve externe existe; sinon mettre à jour les tests pour le contrat canonique.
- Risk: centraliser les routeurs peut oublier un routeur existant.
  - Guardrail: comparaison registry/OpenAPI/app.routes dans le test d'architecture.
- Risk: la route `/api/email/unsubscribe` est historique mais probablement externe-active.
  - Guardrail: la story interdit sa suppression sans décision utilisateur explicite.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the project rule: activate `.\.venv\Scripts\Activate.ps1` before any Python, pytest, ruff, pip or script command.
- Keep file-level comments and non-trivial docstrings in French for any new or significantly modified applicative Python file.
- Keep behavior stable unless an item is classified as removable and has no external blocker.

## 24. References

- `backend/app/api/v1/schemas/routers/public/auth.py` - concrete schema module currently importing FastAPI and defining `router`.
- `backend/app/services/b2b/api_billing.py` - representative service currently importing API dependencies.
- `backend/app/main.py` - current manual router import and include registration.
- `backend/app/api/errors/raising.py` - current legacy HTTP error helper.
- `backend/app/api/errors/handlers.py` - current legacy `detail` response compatibility.
- `backend/app/tests/unit/test_api_router_architecture.py` - existing architecture guard location to extend.
- User-provided `AGENTS.md` instructions - Python venv, DRY, No Legacy, tests and lint requirements.

## 25. Completion Update

- The residual tracked file `backend/app/api/v1/schemas/__init__.py` was deleted after confirming that `app.api.v1.schemas` has no active imports.
- Canonical shared contracts remain under `backend/app/services/api_contracts`.
- Regression guardrail `RG-009` now blocks recreating `backend/app/api/v1/schemas` as a facade, wrapper, alias or re-export path.
- Architecture evidence: `test_api_v1_schemas_package_is_removed` fails if the old package returns.
