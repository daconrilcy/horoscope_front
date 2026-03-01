# Story 28.2: Prompt Registry v2 — versioning DB, admin CRUD, lint, rollback

Status: done

## Story

As a product admin,
I want gérer les prompts use_case via une interface d'administration avec versioning, lint et rollback,
so that je peux modifier le comportement du LLM sans déploiement, avec traçabilité complète et sécurité de rollback.

## Acceptance Criteria

1. [x] **Given** un admin authentifié **When** il crée un nouveau prompt pour un use_case **Then** il est enregistré en état `draft` avec un `version_id` unique, un `created_at`, et l'identifiant de l'auteur.
2. [x] **Given** un prompt en état `draft` **When** l'admin le publie **Then** l'ancien prompt `published` passe à `archived` et le nouveau devient `published` (un seul `published` actif par use_case à tout moment).
3. [x] **Given** un prompt `published` **When** il est utilisé par le gateway **Then** `GatewayResult.meta.prompt_version_id` correspond à son `version_id`.
4. [x] **Given** un admin **When** il sauvegarde un prompt **Then** un lint de validation est exécuté : taille max (8 000 caractères), placeholders obligatoires présents (`{{locale}}`, `{{use_case}}`), absence de mots interdits (`ignore all`, `disregard previous`) — le lint bloque la sauvegarde si échec.
5. [x] **Given** un prompt `published` défectueux **When** un admin déclenche un rollback **Then** le dernier prompt `archived` de ce use_case repasse à `published` et le prompt défectueux passe à `archived`.
6. [x] **Given** le LLM Gateway **When** il résout la config d'un use_case **Then** il charge le prompt `published` actif depuis la DB (avec cache TTL 60s pour éviter les requêtes DB à chaque appel).
7. [x] **Given** aucun prompt `published` pour un use_case **When** le gateway tente de l'utiliser **Then** il fallback sur le stub hardcodé de Story 28.1 avec un warning logué.

## Tasks / Subtasks

- [x] Task 1 (AC: 1, 2, 5)
  - [x] Créer le modèle SQLAlchemy `LlmPromptVersion` : `id`, `use_case_key`, `status` (draft/published/archived), `developer_prompt` (text), `model`, `temperature`, `max_output_tokens`, `fallback_use_case_key`, `created_by`, `created_at`, `published_at`.
  - [x] Migration Alembic correspondante.
  - [x] Créer le modèle `LlmUseCaseConfig` : `key` (PK), `display_name`, `description`, `output_schema_id` (nullable, utilisé en Story 28.4), `allowed_persona_ids` (JSON list).

- [x] Task 2 (AC: 1, 2, 5)
  - [x] Créer `backend/app/llm_orchestration/services/prompt_registry_v2.py` : `get_active_prompt(use_case_key)`, `publish_prompt(version_id)`, `rollback_prompt(use_case_key)`.
  - [x] Garantie d'unicité `published` : contrainte en DB (index unique partiel).

- [x] Task 3 (AC: 4)
  - [x] Créer `backend/app/llm_orchestration/services/prompt_lint.py` : `lint_prompt(text) -> LintResult`.
  - [x] Règles : taille max 8 000 chars, placeholders `{{locale}}` et `{{use_case}}` présents, liste de mots interdits configurables.
  - [x] `LintResult` : `passed: bool`, `errors: list[str]`, `warnings: list[str]`.

- [x] Task 4 (AC: 1, 2, 4, 5)
  - [x] Créer les endpoints admin (RBAC `admin` requis) :
    - [x] `GET /v1/admin/llm/use-cases` — liste des use_cases et statut du prompt actif.
    - [x] `GET /v1/admin/llm/use-cases/{key}/prompts` — historique des versions.
    - [x] `POST /v1/admin/llm/use-cases/{key}/prompts` — créer un draft (lint à la sauvegarde).
    - [x] `PATCH /v1/admin/llm/use-cases/{key}/prompts/{version_id}/publish` — publier.
    - [x] `POST /v1/admin/llm/use-cases/{key}/rollback` — rollback vers la version archivée précédente.

- [x] Task 5 (AC: 6, 7)
  - [x] Intégrer `prompt_registry_v2.get_active_prompt()` dans `LLMGateway.execute()` (Story 28.1).
  - [x] Cache TTL 60s (in-process avec invalidation à la publication).
  - [x] Fallback sur stub hardcodé si aucun prompt `published` + warning structuré.

- [x] Task 6 (AC: 1-7)
  - [x] Migration des use_cases existants (chat, natal_chart_interpretation, guidance_daily) vers des enregistrements `LlmUseCaseConfig` avec un premier prompt `published` (via `seed_registry.py`).
  - [x] Tests unitaires : lint (cas pass/fail), publish/archive/rollback, unicité published, cache TTL.
  - [x] Tests d'intégration : endpoint admin CRUD complet.

## Dev Notes

### Context

Le Prompt Registry actuel (Story 15) est basé sur des fichiers Jinja2 statiques dans `backend/app/ai_engine/prompts/`. Cette story remplace ce mécanisme par une DB avec lifecycle draft/published/archived, un CRUD admin, et un lint de sécurité.

### Modèle de données

```
LlmUseCaseConfig
  key: str (PK)              # ex: "natal_interpretation"
  display_name: str
  description: str
  output_schema_id: str|null # FK vers LlmOutputSchema (Story 28.4)
  allowed_persona_ids: list  # JSON, vide = tous autorisés

LlmPromptVersion
  id: uuid (PK)
  use_case_key: str (FK)
  status: enum (draft|published|archived)
  developer_prompt: text     # Template du developer message
  model: str                 # ex: "gpt-4.1"
  temperature: float
  max_output_tokens: int
  fallback_use_case_key: str|null
  created_by: str            # user_id de l'admin
  created_at: datetime
  published_at: datetime|null
```

