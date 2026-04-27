# Story centralize-api-http-errors: Centraliser la gestion des erreurs HTTP API

Status: ready-for-dev

## 1. Objective

Centraliser les erreurs HTTP de `backend/app/api` dans un package dédié, typé et réutilisable.
Après migration, les routes ne construisent plus d'erreurs localement et les services ne retournent plus de réponse HTTP.
Les services lèvent des exceptions applicatives typées hors API.
La couche API les convertit en réponses HTTP via des contrats explicites.

## 2. Trigger / Source

- Source type: refactor
- Source reference: brief utilisateur du 2026-04-26 et audit rapide de `backend/app/api` / `backend/app/services`
- Reason for change: `backend/app/api/v1/errors.py` contient une ébauche de fabrique d'erreurs.
  Les routes et certains services construisent encore des erreurs avec `HTTPException`, `_error_response`,
  `_create_error_response`, `api_error_response`, ou des détails libres.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/api`
- In scope:
  - Créer `backend/app/api/errors/` pour les contrats JSON, le catalogue HTTP et les handlers FastAPI.
  - Créer ou utiliser `backend/app/core/exceptions.py` pour la classe mère `ApplicationError`.
  - Modéliser les constantes HTTP exposées par domaine ou route avec statut et texte associé.
  - Remplacer les constructions locales d'erreurs HTTP dans `backend/app/api`.
  - Auditer `backend/app/services` et transformer les fonctions qui construisent ou retournent encore des erreurs HTTP en fonctions qui lèvent des exceptions applicatives.
  - Déporter la conversion exception applicative -> réponse HTTP dans `backend/app/api`.
- Out of scope:
  - Modifier les règles métier des domaines `billing`, `b2b`, `llm_generation`, `ops`, `privacy`, `geocoding`, `reference_data`, `user_profile`, `chart`, ou `auth`.
  - Changer les routes, chemins, schémas de succès, authentification, autorisations ou persistance.
  - Modifier le frontend.
  - Introduire un nouveau framework d'erreurs externe.
- Explicit non-goals:
  - Ne pas créer plusieurs formats concurrents d'erreur.
  - Ne pas conserver `backend/app/api/v1/errors.py` comme façade de compatibilité si le package dédié devient propriétaire canonique.
  - Ne pas placer la classe mère des exceptions applicatives dans `backend/app/api/errors/`.
  - Ne pas masquer les erreurs services par des `Exception` génériques sans code applicatif stable.
  - Ne pas remplacer l'audit par une correction opportuniste de quelques fichiers seulement.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: service-boundary-refactor
- Archetype reason: la responsabilité HTTP doit converger vers l'API.
  Les services doivent exposer uniquement des exceptions applicatives typées hors API.
- Behavior change allowed: yes
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: une route expose un contrat public d'erreur incompatible avec l'enveloppe centralisée,
  sans test ou contrat existant permettant de trancher sans risque.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/api/v1/errors.py` - module unique avec `ApiV1HttpError`,
  classes HTTP spécialisées et `api_error_response`, mais sans package dédié.
- Evidence 2: `backend/app/api/v1/routers/admin/users.py` - plusieurs `raise HTTPException`
  construisent encore les statuts et messages localement.
- Evidence 3: `backend/app/api/v1/routers/admin/llm/releases.py` - mélange `HTTPException`, `ValueError` converties localement et dictionnaires d'erreurs.
- Evidence 4: `backend/app/api/v1/routers/admin/llm/assemblies.py` - importe `HTTPException` et construit encore des erreurs locales malgré l'existence de `_error_response`.
- Evidence 5: `backend/app/api/v1/routers/public/email.py` et `backend/app/api/v1/routers/public/predictions.py` - construisent encore des `HTTPException` avec textes locaux.
- Evidence 6: plusieurs services importent `app.api.v1.errors` ou retournent `api_error_response`,
  notamment `auth/public_support.py`, `billing/public_billing.py`, `geocoding/public_support.py`,
  `llm_generation/admin_prompts.py`, `llm_generation/internal_qa.py` et `ops/admin_content.py`.
- Evidence 7: `backend/app/api/dependencies/auth.py` et `backend/app/api/dependencies/b2b_auth.py`
  définissent déjà des exceptions API locales avec `status_code`, `code`, `message`, `details`.

