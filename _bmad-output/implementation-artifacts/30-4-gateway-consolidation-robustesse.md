# Story 30.4: Gateway Consolidation — 3-Rôles, Robustesse & Observabilité

Status: done

## Story

As a system owner,
I want consolider le LLMGateway et le ResponsesClient sur les axes robustesse, observabilité, et architecture 3-rôles,
so that les appels GPT-5 sont corrects, traçables, et moins fragiles en cas de panne ou de changement de SDK.

## Modifications Réalisées

### 1. Robustesse & SDK
- **Pinning SDK `openai`** : Mise à jour de `backend/pyproject.toml` vers `openai>=2.0.0` pour supporter nativement `verbosity` et l'API Responses v2.
- **Gestion des Exceptions** : Refactor de `ResponsesClient` pour utiliser les exceptions typées (`RateLimitError`, `APITimeoutError`) et suppression des détections par string-match.
- **Headers de Tracing** : Transmission systématique de `x-request-id`, `x-trace-id` et `x-use-case` vers le provider LLM.
- **Test Fallbacks V2** : Support des modes dégradés en test dans `AIEngineAdapter` pour l'orchestration V2, permettant aux tests d'intégration de passer sans clé API réelle (echo mock).

### 2. Architecture 3-Rôles
- **Refactor `chart_json`** : Retrait de `chart_json` des placeholders requis pour les interprétations natales. Les données techniques sont désormais envoyées dans le rôle `user` (Technical Data) au lieu du rôle `developer`, respectant la séparation instructions/données.
- **Mise à jour des Stubs** : Les `USE_CASE_STUBS` du gateway ont été complétés pour éviter les erreurs 422 lors de la migration des services existants vers la V2.

### 3. Performance
- **Parsing Préventif** : Le `ResponsesClient` tente de parser le JSON immédiatement après l'appel si un format structuré est demandé, évitant un double parsing ultérieur.

## Fichiers Modifiés
- `backend/pyproject.toml`
- `backend/app/llm_orchestration/providers/responses_client.py`
- `backend/app/llm_orchestration/gateway.py`
- `backend/app/services/ai_engine_adapter.py`
- `backend/scripts/seed_29_prompts.py`
- `backend/app/tests/unit/test_responses_client_exceptions.py`
- `backend/app/tests/unit/test_gateway_3_roles.py`

## Validation
- [x] Tests unitaires exceptions provider : 3/3 passent.
- [x] Test 3-rôles (chart_json dans user) : 1/1 passe.
- [x] Intégration Chat/Guidance en V2 avec test fallback : 51/51 passent.