### Règles lint (v1)

| Règle | Sévérité |
|---|---|
| Taille > 8 000 caractères | Erreur (bloquante) |
| `{{locale}}` absent | Erreur (bloquante) |
| `{{use_case}}` absent | Erreur (bloquante) |
| `ignore all` ou `disregard previous` | Erreur (bloquante) |
| Taille > 4 000 caractères | Warning (non bloquant) |

### Scope

- Modèles DB + migrations Alembic.
- Service `prompt_registry_v2` + `prompt_lint`.
- Endpoints admin CRUD.
- Intégration dans `LLMGateway` (cache + fallback).
- Migration initiale des prompts existants.

### Out of Scope

- Interface graphique admin (les endpoints REST suffisent pour cette story).
- Schémas de sortie JSON (Story 28.4).
- Personas (Story 28.3).

### Technical Notes

- Contrainte DB : index unique partiel `(use_case_key, status='published')` pour garantir l'unicité du prompt actif.
- Cache : utiliser `CacheService` existant avec clé `prompt_v2:{use_case_key}`, TTL 60s. Invalider le cache à chaque publication/rollback.
- Les templates Jinja2 actuels doivent être traduits : remplacer `{{ variable }}` par `{{variable}}` (placeholder simplifié sans espace pour le lint).

### Tests

- `test_prompt_lint.py` : toutes les règles lint (pass/fail par règle).
- `test_prompt_registry_v2.py` : lifecycle draft→published→archived, unicité, rollback, fallback stub.
- `test_admin_prompt_endpoints.py` : CRUD complet, lint bloquant à la sauvegarde, RBAC (non-admin → 403).
- `test_gateway_prompt_resolution.py` : résolution depuis DB, cache hit/miss, fallback stub.

### Rollout / Feature Flag

- Dépend du flag `LLM_ORCHESTRATION_V2` de Story 28.1.
- Migration initiale peut être exécutée indépendamment (les données DB n'affectent rien tant que le flag est off).

### Observability

- Audit log : chaque action admin (create draft, publish, rollback) loguée avec `user_id`, `use_case_key`, `version_id`, `action`, `timestamp`.
- Métriques : `prompt_registry_cache_hits_total`, `prompt_registry_db_reads_total`, `prompt_lint_failures_total{use_case}`.

### Dependencies

- 28.1 (LLM Gateway) : intégration dans `execute()`.
- Modèle `User` + RBAC `admin` existants.
- `CacheService` (Story 15).

### Project Structure Notes

- Nouveaux fichiers : `backend/app/llm_orchestration/services/prompt_registry_v2.py`, `prompt_lint.py`.
- Modèles DB : `backend/app/models/llm_prompt.py`.
- Migration : `backend/alembic/versions/`.
- Endpoints : `backend/app/api/v1/routers/admin_llm.py`.
- Story artifact : `_bmad-output/implementation-artifacts/`.
- Planning source : `_bmad-output/planning-artifacts/epic-28-llm-orchestration-layer.md`.

### References

- [Source: _bmad-output/planning-artifacts/epic-28-llm-orchestration-layer.md]
- [Source: backend/app/ai_engine/services/prompt_registry.py]
- [Source: backend/app/ai_engine/services/cache_service.py]

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

- Fixed migration issues by stamping DB to 20260226_0027.
- Added `admin` to `VALID_ROLES` in `rbac.py` to match story requirements.
- Updated `admin_llm.py` to return `JSONResponse` for error consistency.

### Implementation Plan

1.  Created DB models `LlmUseCaseConfigModel` and `LlmPromptVersionModel`.
2.  Generated and applied migration.
3.  Implemented `PromptRegistryV2` with 60s TTL cache.
4.  Implemented `PromptLint` for security and placeholder validation.
5.  Integrated registry into `LLMGateway.execute`.
6.  Updated `AIEngineAdapter` and callers (`ChatGuidanceService`, `GuidanceService`) to pass `db` session.
7.  Created Admin REST API with RBAC `admin`.
8.  Seeded initial templates from Jinja2 to DB format.

### Completion Notes List

- All unit and integration tests passed (27 tests total in `llm_orchestration`).
- `admin` role is now required for LLM prompt management.
- Cache is automatically invalidated upon publication or rollback.

### File List

- `backend/app/infra/db/models/llm_prompt.py`
- `backend/migrations/versions/0be022f23e03_create_llm_prompt_registry_tables.py`
- `backend/app/llm_orchestration/services/prompt_registry_v2.py`
- `backend/app/llm_orchestration/services/prompt_lint.py`
- `backend/app/llm_orchestration/admin_models.py`
- `backend/app/api/v1/routers/admin_llm.py`
- `backend/app/llm_orchestration/seed_registry.py`
- `backend/app/core/rbac.py`
- `backend/app/main.py` (router registration)
- `backend/app/llm_orchestration/gateway.py` (integration)
- `backend/app/services/ai_engine_adapter.py` (integration)
- `backend/app/services/chat_guidance_service.py` (caller update)
- `backend/app/services/guidance_service.py` (caller update)
- `backend/app/llm_orchestration/tests/test_prompt_lint.py`
- `backend/app/llm_orchestration/tests/test_prompt_registry_v2.py`
- `backend/app/llm_orchestration/tests/test_admin_llm_api.py`

## Change Log

- 2026-03-01: Story créée (Epic 28, LLM Orchestration Layer).