## 6. Target State

After implementation:

- `backend/app/core/exceptions.py` possède `ApplicationError` sans dépendance FastAPI.
- `backend/app/api/errors/contracts.py` possède `ApiErrorBody` et `ApiErrorEnvelope`.
- `backend/app/api/errors/catalog.py` possède les constantes HTTP exposées, typées et validées.
- `backend/app/api/errors/handlers.py` convertit `ApplicationError` en réponse FastAPI.
- `backend/app/api/errors/raising.py` ou `responses.py` porte les helpers centralisés côté API si nécessaires.
- L'enveloppe JSON d'erreur est exactement `{"error": {"code": str, "message": str, "details": object, "request_id": str | null}}`.
- Les routes lèvent des exceptions applicatives ou utilisent une factory centralisée.
  Elles ne construisent jamais elles-mêmes l'enveloppe JSON.
- Les services de `backend/app/services` ne dépendent plus de `app.api`, `JSONResponse` ou `HTTPException`.
  Ils lèvent des exceptions applicatives quand une erreur doit remonter vers l'API.
- Tout `ApplicationError` non explicitement mappé produit une erreur contrôlée avec code stable,
  statut HTTP défini et sans fuite de stacktrace.
- Des tests et gardes d'architecture empêchent la réintroduction de constructions locales d'erreurs HTTP.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `ApplicationError` vit hors API, dans `backend/app/core/exceptions.py`. | `pytest -q backend/tests/unit/test_api_error_contracts.py` + scan erreurs dans services. |
| AC2 | Le catalogue HTTP typé a codes uniques, statuts valides et messages non vides. | `pytest -q backend/tests/unit/test_api_error_contracts.py` teste le registre. |
| AC3 | Les routes ne lèvent plus `HTTPException` métier/applicative. | `pytest -q backend/tests/unit/test_api_error_architecture.py` avec allowlist stricte. |
| AC4 | Les helpers locaux d'erreur disparaissent des routeurs. | `pytest -q backend/tests/unit/test_api_error_architecture.py` + scan `def _error_response`. |
| AC5 | Les services ne construisent plus de réponse HTTP. | `pytest -q backend/tests/unit/test_api_error_architecture.py` + scan `app.api`/`JSONResponse`. |
| AC6 | Toutes les sous-classes d'`ApplicationError` auditées ont mapping ou fallback testé. | `pytest -q backend/tests/unit/test_api_error_contracts.py` + `error-audit.md`. |
| AC7 | Le JSON d'erreur conserve l'enveloppe `error.code/message/details/request_id`. | `pytest -q backend/tests/integration/test_api_error_responses.py`. |
| AC8 | OpenAPI ne perd aucun path/method et ne duplique pas les schémas d'erreur. | `pytest -q backend/tests/integration/test_api_error_responses.py`. |
| AC9 | Tests, lint et scans d'architecture passent dans le venv Python activé. | `.\\.venv\\Scripts\\Activate.ps1`, `ruff format .`, `ruff check .`, `pytest -q`, scans `rg`. |

## 8. Implementation Tasks

- [ ] Task 1 - Auditer les surfaces d'erreur API et services (AC: AC1, AC3, AC4, AC5, AC6)
  - [ ] Subtask 1.1 - Produire `_condamad/stories/centralize-api-http-errors/error-audit.md` avec les fichiers trouvés, le type de construction locale et la décision de migration.
  - [ ] Subtask 1.2 - Classer séparément les usages dans `backend/app/api`, `backend/app/api/dependencies` et `backend/app/services`.
  - [ ] Subtask 1.3 - Identifier les exceptions services déjà existantes qui doivent être mappées plutôt que remplacées.

- [ ] Task 2 - Créer les bases canoniques d'erreurs (AC: AC1, AC2, AC7)
  - [ ] Subtask 2.1 - Créer `backend/app/core/exceptions.py` avec `ApplicationError` sans FastAPI.
  - [ ] Subtask 2.2 - Créer `backend/app/api/errors/` avec contrats JSON, catalogue HTTP et handlers.
  - [ ] Subtask 2.3 - Supprimer `backend/app/api/v1/errors.py` par migration atomique des imports.
  - [ ] Subtask 2.4 - Ajouter les constantes HTTP exposées nécessaires aux usages audités.

