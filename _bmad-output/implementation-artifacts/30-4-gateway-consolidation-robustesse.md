# Story 30.4: Gateway Consolidation — 3-Rôles, Robustesse & Observabilité

Status: done

## Story

As a system owner,
I want consolider le LLMGateway et le ResponsesClient sur les axes robustesse, observabilité, et architecture 3-rôles,
so that les appels GPT-5 sont corrects, traçables, et moins fragiles en cas de panne ou de changement de SDK.

## Modifications Réalisées

### 1. Robustesse & SDK
- **Pinning SDK `openai`** : Mise à jour de `backend/pyproject.toml` vers `openai>=2.0.0`.
- **Gestion des Exceptions** : Utilisation d'exceptions typées et suppression du string-match.
- **Headers de Tracing** : Transmission de `x-request-id`, `x-trace-id` et `x-use-case`.
- **Test Fallbacks V2** : Support des modes dégradés en test dans `AIEngineAdapter`.
- **Alignement Historique** : Correction de `ai_engine_adapter.py` pour transmettre l'historique (`history`) au lieu de la liste complète des messages au gateway.

### 2. Architecture 3-Rôles
- **Refactor `chart_json`** : Passage des données techniques dans le rôle `user` (Technical Data).
- **Mise à jour des Seeds** : Alignement de `seed_28_4.py` sur les standards stricts (evidence `min_items=0`, limites à 360 caractères).

## Fichiers Modifiés
- `backend/pyproject.toml`
- `backend/app/llm_orchestration/providers/responses_client.py`
- `backend/app/llm_orchestration/gateway.py`
- `backend/app/services/ai_engine_adapter.py`
- `backend/scripts/seed_28_4.py`
- `backend/scripts/seed_29_prompts.py`

## Validation
- [x] Tests unitaires exceptions provider : 3/3 passent.
- [x] Test 3-rôles : 1/1 passe.
- [x] Intégration Chat avec historique : 30/30 passent.
