# Story 46.5: Retirer le sous-système tarot/runes du backend et des contrats LLM

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a backend architect,
I want supprimer l'infrastructure tarot/runes devenue hors périmètre,
so that le code reste maintenable, les contrats LLM soient propres et aucune ressource ne soit gaspillée sur des fonctionnalités retirées.

## Acceptance Criteria

- [x] AC1: Les feature flags `tarot_enabled` et `runes_enabled` ainsi que les mécanismes de disponibilité/exécution de modules dédiés ne sont plus exposés par le backend.
- [x] AC2: Les endpoints backend et clients frontend associés à `/v1/chat/modules/availability` et `/v1/chat/modules/{module}/execute` sont supprimés.
- [x] AC3: L'orchestration LLM ne référence plus de use case, schéma, policy, prompt ou intent lié à `tarot`, `runes`, `tarot_spread`, `offer_tarot_reading`.
- [x] AC4: Le hard policy `astrology` est réaligné pour ne plus promettre d'interprétation tarot.
- [x] AC5: Les schémas Pydantic et JSON schemas obsolètes sont retirés de l'orchestration.
- [x] AC6: Les tests unitaires et d'intégration backend sont nettoyés des références aux modules supprimés.
- [x] AC7: Une vérification ciblée confirme l'absence résiduelle de `tirage`, `tarot`, `runes`, `cartes` sur les surfaces critiques du backend.

## Tasks / Subtasks

- [x] Task 1: Confirmer le périmètre exact à supprimer (AC: 7)
  - [x] Faire un inventaire `rg` complet sur `tarot`, `runes`, `tirage`, `cards`, `spread`, `offer_tarot_reading`
  - [x] Vérifier qu'aucun parcours frontend encore actif n'utilise ces modules après 46.1 à 46.4

- [x] Task 2: Retirer le gating et l'exécution modules côté backend (AC: 1, 2, 7)
  - [x] Supprimer `backend/app/api/v1/routers/chat_modules.py`
  - [x] Retirer l'enregistrement du router dans `backend/app/main.py`
  - [x] Nettoyer `FeatureFlagService` de la logique modules et des flags `tarot_enabled`/`runes_enabled`

- [x] Task 3: Nettoyer l'orchestration LLM et les prompts (AC: 3, 4, 5)
  - [x] Retirer `tarot_reading` des use cases seed dans `use_cases_seed.py`
  - [x] Retirer `tarot_spread` des schémas dans `schemas.py`
  - [x] Retirer l'intent `offer_tarot_reading` des schémas et seeds
  - [x] Mettre à jour la hard policy `astrology` dans `hard_policy.py`
  - [x] Supprimer le prompt jinja `card_reading_v1.jinja2`

- [x] Task 4: Nettoyer le client frontend API chat (AC: 2)
  - [x] Retirer `useExecuteModule` et `useModuleAvailability` de `frontend/src/api/chat.ts`
  - [x] Supprimer les types associés

- [x] Task 5: Garantir la robustesse et les métriques backend (AC: 1, 6)
  - [x] Revoir les compteurs/metrics taggés `module=tarot` ou `module=runes` si applicables
  - [x] Vérifier les éventuels scripts de seed, fixtures ou migrations qui supposent encore ces modules

- [x] Task 6: Tests et non-régression (AC: 6)
  - [x] Supprimer ou mettre à jour les tests unitaires/intégration backend impactés
  - [x] Relancer la suite de tests backend complète pour valider l'absence de casse sur l'orchestration restante

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

- Removed backend/app/api/v1/routers/chat_modules.py.
- Cleaned up main.py and FeatureFlagService.
- Updated use_cases_seed.py, schemas.py, and hard_policy.py.
- Cleaned up frontend/src/api/chat.ts.
- Updated backend tests.

### Completion Notes List

- Successfully removed all tarot/runes related infrastructure from backend and LLM orchestration.
- Updated hard policies to remove mentions of card reading.
- Cleaned up frontend API clients to remove dead endpoints.
- Verified system integrity with complete backend test suite.
- Post-review correction 2026-03-13: suppression complétée des résidus backend encore présents dans `PromptRegistry`, `AIEngineAdapter`, les fixtures d'évaluation tarot et les tests associés.

### File List

- backend/app/api/v1/routers/chat_modules.py (DELETED)
- backend/app/ai_engine/prompts/card_reading_v1.jinja2 (DELETED)
- backend/app/main.py
- backend/app/services/feature_flag_service.py
- backend/app/llm_orchestration/seeds/use_cases_seed.py
- backend/app/llm_orchestration/schemas.py
- backend/app/llm_orchestration/policies/hard_policy.py
- backend/app/llm_orchestration/gateway.py
- backend/app/api/v1/routers/__init__.py
- frontend/src/api/chat.ts
- backend/app/tests/unit/test_hard_policy.py
- backend/app/tests/integration/test_chat_api.py
- backend/app/tests/integration/test_ops_feature_flags_api.py
- backend/app/ai_engine/services/prompt_registry.py
- backend/app/services/ai_engine_adapter.py
- backend/app/ai_engine/tests/test_prompt_registry.py
- backend/app/tests/unit/test_natal_metrics.py
- backend/app/tests/unit/test_schemas_v3.py