- [ ] Task 3 - Migrer les routes et dépendances API vers le gestionnaire centralisé (AC: AC2, AC3, AC4, AC7, AC8)
  - [ ] Subtask 3.1 - Remplacer les `HTTPException` métier et helpers locaux par des appels au gestionnaire centralisé.
  - [ ] Subtask 3.2 - Préférer un handler FastAPI global à des conversions dispersées dans les routes.
  - [ ] Subtask 3.3 - Garder les status codes existants sauf décision documentée dans l'audit.
  - [ ] Subtask 3.4 - Documenter toute conservation de `HTTPException` framework dans l'allowlist de test.

- [ ] Task 4 - Découpler `backend/app/services` de HTTP/FastAPI (AC: AC1, AC5, AC6)
  - [ ] Subtask 4.1 - Remplacer les imports `app.api.v1.errors` par `app.core.exceptions`.
  - [ ] Subtask 4.2 - Transformer les fonctions services qui retournent une réponse HTTP en fonctions qui retournent une valeur métier ou lèvent une exception applicative.
  - [ ] Subtask 4.3 - Mapper ces exceptions dans `backend/app/api` au plus près des routeurs ou via un handler centralisé.

- [ ] Task 5 - Ajouter les tests et gardes d'architecture (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9)
  - [ ] Subtask 5.1 - Ajouter les tests unitaires du package d'erreurs.
  - [ ] Subtask 5.2 - Ajouter ou compléter des tests API pour les routes migrées.
  - [ ] Subtask 5.3 - Ajouter un test d'architecture qui échoue sur les imports et symboles interdits.

