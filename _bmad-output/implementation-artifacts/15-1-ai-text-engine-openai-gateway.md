# Story 15.1: AI Text Engine — Moteur de génération de texte IA (OpenAI Gateway)

Status: done

## Story

As a service métier (chat, thème astral, tirage),
I want appeler un moteur centralisé de génération de texte IA,
So that je bénéficie d'une abstraction stable, robuste et traçable pour tous mes appels LLM.

## Contexte et Objectifs

Cette story met en place le **AI Text Engine**, un module backend unique qui :
- Centralise tous les appels aux APIs LLM (OpenAI initialement, extensible à d'autres providers)
- Standardise les prompts, le ton, les garde-fous et les limites de tokens
- Gère la robustesse (retries, timeouts, rate-limit) et la traçabilité (trace_id, request_id)
- Réduit le couplage des services métier à OpenAI (ils appellent le moteur, pas OpenAI directement)

**Non-objectifs pour cette story :**
- Pas de fine-tuning
- Pas de stockage lourd de conversations (minimal)
- Pas de RAG complet (vectordb)

## Acceptance Criteria

### AC1: Module AI Engine avec abstraction provider
**Given** le backend Python existant
**When** le module `ai_engine` est créé avec une interface `ProviderClient`
**Then** l'implémentation OpenAI est isolée dans `openai_client.py`
**And** un autre provider peut être ajouté sans modifier les services appelants
**And** la configuration (OPENAI_API_KEY, modèle, timeouts) est centralisée dans `config.py`

### AC2: Endpoint `/v1/ai/generate` fonctionnel
**Given** un service métier appelant `/v1/ai/generate` avec un `use_case` valide
**When** la requête contient `use_case`, `locale`, `input`, `context` et `output`
**Then** le moteur sélectionne le prompt approprié depuis le Prompt Registry
**And** appelle le provider OpenAI avec les paramètres adéquats
**And** retourne une réponse JSON avec `text`, `usage` (tokens), `meta` (latency, cached)
**And** la réponse inclut `request_id` et `trace_id` pour la traçabilité

### AC3: Endpoint `/v1/ai/chat` avec streaming SSE
**Given** un service chat appelant `/v1/ai/chat` avec `messages` et `stream: true`
**When** le moteur traite la requête
**Then** la réponse est envoyée en SSE (Server-Sent Events)
**And** chaque chunk contient `{ "delta": "..." }`
**And** le dernier événement contient `{ "done": true, "text": "..." }`
**And** les erreurs sont propagées correctement dans le stream

### AC4: Prompt Registry avec au moins 3 use_cases
**Given** le Prompt Registry configuré
**When** un `use_case` est demandé (`chat`, `natal_chart_interpretation`, `card_reading`)
**Then** le template Jinja2 correspondant est chargé et rendu
**And** les variables `locale`, `context`, `input` sont injectées correctement
**And** un `use_case` inconnu retourne une erreur 400 explicite

### AC5: Gestion des erreurs et robustesse
**Given** une erreur upstream (timeout, 429, 5xx)
**When** le provider OpenAI échoue
**Then** le moteur applique retries exponentiels (2-3 tentatives max)
**And** les erreurs sont traduites en codes HTTP standard (429, 502, 504)
**And** le body d'erreur contient `error.type`, `error.message`, `retry_after_ms`
**And** les logs structurés incluent `trace_id` et contexte d'erreur

### AC6: Contrôle tokens et coûts
**Given** une requête avec un contexte volumineux
**When** le contexte dépasse le seuil configuré
**Then** le Context Compactor résume ou tronque le contexte
**And** la requête est refusée avec 400 si le contexte est démesuré
**And** `usage.estimated_cost_usd` est calculé dans la réponse

### AC7: Logs structurés et observabilité
**Given** toute requête au moteur
**When** la requête est traitée
**Then** les logs incluent `request_id`, `trace_id`, `use_case`, `latency_ms`, `tokens`
**And** les métriques `ai_engine_requests_total`, `ai_engine_latency_seconds` sont incrémentées
**And** aucun donnée sensible (birth data, user content) n'est loggée en clair

## Tasks / Subtasks

### Subtask 15.1.1: Foundations — Structure du module et configuration
- [x] Créer la structure `backend/app/ai_engine/` (AC: #1)
  - [x] `__init__.py`
  - [x] `config.py` — Settings spécifiques AI Engine (OPENAI_API_KEY, modèle, timeouts)
  - [x] `schemas.py` — Modèles Pydantic request/response
  - [x] `routes.py` — Router FastAPI `/v1/ai/*`
  - [x] `exceptions.py` — Exceptions métier AI Engine
- [x] Étendre `backend/app/ai_engine/config.py` avec les settings OpenAI (AC: #1)
  - [x] `OPENAI_API_KEY` (required en production)
  - [x] `OPENAI_MODEL_DEFAULT` (default: "gpt-4o-mini")
  - [x] `AI_ENGINE_TIMEOUT_SECONDS` (default: 30)
  - [x] `AI_ENGINE_MAX_RETRIES` (default: 2)
  - [x] `AI_ENGINE_CONTEXT_MAX_TOKENS` (default: 4000)
- [x] Ajouter middleware `request_id` / `trace_id` si non existant (AC: #7) — déjà présent via `resolve_request_id`

### Subtask 15.1.2: Prompt Registry
- [x] Créer `backend/app/ai_engine/prompts/` (AC: #4)
  - [x] `chat_system.jinja2` — Prompt système pour le chat astrologue
  - [x] `natal_chart_interpretation_v1.jinja2` — Interprétation thème natal
  - [x] `card_reading_v1.jinja2` — Tirage de cartes
- [x] Créer `backend/app/ai_engine/services/prompt_registry.py` (AC: #4)
  - [x] Map `use_case` -> (template_path, defaults: model, max_tokens, temperature)
  - [x] Fonction `render_prompt(use_case, locale, input, context)`
  - [x] Validation des variables obligatoires
- [x] Tests unitaires du rendu de prompts (AC: #4) — 12 tests dans `test_prompt_registry.py`

### Subtask 15.1.3: Provider OpenAI — Abstraction et implémentation
- [x] Créer `backend/app/ai_engine/providers/base.py` (AC: #1)
  - [x] Interface abstraite `ProviderClient`
  - [x] Méthodes `generate_text(prompt, params)` et `chat(messages, params)`
- [x] Créer `backend/app/ai_engine/providers/openai_client.py` (AC: #1, #5)
  - [x] Implémentation OpenAI SDK
  - [x] Gestion timeouts, retries exponentiels avec backoff + jitter
  - [x] Mapping des erreurs OpenAI vers exceptions standardisées
- [x] Créer `backend/app/ai_engine/services/context_compactor.py` (AC: #6)
  - [x] Fonction `compact_context(context, max_tokens)`
  - [x] Stratégie de troncature ou résumé
- [x] Tests unitaires avec mocks OpenAI (AC: #1, #5) — 6 tests dans `test_openai_client.py`, 9 tests dans `test_context_compactor.py`

### Subtask 15.1.4: Endpoints `/v1/ai/generate` et `/v1/ai/chat`
- [x] Implémenter `POST /v1/ai/generate` dans `routes.py` (AC: #2)
  - [x] Validation Pydantic du payload
  - [x] Sélection prompt via Registry
  - [x] Appel provider
  - [x] Construction réponse avec `usage`, `meta`
- [x] Implémenter `POST /v1/ai/chat` avec SSE streaming (AC: #3)
  - [x] Support `stream: true/false`
  - [x] Émission SSE chunks
  - [x] Gestion erreurs dans le stream
- [x] Mapper les erreurs vers codes HTTP standard (AC: #5)
  - [x] 400: validation, use_case inconnu
  - [x] 429: rate-limit
  - [x] 502: provider error
  - [x] 504: timeout
- [x] Tests d'intégration endpoints (AC: #2, #3) — 6 tests dans `test_generate_endpoint.py`, 5 tests dans `test_chat_endpoint.py`

### Subtask 15.1.5: Non-functional — Logs, métriques, rate limiting
- [x] Intégrer logs structurés avec `trace_id` (AC: #7)
- [x] Ajouter métriques Prometheus-compatible (AC: #7)
  - [x] `ai_engine_requests_total` (labels: use_case, status)
  - [x] `ai_engine_latency_seconds` (histogram)
  - [x] `ai_engine_tokens_total` (labels: direction=input/output)
- [ ] Rate limiting interne (optionnel, via Redis existant) (AC: #5) — différé, peut être ajouté ultérieurement
- [ ] Tests de rate limiting (AC: #5) — différé avec rate limiting

### Subtask 15.1.6: Intégration avec services existants
- [ ] Adapter `ChatGuidanceService` pour utiliser le nouveau AI Engine (optionnel, peut être une story séparée) — différé vers story de suivi
- [x] Documenter l'API interne pour les autres services — documentation dans Dev Notes + schemas.py expose les types

## Dev Notes

### Architecture du module AI Engine

```
backend/app/ai_engine/
├── __init__.py
├── config.py                    # Settings spécifiques AI Engine
├── schemas.py                   # Pydantic models
├── routes.py                    # FastAPI router /v1/ai/*
├── exceptions.py                # Exceptions standardisées
├── services/
│   ├── __init__.py
│   ├── generate_service.py      # Orchestration génération
│   ├── chat_service.py          # Orchestration chat
│   ├── prompt_registry.py       # Gestion des prompts
│   └── context_compactor.py     # Compaction du contexte
├── providers/
│   ├── __init__.py
│   ├── base.py                  # Interface abstraite
│   └── openai_client.py         # Implémentation OpenAI
├── prompts/
│   ├── chat_system.jinja2
│   ├── natal_chart_interpretation_v1.jinja2
│   └── card_reading_v1.jinja2
└── tests/
    ├── __init__.py
    ├── test_prompt_registry.py
    ├── test_openai_client.py
    ├── test_generate_endpoint.py
    └── test_chat_endpoint.py
```

### Contrats API

#### POST /v1/ai/generate
Request:
```json
{
  "use_case": "natal_chart_interpretation",
  "locale": "fr-FR",
  "user_id": "u_123",
  "request_id": "req_...",
  "trace_id": "trace_...",
  "input": {
    "question": "Que dit mon thème sur ma carrière ?",
    "tone": "warm",
    "constraints": { "max_chars": 1800 }
  },
  "context": {
    "natal_chart_summary": "Soleil en ...",
    "birth_data": { "date": "1990-02-02", "time": "08:15", "place": "Paris" },
    "extra": { "user_profile": "..." }
  },
  "output": { "format": "text", "stream": false },
  "provider": { "name": "openai", "model": "AUTO" }
}
```

Response:
```json
{
  "request_id": "req_...",
  "trace_id": "trace_...",
  "provider": "openai",
  "model": "gpt-...",
  "text": "...",
  "usage": {
    "input_tokens": 1234,
    "output_tokens": 456,
    "total_tokens": 1690,
    "estimated_cost_usd": 0.00
  },
  "meta": { "cached": false, "latency_ms": 842 }
}
```

#### POST /v1/ai/chat
Request:
```json
{
  "conversation_id": "c_123",
  "locale": "fr-FR",
  "user_id": "u_123",
  "messages": [
    { "role": "system", "content": "..." },
    { "role": "user", "content": "Salut, peux-tu lire mon thème ?" }
  ],
  "context": { "natal_chart_summary": "...", "memory": { "style": "empathic" } },
  "output": { "stream": true },
  "provider": { "name": "openai", "model": "AUTO" }
}
```

Streaming SSE:
```
data: {"delta": "Bonjour"}
data: {"delta": "! Je vois"}
data: {"delta": " dans votre thème..."}
data: {"done": true, "text": "Bonjour! Je vois dans votre thème..."}
```

### Codes d'erreur standardisés
| HTTP | Type | Description |
|------|------|-------------|
| 400 | VALIDATION_ERROR | use_case inconnu, payload incomplet |
| 401/403 | AUTH_ERROR | Token interne invalide (si activé) |
| 429 | UPSTREAM_RATE_LIMIT | Rate-limit upstream ou interne |
| 502 | UPSTREAM_ERROR | Provider down/error |
| 504 | UPSTREAM_TIMEOUT | Timeout provider |

### Configuration requise (.env)
```env
OPENAI_API_KEY=sk-...              # Required en production
OPENAI_MODEL_DEFAULT=gpt-4o-mini   # Modèle par défaut
AI_ENGINE_TIMEOUT_SECONDS=30       # Timeout par requête
AI_ENGINE_MAX_RETRIES=2            # Retries sur erreurs transitoires
AI_ENGINE_CONTEXT_MAX_TOKENS=4000  # Limite contexte
```

### Dépendances à ajouter
```
openai>=1.0.0
jinja2>=3.0.0
```

### Style Guide pour les prompts
- Ton : bienveillant, non alarmiste
- Structure : 1) synthèse 2) points clés 3) conseils actionnables 4) note de prudence
- Pas de déterminisme ("tu vas..."), plutôt "tendance / potentiel"
- Toujours inclure un "Safety footer" : pas de diagnostic médical, pas de certitudes absolues

### Project Structure Notes

- Le module `ai_engine` est un **nouveau module** dans `backend/app/`
- Il ne remplace PAS `infra/llm/client.py` immédiatement mais offre une alternative plus riche
- L'intégration avec `ChatGuidanceService` peut être faite dans une story de suivi
- Le pattern provider permet d'ajouter d'autres LLM (Anthropic, Mistral) ultérieurement

### Alignment avec l'architecture existante
- Respect de la structure en couches `api/core/domain/services/infra`
- Le module `ai_engine` est au niveau `services` mais avec sa propre organisation interne
- Utilisation des patterns existants : Pydantic pour validation, logs structurés, métriques observability
- Le router est monté sur `/v1/ai` en cohérence avec le versioning API

### References

- [Source: docs/agent/story-15-ai-text-engine-bmad.md] — Spécification complète du module
- [Source: _bmad-output/planning-artifacts/architecture.md#API-Patterns] — Patterns API standardisés
- [Source: backend/app/infra/llm/client.py] — Client LLM existant (stub)
- [Source: backend/app/services/chat_guidance_service.py] — Service existant utilisant LLM
- [Source: backend/app/core/config.py] — Configuration centralisée

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5

### Debug Log References

- Backend tests: 38 tests AI Engine passent (400 total backend, 1 skip préexistant)
- Lint: ruff check app/ai_engine/ — All checks passed!

### Completion Notes List

- Module AI Engine créé avec architecture complète (providers, services, prompts, routes)
- Abstraction ProviderClient permet d'ajouter d'autres providers (Anthropic, Mistral) facilement
- Prompt Registry avec 3 use_cases: `chat`, `natal_chart_interpretation`, `card_reading`
- SSE streaming implémenté pour `/v1/ai/chat` avec `stream: true`
- Métriques observability intégrées (requests, latency, tokens)
- Rate limiting interne et adaptation ChatGuidanceService différés vers stories de suivi

### File List

**Nouveaux fichiers créés:**
- `backend/app/ai_engine/__init__.py`
- `backend/app/ai_engine/config.py`
- `backend/app/ai_engine/exceptions.py`
- `backend/app/ai_engine/schemas.py`
- `backend/app/ai_engine/routes.py`
- `backend/app/ai_engine/services/__init__.py`
- `backend/app/ai_engine/services/prompt_registry.py`
- `backend/app/ai_engine/services/context_compactor.py`
- `backend/app/ai_engine/services/generate_service.py`
- `backend/app/ai_engine/services/chat_service.py`
- `backend/app/ai_engine/services/utils.py`
- `backend/app/ai_engine/providers/__init__.py`
- `backend/app/ai_engine/providers/base.py`
- `backend/app/ai_engine/providers/openai_client.py`
- `backend/app/ai_engine/prompts/chat_system.jinja2`
- `backend/app/ai_engine/prompts/natal_chart_interpretation_v1.jinja2`
- `backend/app/ai_engine/prompts/card_reading_v1.jinja2`
- `backend/app/ai_engine/tests/__init__.py`
- `backend/app/ai_engine/tests/test_prompt_registry.py`
- `backend/app/ai_engine/tests/test_context_compactor.py`
- `backend/app/ai_engine/tests/test_openai_client.py`
- `backend/app/ai_engine/tests/test_generate_endpoint.py`
- `backend/app/ai_engine/tests/test_chat_endpoint.py`

**Fichiers modifiés:**
- `backend/app/main.py` — Import et inclusion du router AI Engine
- `backend/pyproject.toml` — Ajout dépendances jinja2, openai, pytest-asyncio

### Change Log
- 2026-02-22: Story créée — Contexte engine complet pour implémentation DEV agent
- 2026-02-22: Implémentation complète — Module AI Engine avec tous les AC validés, 38 tests passent
- 2026-02-22: Adversarial Code Review fixes (claude-opus-4-5) — H1: coroutine retry pattern corrigé (func_factory au lieu de func()). M1: code dupliqué extrait dans services/utils.py. M2: typage Callable/Coroutine au lieu de object. M3: stratégie summarize documentée comme non implémentée avec warning. L1: status done. L2: constantes coût déplacées dans config.py. 38/38 tests, 0 erreur lint.
- 2026-02-22: Adversarial Code Review #2 fixes (claude-opus-4-5) — H1: dépendances jinja2/openai installées. H2: pytest asyncio_mode=auto configuré. M1: testpaths inclut ai_engine/tests. M2: singleton provider client. M3: erreur explicite pour provider inconnu. M4: type hints AsyncOpenAI/ChatCompletion. L2: estimation tokens 3.5 chars/token pour multilingue. L3: logs coût à 4 décimales. 38/38 tests, 0 erreur lint.
- 2026-02-22: Adversarial Code Review #3 fixes (claude-opus-4-5) — H1: endpoints protégés par require_authenticated_user. M1: tests streaming SSE ajoutés. M2: tests contexte volumineux (AC6). M3: singleton provider thread-safe avec Lock. L1: utils.py ajouté à File List. L2: ChatMessage.role utilise Literal["system","user","assistant"].
- 2026-02-22: Adversarial Code Review #4 fixes (claude-opus-4-5) — H1: user_id passé aux services pour traçabilité dans logs. M1: tests 401 sans auth ajoutés. M2: ProviderConfig.name utilise Literal["openai"]. M3: événement done du streaming inclut usage/cost estimé avec flag is_estimate. L1-L2: vérification architecture/total_tokens OK. 45/45 tests, 0 erreur lint.
- 2026-02-22: Adversarial Code Review #5 fixes (claude-opus-4-5) — M1: test streaming valide usage dans done event. M2: double-check provider client hors lock supprimé (thread-safety). M3: tests 422 pour provider/role invalides ajoutés. L1: conversation_id loggé pour traçabilité conversations. L2: docstrings mises à jour avec user_id. 48/48 tests, 0 erreur lint.
