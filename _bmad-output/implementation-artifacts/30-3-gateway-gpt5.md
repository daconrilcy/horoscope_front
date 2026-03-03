# Story 30.3: Gateway GPT-5 — Orchestration Responses API avec reasoning & verbosity

Status: done

## Story

As a system owner,
I want exploiter les capacités natives de GPT-5 (reasoning, verbosity, typed blocks),
So that les interprétations soient plus pertinentes, denses et conformes aux nouveaux standards OpenAI.

## Contexte et Objectifs

Cette story adapte le Gateway LLM pour supporter GPT-5 et ses paramètres spécifiques.
- Ajout de colonnes `reasoning_effort` et `verbosity` en DB (table `llm_prompt_versions`).
- Support des `typed content blocks` dans `ResponsesClient` pour GPT-5.
- Transmission automatique de ces nouveaux paramètres du Gateway vers le client LLM.
- Publication de nouveaux prompts optimisés GPT-5 pour le use case `natal_interpretation`.

**Non-objectifs :**
- Pas de changement pour les anciens modèles (gpt-4o-mini).
- Pas de refactorisation vers la structure 3-rôles (system/developer/user) immédiate.

## Acceptance Criteria

### AC1: Migration Alembic appliquée
**Given** la base de données existante
**When** la migration est appliquée
**Then** la table `llm_prompt_versions` possède les colonnes `reasoning_effort` et `verbosity`.

### AC2: Support GPT-5 dans ResponsesClient
**Given** un appel vers un modèle `gpt-5`
**When** `ResponsesClient.execute` est appelé
**Then** le payload envoyé inclut les paramètres `reasoning` et `verbosity`
**And** les messages sont convertis au format `typed content blocks`.

### AC3: Orchestration Gateway enrichie
**Given** une configuration de use case chargée depuis la DB
**When** `LLMGateway` prépare l'appel
**Then** il extrait et transmet les valeurs de reasoning et verbosity.

### AC4: Nouveaux prompts GPT-5 en DB
**Given** l'exécution de `seed_30_3_gpt5_prompts.py`
**When** le use case `natal_interpretation` est appelé
**Then** c'est le nouveau prompt optimisé GPT-5 qui est utilisé.

## Tasks / Subtasks

### Subtask 30.3.1: Database & ORM
- [x] Créer et appliquer la migration Alembic pour `reasoning_effort` et `verbosity`.
- [x] Mettre à jour l'ORM `LlmPromptVersionModel` dans `backend/app/infra/db/models/llm_prompt.py`.
- [x] Ajouter les champs au modèle Pydantic `UseCaseConfig` dans `backend/app/llm_orchestration/models.py`.

### Subtask 30.3.2: LLM Gateway & Providers
- [x] Modifier `LLMGateway.execute()` pour transmettre les nouveaux paramètres.
- [x] Étendre la détection des reasoning models dans `gateway.py` pour inclure le préfixe `gpt-5`.
- [x] Implémenter `_to_typed_content_blocks` dans `ResponsesClient`.
- [x] Modifier `ResponsesClient.execute()` pour inclure `reasoning` et `verbosity` dans le payload API.

### Subtask 30.3.3: Seed & Prompts
- [x] Créer le script `backend/scripts/seed_30_3_gpt5_prompts.py`.
- [x] Rédiger le prompt `NATAL_COMPLETE_PROMPT_V2` sans contraintes de longueur textuelles (déléguées à GPT-5).

### Subtask 30.3.4: Validation & Tests
- [x] Créer `backend/app/tests/unit/test_responses_client_gpt5.py`.
- [x] Créer `backend/app/tests/integration/test_gateway_gpt5_params.py`.

## Dev Notes

### Support GPT-5
Les modèles commençant par `gpt-5` activent automatiquement :
1. La conversion en `typed content blocks`.
2. L'exclusion de `temperature` si les paramètres de reasoning sont utilisés.
3. L'augmentation des `max_output_tokens` par défaut à 16384 minimum.

### Format Typed Content Blocks
```json
{"role": "developer", "content": [{"type": "input_text", "text": "..."}]}
```

## Project Structure Notes
- La migration Alembic doit suivre la séquence actuelle.
- Le client LLM reste compatible avec les anciens modèles via des conditions sur le nom du modèle.

## Alignment avec l'architecture existante
- Intégration transparente dans le cycle de vie du Gateway existant.
- Utilisation du système de seed idempotent pour la mise à jour des prompts.

## References
- [Source: docs/agent/story-30-3-gateway-gpt5.md]
- [Source: backend/app/llm_orchestration/gateway.py]

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Flash

### Completion Notes List
- Support reasoning/verbosity opérationnel.
- Migration DB effectuée.
- Prompts GPT-5 seédés avec succès.
- Tests de non-régression validés.

### Code Review Fixes (2026-03-02)
- [C1] `_to_typed_content_blocks()` rendue idempotente + préserve tous les champs du message
- [C2] Prompt `NATAL_COMPLETE_PROMPT_V2` réécrit : ajout `{{locale}}`, `{{use_case}}`, `{{persona_name}}`, règles de vérité, auto-check evidence, directives PREMIUM
- [C3] Seed `seed_30_3_gpt5_prompts.py` rendu idempotent + lint obligatoire + `invalidate_cache()`
- [H1] `reasoning_effort` corrigé : `"high"` → `"low"` (spec AC8)
- [H2] Commentaire ajouté sur le format `reasoning_effort` flat (Responses API) vs `reasoning.effort` (Chat Completions)
- [M1] `max_output_tokens` corrigé : `16384` → `32000`, `temperature` : `1.0` → `0.5`
- [M2] Tests ajoutés : idempotence typed blocks, préservation des champs, o4- sans temperature, gpt4o sans reasoning
- [M3] Détection reasoning models dans client alignée avec gateway : ajout `o4-` et `o4`

### File List
- `backend/migrations/versions/4b2d52442492_add_reasoning_effort_verbosity_to_.py` (Nouveau)
- `backend/app/infra/db/models/llm_prompt.py` (Modifié)
- `backend/app/llm_orchestration/models.py` (Modifié)
- `backend/app/llm_orchestration/gateway.py` (Modifié)
- `backend/app/llm_orchestration/providers/responses_client.py` (Modifié)
- `backend/scripts/seed_30_3_gpt5_prompts.py` (Nouveau)
- `backend/app/tests/unit/test_responses_client_gpt5.py` (Nouveau)
- `backend/app/tests/integration/test_gateway_gpt5_params.py` (Nouveau)