- [ ] Task 6 - Valider localement (AC: AC9)
  - [ ] Subtask 6.1 - Activer le venv avant toute commande Python.
  - [ ] Subtask 6.2 - Exécuter lint, tests et scans négatifs.
  - [ ] Subtask 6.3 - Mettre à jour l'audit si une exception/route supplémentaire est découverte pendant l'implémentation.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/api/v1/errors.py` comme source d'intention existante pour l'enveloppe JSON.
    Il ne doit pas rester module canonique final si le package dédié le remplace.
  - Les exceptions services existantes quand elles portent déjà `code`, `message`, `details`.
    Exemples : `AuthServiceError`, `PricingExperimentServiceError`, `GeocodingServiceError`.
  - `fastapi.encoders.jsonable_encoder` pour la sérialisation si nécessaire.
- Do not recreate:
  - Des helpers `_error_response` par route ou par service.
  - Des `Enum` de codes dupliqués entre schémas, routeurs et services.
  - Des décisions métier dans le catalogue HTTP.
  - Des dictionnaires libres utilisés comme contrat d'erreur principal.
- Shared abstraction allowed only if:
  - Elle remplace au moins deux responsabilités dupliquées observées dans l'audit.
  - Elle reste dans `backend/app/api/errors/` pour HTTP ou `backend/app/core/exceptions.py` pour l'applicatif.
  - Elle est couverte par un test de contrat.

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

- `from app.api.v1.errors import api_error_response`
- `app.api.v1.errors`
- `def _error_response`
- `def _create_error_response`
- `HTTPException(` pour erreurs métier dans `backend/app/api`, sauf allowlist testée
- `JSONResponse` dans `backend/app/services`
- `api_error_response(` dans `backend/app/services`
- `ApplicationError` défini sous `backend/app/api`
- nouveaux `dict[str, Any]` utilisés comme contrat principal d'erreur sans modèle typé

## 11. Removal Classification Rules

- Removal classification: internal-legacy-surface-removal

Classification must be deterministic:

- `canonical-active`: surface encore propriétaire canonique, à conserver.
- `historical-facade`: ancien import ou helper remplacé par une surface canonique.
- `dead`: surface sans consommateur après migration atomique.
- `needs-user-decision`: ambiguïté restante après scans obligatoires.

`backend/app/api/v1/errors.py` et `app.api.v1.errors` doivent être classés avant suppression.
Une surface `historical-facade` ou `dead` doit être supprimée, pas réexportée.

## 12. Removal Audit Format

Required audit table in `_condamad/stories/centralize-api-http-errors/error-audit.md`:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Minimum items to audit:

- `backend/app/api/v1/errors.py`
- `app.api.v1.errors`
- `api_error_response`
- route-local `_error_response`
- route-local `_create_error_response`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Exceptions applicatives | `backend/app/core/exceptions.py` | Exceptions API locales sans base commune |
| Contrats JSON d'erreur API | `backend/app/api/errors/contracts.py` | Dictionnaires libres dans routeurs |
| Catalogue HTTP exposé | `backend/app/api/errors/catalog.py` | Triplets locaux statut/code/message |
| Mapping exception -> réponse HTTP | `backend/app/api/errors/handlers.py` | `HTTPException`, `api_error_response`, tuples locaux |
| Helpers de levée côté API | `backend/app/api/errors/raising.py` ou `responses.py` | `_error_response`, `_create_error_response` |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- preserving `backend/app/api/v1/errors.py` as a re-export
- adding a compatibility alias for `api_error_response`
- keeping route-local wrappers after migration
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

If `app.api.v1.errors` is referenced outside first-party backend code, stop and record the evidence.
Do not delete an external-active surface without explicit user decision.

## 16. Reintroduction Guard

The implementation must add or update an architecture guard that fails if these surfaces return:

- `backend/app/api/v1/errors.py`
- `from app.api.v1.errors import`
- `api_error_response(`
- route-local `_error_response`
- route-local `_create_error_response`
- `ApplicationError` under `backend/app/api`

## 17. Generated Contract Check

- Generated contract check: applicable
- Reason: les réponses d'erreur font partie du comportement API FastAPI exposé par OpenAPI.
- Required generated-contract evidence:
  - Vérifier que les paths et méthodes OpenAPI existants restent présents.
  - Vérifier que les statuts d'erreur ciblés correspondent aux statuts attendus.
  - Vérifier qu'un modèle d'erreur explicite n'est pas dupliqué si ajouté.
  - Vérifier que `backend/app/api/v1/errors.py` n'est pas exposé par un import résiduel.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/api/v1/errors.py`
- `backend/app/core/exceptions.py`
- `backend/app/api/dependencies/auth.py`
- `backend/app/api/dependencies/b2b_auth.py`
- `backend/app/api/v1/routers/admin/users.py`
- `backend/app/api/v1/routers/admin/llm/releases.py`
- `backend/app/api/v1/routers/admin/llm/assemblies.py`
- `backend/app/api/v1/routers/admin/llm/prompts.py`
- `backend/app/api/v1/routers/public/email.py`
- `backend/app/api/v1/routers/public/predictions.py`
- `backend/app/services/auth/public_support.py`
- `backend/app/services/billing/public_billing.py`
- `backend/app/services/chart/public_astrology_engine.py`
- `backend/app/services/geocoding/public_support.py`
- `backend/app/services/llm_generation/admin_prompts.py`
- `backend/app/services/llm_generation/internal_qa.py`
- `backend/app/services/ops/admin_content.py`
- `backend/tests/conftest.py`
- `backend/tests/integration/app_db.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/core/exceptions.py` - base `ApplicationError` sans dépendance FastAPI.
- `backend/app/api/errors/__init__.py` - exports canoniques du package d'erreurs.
- `backend/app/api/errors/contracts.py` - modèles `ApiErrorBody` et `ApiErrorEnvelope`.
- `backend/app/api/errors/catalog.py` - constantes HTTP exposées par domaine/route.
- `backend/app/api/errors/handlers.py` - conversion exception/constante vers réponse HTTP FastAPI.
- `backend/app/api/errors/raising.py` - helpers centralisés côté API si des routes doivent lever un catalogue.
- `backend/app/api/v1/errors.py` - suppression après migration atomique, sans façade legacy.
- `backend/app/api/dependencies/auth.py` - migration vers la classe mère centralisée.
- `backend/app/api/dependencies/b2b_auth.py` - migration vers la classe mère centralisée.
- `backend/app/api/v1/routers/**/*.py` - remplacement des constructions locales d'erreurs dans les routeurs audités.
- `backend/app/services/**/*.py` - uniquement les services audités qui importent `app.api` ou retournent une réponse HTTP.
- `_condamad/stories/centralize-api-http-errors/error-audit.md` - audit d'exécution de la migration.

Likely tests:

- `backend/tests/unit/test_api_error_contracts.py` - contrat du package d'erreurs.
- `backend/tests/unit/test_api_error_architecture.py` - gardes contre imports/symboles interdits.
- `backend/tests/integration/test_api_error_responses.py` - réponses API représentatives.
- Tests existants des routeurs migrés, à mettre à jour sans élargir leur périmètre.

Files not expected to change:

- `frontend/src/**` - aucun changement frontend demandé.
- `backend/pyproject.toml` - aucune nouvelle dépendance prévue.
- `requirements.txt` - ne doit pas être créé.
- `backend/app/domain/**` - pas de changement de règles métier demandé.
- `backend/app/infra/**` - pas de changement infra demandé.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

```powershell
.\.venv\Scripts\Activate.ps1
rg -n "from app\.api\.v1\.errors|app\.api\.v1\.errors" backend/app backend/tests
rg -n "def _error_response|def _create_error_response|api_error_response\(" backend/app/api/v1/routers backend/app/api/dependencies backend/app/services
rg -n "app\.api\.|JSONResponse|HTTPException|api_error_response|_error_response\(" backend/app/services
rg -n "HTTPException\(" backend/app/api
rg -n "class ApplicationError|ApplicationError" backend/app/api
Test-Path backend/app/api/v1/errors.py
```

Expected scan result: no nominal usage remains, except `HTTPException` usages allowlisted by test.
`Test-Path backend/app/api/v1/errors.py` must return `False` after migration.
Any `HTTPException` allowlist must live in `backend/tests/unit/test_api_error_architecture.py`.

## 22. Regression Risks

- Risk: changement involontaire du format JSON d'erreur consommé par le frontend ou des clients externes.
  - Guardrail: tests API ciblés vérifiant `error.code`, `error.message`, `error.details`, `error.request_id`.
- Risk: services encore couplés à FastAPI après migration partielle.
  - Guardrail: scan négatif sur `backend/app/services` et test d'architecture.
- Risk: conversion incomplète des exceptions services existantes.
  - Guardrail: audit `error-audit.md` avec table fichier/fonction/exception/mapping.
- Risk: prolifération de constantes d'erreur dupliquées.
  - Guardrail: catalogue typé unique par domaine/route et tests du registre.
- Risk: le catalogue HTTP devient un fourre-tout métier.
  - Guardrail: `ApplicationError` porte le code applicatif ; l'API porte seulement la traduction HTTP.
- Risk: les routes admin LLM, très volumineuses, gardent des helpers locaux par oubli.
  - Guardrail: scans négatifs ciblés sur `backend/app/api/v1/routers/admin/llm`.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: activate `.\\.venv\\Scripts\\Activate.ps1` before every Python command.
- Keep comments and public/non-trivial docstrings in French for every new or significantly modified Python file.
- Do not create `requirements.txt`.
- Do not add a new base folder under `backend/`; `backend/app/api/errors/` is inside the existing API package and is allowed by this story.
- Do not place `ApplicationError` in `backend/app/api/errors/`.
- Migrate `backend/app/api/v1/errors.py` atomically; no committed state may keep `app.api.v1.errors` imports.
- Preserve `HTTPException` only for framework-only cases listed in the architecture test allowlist.
- Prefer small, mechanical migrations backed by scans over broad stylistic edits.

## 24. References

- `backend/app/api/v1/errors.py` - ébauche actuelle de gestion centralisée.
- `backend/app/core/exceptions.py` - cible prévue pour la base applicative sans FastAPI.
- `backend/app/api/dependencies/auth.py` - exception API locale à converger.
- `backend/app/api/dependencies/b2b_auth.py` - exception API locale à converger.
- `backend/app/api/v1/routers/admin/users.py` - exemples de `HTTPException` métier locales.
- `backend/app/api/v1/routers/admin/llm/releases.py` - exemples de `HTTPException`, `ValueError` et dictionnaires d'erreur locaux.
- `backend/app/api/v1/routers/admin/llm/assemblies.py` - mélange `HTTPException` et helper d'erreur.
- `backend/app/services/billing/public_billing.py` - exemple de service retournant `api_error_response`.
- `backend/app/services/llm_generation/admin_prompts.py` - exemple de service couplé à `app.api.v1.errors`.
- `backend/tests/conftest.py` - contraintes de test backend et migration SQLite mentionnées par les instructions projet.
- User brief 2026-04-26 - demande de package dédié, classes mères, constantes typées et audit services.
