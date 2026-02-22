# Story 15.3: Migration des services Chat et Guidance vers le AI Engine

Status: done

## Story

As a utilisateur du chat et des guidances astrologiques,
I want que mes conversations et guidances soient générées par le vrai moteur OpenAI,
So that je reçoive des réponses astrologiques de qualité au lieu de simples échos de prompt.

## Contexte et Objectifs

Cette story finalise l'intégration du **AI Text Engine** (stories 15.1 + 15.2) dans l'application. Actuellement :

**Problème identifié :**
Les services `ChatGuidanceService` et `GuidanceService` utilisent encore l'ancien **LLMClient stub** (`app/infra/llm/client.py`) qui ne fait qu'un echo du prompt sans appeler OpenAI. Le nouveau module `ai_engine` avec le vrai client OpenAI n'est pas encore intégré aux services métier.

**Objectif :**
Migrer tous les services utilisant le LLM vers le nouveau AI Engine pour bénéficier de :
- Vrais appels OpenAI au lieu d'échos
- Rate limiting, cache, logs structurés (15.2)
- Prompts centralisés et versionnés (Prompt Registry)
- Gestion robuste des erreurs et retries

**Pré-requis :**
- Story 15.1 (AI Engine + OpenAI gateway) ✅
- Story 15.2 (Rate limiting, observabilité, Docker) ✅

## Acceptance Criteria

### AC1: Migration de ChatGuidanceService
**Given** le service `ChatGuidanceService` existant
**When** un utilisateur envoie un message dans le chat
**Then** le service utilise le nouveau AI Engine (appel direct au module `chat_service`)
**And** la réponse est générée par OpenAI avec le template `chat_system.jinja2`
**And** le contexte de conversation est passé via le format du AI Engine
**And** les métriques et logs passent par le AI Engine

### AC2: Migration de GuidanceService
**Given** le service `GuidanceService` existant
**When** un utilisateur demande une guidance (daily/weekly/contextual)
**Then** le service utilise le nouveau AI Engine avec les use_cases appropriés
**And** les templates de prompts `guidance_daily`, `guidance_weekly`, `guidance_contextual` sont utilisés
**And** les garde-fous hors-scope existants sont préservés

### AC3: Nouveaux use_cases dans le Prompt Registry
**Given** le Prompt Registry existant
**When** les nouveaux use_cases sont ajoutés
**Then** les templates `guidance_daily_v1.jinja2`, `guidance_weekly_v1.jinja2`, `guidance_contextual_v1.jinja2` sont disponibles
**And** chaque template inclut les instructions persona, les données de naissance, et le contexte de conversation
**And** les defaults (model, max_tokens, temperature) sont configurés pour chaque use_case

### AC4: Suppression de l'ancien LLMClient stub
**Given** l'ancien `LLMClient` stub dans `infra/llm/client.py`
**When** la migration est terminée
**Then** l'ancien stub est supprimé ou marqué comme déprécié
**And** tous les imports de `LLMClient` sont remplacés par des appels au AI Engine
**And** les tests sont mis à jour pour utiliser le mock du AI Engine

### AC5: Préservation de la compatibilité des endpoints REST
**Given** les endpoints REST existants (`/v1/chat/message`, `/v1/guidance/*`)
**When** ils sont appelés après la migration
**Then** le contrat API reste inchangé (mêmes champs request/response)
**And** seul le backend de génération change (AI Engine au lieu de LLMClient)
**And** aucune modification frontend n'est nécessaire

### AC6: Tests et non-régression
**Given** les tests existants des services Chat et Guidance
**When** ils sont exécutés après la migration
**Then** tous les tests passent avec le nouveau AI Engine (mode mock/test)
**And** aucune régression n'est introduite dans le comportement fonctionnel
**And** les nouveaux tests couvrent les use_cases guidance

## Tasks / Subtasks

### Subtask 15.3.1: Nouveaux templates de prompts pour Guidance
- [x] Créer `backend/app/ai_engine/prompts/guidance_daily_v1.jinja2` (AC: #3)
  - [x] Intégrer les données de naissance (birth_date, birth_time, birth_timezone)
  - [x] Intégrer le contexte de conversation récent
  - [x] Intégrer les instructions persona
  - [x] Ajouter le safety footer (pas de conseils médicaux/légaux/financiers)
- [x] Créer `backend/app/ai_engine/prompts/guidance_weekly_v1.jinja2` (AC: #3)
  - [x] Variante pour la guidance hebdomadaire
- [x] Créer `backend/app/ai_engine/prompts/guidance_contextual_v1.jinja2` (AC: #3)
  - [x] Intégrer situation, objective, time_horizon
- [x] Enregistrer les use_cases dans `prompt_registry.py` (AC: #3)
  - [x] `guidance_daily` -> guidance_daily_v1.jinja2
  - [x] `guidance_weekly` -> guidance_weekly_v1.jinja2
  - [x] `guidance_contextual` -> guidance_contextual_v1.jinja2
- [x] Tests de rendu des nouveaux templates (AC: #3)

### Subtask 15.3.2: Création d'un adaptateur AI Engine pour les services
- [x] Créer `backend/app/services/ai_engine_adapter.py` (AC: #1, #2)
  - [x] Fonction `generate_chat_reply(messages, context, user_id, trace_id) -> str`
  - [x] Fonction `generate_guidance(use_case, context, user_id, trace_id) -> str`
  - [x] Encapsule les appels au AI Engine avec gestion d'erreurs
  - [x] Mapping des erreurs AI Engine vers exceptions des services existants
- [x] Tests de l'adaptateur (AC: #1, #2)

### Subtask 15.3.3: Migration de ChatGuidanceService
- [x] Modifier `ChatGuidanceService.send_message()` (AC: #1)
  - [x] Remplacer `LLMClient().generate_reply()` par appel à l'adaptateur
  - [x] Passer le contexte de conversation au format AI Engine
  - [x] Conserver la logique de récupération hors-scope
- [x] Modifier `ChatGuidanceService._apply_off_scope_recovery()` (AC: #1)
  - [x] Utiliser l'adaptateur pour les retries de récupération
- [x] Tests mis à jour pour ChatGuidanceService (AC: #6)

### Subtask 15.3.4: Migration de GuidanceService
- [x] Modifier `GuidanceService.request_guidance()` (AC: #2)
  - [x] Remplacer `LLMClient().generate_reply()` par appel à l'adaptateur avec `guidance_daily` ou `guidance_weekly`
  - [x] Passer le contexte de naissance et conversation au format AI Engine
- [x] Modifier `GuidanceService.request_contextual_guidance()` (AC: #2)
  - [x] Utiliser `guidance_contextual` avec situation/objective/time_horizon
- [x] Modifier `GuidanceService._apply_off_scope_recovery()` (AC: #2)
  - [x] Utiliser l'adaptateur pour les retries
- [x] Tests mis à jour pour GuidanceService (AC: #6)

### Subtask 15.3.5: Suppression de l'ancien LLMClient
- [x] Marquer `backend/app/infra/llm/client.py` comme déprécié (AC: #4)
  - [x] Ajouter docstring de dépréciation pointant vers AI Engine
  - [x] Optionnel : supprimer le fichier si tous les usages sont migrés
- [x] Vérifier qu'aucun autre service n'utilise `LLMClient` (AC: #4)
  - [x] Grep dans le codebase pour `from app.infra.llm.client`
- [x] Mettre à jour les imports dans les tests (AC: #4)

### Subtask 15.3.6: Vérification de la compatibilité des endpoints
- [x] Vérifier que les endpoints `/v1/chat/*` fonctionnent toujours (AC: #5)
- [x] Vérifier que les endpoints `/v1/guidance/*` fonctionnent toujours (AC: #5)
- [x] Tests d'intégration des endpoints (AC: #5, #6)

## Dev Notes

### Architecture de migration

```
AVANT:
┌─────────────────────┐     ┌─────────────┐
│ ChatGuidanceService │────▶│  LLMClient  │ (stub - echo)
│ GuidanceService     │     │  (infra)    │
└─────────────────────┘     └─────────────┘

APRÈS:
┌─────────────────────┐     ┌───────────────────┐     ┌─────────────────┐
│ ChatGuidanceService │────▶│ AIEngineAdapter   │────▶│   AI Engine     │
│ GuidanceService     │     │ (services/)       │     │ (ai_engine/)    │
└─────────────────────┘     └───────────────────┘     │ ├─ OpenAI       │
                                                       │ ├─ Rate limit   │
                                                       │ ├─ Cache        │
                                                       │ └─ Prompts      │
                                                       └─────────────────┘
```

### Adaptateur AI Engine

L'adaptateur encapsule la complexité du AI Engine et offre une interface simple pour les services existants :

```python
# backend/app/services/ai_engine_adapter.py
from app.ai_engine.services import generate_service, chat_service
from app.ai_engine.schemas import GenerateRequest, ChatRequest, ChatMessage

class AIEngineAdapter:
    """Adaptateur pour intégrer le AI Engine dans les services existants."""
    
    @staticmethod
    async def generate_chat_reply(
        messages: list[dict],
        context: dict,
        user_id: int,
        request_id: str,
        trace_id: str,
    ) -> str:
        """Génère une réponse chat via le AI Engine."""
        # Convertir les messages au format ChatMessage
        # Appeler chat_service.chat()
        # Retourner le texte de la réponse
        pass
    
    @staticmethod
    async def generate_guidance(
        use_case: str,  # guidance_daily, guidance_weekly, guidance_contextual
        context: dict,
        user_id: int,
        request_id: str,
        trace_id: str,
    ) -> str:
        """Génère une guidance via le AI Engine."""
        # Construire la requête GenerateRequest
        # Appeler generate_service.generate_text()
        # Retourner le texte de la réponse
        pass
```

### Templates de prompts Guidance

Les nouveaux templates doivent reprendre la structure des prompts existants dans `GuidanceService._build_prompt()` :

```jinja2
{# guidance_daily_v1.jinja2 #}
[guidance_prompt_version:guidance-v1]
{{ persona_line }}
You are a prudent astrology assistant.
Never provide medical, legal, or financial certainty.
Period: daily
Birth date: {{ birth_date }}
Birth time: {{ birth_time }}
Birth timezone: {{ birth_timezone }}
Recent context:
{% for line in context_lines %}
{{ line }}
{% endfor %}
Return practical and calm guidance in French.
```

### Mapping des erreurs

| Erreur AI Engine | Erreur Service existant |
|-----------------|------------------------|
| `ValidationError` | `ChatGuidanceServiceError(code="invalid_chat_input")` |
| `RateLimitExceededError` | `ChatGuidanceServiceError(code="rate_limit_exceeded")` |
| `ProviderTimeoutError` | `TimeoutError` (rethrow) |
| `ProviderUnavailableError` | `ConnectionError` (rethrow) |
| `ContextTooLargeError` | `ChatGuidanceServiceError(code="context_too_large")` |

### Tests à modifier

1. `backend/app/tests/test_chat_guidance_service.py`
   - Mocker `AIEngineAdapter` au lieu de `LLMClient`
   - Ajouter tests pour les nouveaux use_cases

2. `backend/app/tests/test_guidance_service.py`
   - Mocker `AIEngineAdapter` au lieu de `LLMClient`
   - Tests pour guidance_daily, guidance_weekly, guidance_contextual

3. `backend/app/ai_engine/tests/test_prompt_registry.py`
   - Ajouter tests de rendu pour les nouveaux templates guidance

### Project Structure Notes

- L'adaptateur est dans `services/` car il orchestre l'appel au AI Engine
- Les templates de prompts sont dans `ai_engine/prompts/` pour rester cohérents avec le Prompt Registry
- Les services existants conservent leur interface publique (compatibilité des endpoints)

### Alignment avec l'architecture existante

- Respect de la séparation `services` (orchestration) / `ai_engine` (génération IA)
- Utilisation des patterns de gestion d'erreurs existants
- Intégration avec les métriques et logs déjà en place dans le AI Engine
- Pas de modification des endpoints REST (transparence pour le frontend)

### References

- [Source: docs/agent/story-15-ai-text-engine-bmad.md] — Objectif #3 : "Réduire le couplage des services métier à OpenAI"
- [Source: _bmad-output/implementation-artifacts/15-1-ai-text-engine-openai-gateway.md] — Module AI Engine
- [Source: _bmad-output/implementation-artifacts/15-2-ai-text-engine-rate-limiting-observability-docker.md] — Rate limiting et observabilité
- [Source: backend/app/services/chat_guidance_service.py] — Service à migrer
- [Source: backend/app/services/guidance_service.py] — Service à migrer
- [Source: backend/app/infra/llm/client.py] — Ancien stub à supprimer

### Dépendances

**Stories pré-requises :**
- Story 15.1 (AI Engine - OpenAI Gateway) ✅
- Story 15.2 (Rate limiting, observabilité, Docker) ✅

**Services impactés :**
- `ChatGuidanceService` — Migration vers AI Engine
- `GuidanceService` — Migration vers AI Engine
- `LLMClient` — Suppression/dépréciation

### Tests DoD

- [x] Nouveaux templates guidance : 8 tests spécifiques guidance (rendu daily, weekly, contextual, variables manquantes, context_lines) sur 19 tests total dans prompt_registry
- [x] Adaptateur : 13 tests (succès, erreurs rate_limit/context_too_large/validation, mapping, assess_off_scope, reset_generators)
- [x] ChatGuidanceService : tous les tests existants passent + nouveaux tests AI Engine
- [x] GuidanceService : tous les tests existants passent + nouveaux tests AI Engine
- [x] Intégration endpoints : 4 tests minimum (chat, guidance daily/weekly/contextual)
- [x] Aucune référence à `LLMClient` dans le code (sauf dépréciation)

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (code-review: 2026-02-22)

### Debug Log References

- Tests unitaires: 70 passed (17 guidance_service, 21 chat_guidance_service, 13 ai_engine_adapter, 19 prompt_registry)
- Lint: All checks passed (ruff)

### Completion Notes List

- **CR4 Fix (2026-02-22)** : Code mort supprimé — `_build_recovery_prompt` (chat + guidance), `_build_prompt`, `_build_contextual_prompt` (guidance). DoD test count corrigé (14→13).
- **CR5 Fix (2026-02-22)** : Pattern error handling unifié — `context_too_large` explicite dans `GuidanceService`. Absence de backoff documentée dans `ChatGuidanceService` (choix UX). DoD guidance tests corrigé (6→8).
- **CR6 Fix (2026-02-22)** : Performance async — `time.sleep()` bloquant remplacé par `asyncio.sleep()` dans `GuidanceService._sleep_before_retry_async()`. Documentation `natal_chart_summary` (feature non implémentée) ajoutée dans les services. Test unitaire `period=weekly` ajouté.
- **CR7 Fix (2026-02-22)** : Documentation — Ajout note sur pattern `asyncio.run()` dans docstrings des méthodes sync wrapper (`request_guidance`, `request_contextual_guidance`). Code review final validé avec 0 issues HIGH/MEDIUM.
- **CR8 Fix (2026-02-22)** : Debug Log corrigé (63→70 tests). Test `reset_test_generators` amélioré avec assertions avant/après reset. DoD clarifié (8 tests guidance-spécifiques sur 19 total prompt_registry).
- **CR9 Fix (2026-02-22)** : Docstrings harmonisées en anglais dans `GuidanceService` (6 méthodes privées). Code review final: 0 issues HIGH/MEDIUM, story validée.

1. **AIEngineAdapter créé** avec test generators pour faciliter les tests unitaires et d'intégration
2. **Templates Jinja2 guidance_* créés** avec structure cohérente incluant birth_data, persona_line, context_lines
3. **Services migrés** de LLMClient vers AIEngineAdapter avec gestion async complète
4. **LLMClient marqué déprécié** avec warnings et docstrings pointant vers AI Engine
5. **Tests mis à jour** pour utiliser set_test_chat_generator / set_test_guidance_generator
6. **Code Review (2026-02-22)**: Tests dupliqués supprimés, docstrings Pydantic harmonisées en anglais
7. **Code Review #2 (2026-02-22)**: Templates Jinja2 corrigés (context.persona_line → context.extra.persona_line), test assertion ajoutée, error handling refactorisé avec `_handle_ai_engine_error()`, constante `DEFAULT_MODEL` introduite
8. **Code Review #3 (2026-02-22)**: Type hint `NoReturn` ajouté sur `_handle_ai_engine_error`, constante `DEFAULT_PROVIDER` introduite, tests error handling étendus (context_too_large, validation_error), validation conversation extraite dans `_resolve_conversation_id()`

### File List

**Fichiers créés :**
- `backend/app/services/ai_engine_adapter.py` — Adaptateur AI Engine avec test generators
- `backend/app/ai_engine/prompts/guidance_daily_v1.jinja2` — Template guidance quotidienne
- `backend/app/ai_engine/prompts/guidance_weekly_v1.jinja2` — Template guidance hebdomadaire
- `backend/app/ai_engine/prompts/guidance_contextual_v1.jinja2` — Template guidance contextuelle
- `backend/app/tests/unit/test_ai_engine_adapter.py` — Tests unitaires de l'adaptateur

**Fichiers modifiés :**
- `backend/app/ai_engine/services/prompt_registry.py` — Ajout use_cases guidance_daily, guidance_weekly, guidance_contextual
- `backend/app/services/chat_guidance_service.py` — Migration vers AIEngineAdapter (async)
- `backend/app/services/guidance_service.py` — Migration vers AIEngineAdapter (async)
- `backend/app/infra/llm/client.py` — Dépréciation avec DeprecationWarning
- `backend/app/infra/llm/__init__.py` — Mise à jour docstring dépréciation
- `backend/app/tests/unit/test_chat_guidance_service.py` — Utilise set_test_chat_generator
- `backend/app/tests/unit/test_guidance_service.py` — Utilise set_test_guidance_generator
- `backend/app/ai_engine/tests/test_prompt_registry.py` — Tests rendu templates guidance
- `backend/app/tests/integration/test_chat_api.py` — Migration vers test generators
- `backend/app/tests/integration/test_guidance_api.py` — Migration vers test generators
