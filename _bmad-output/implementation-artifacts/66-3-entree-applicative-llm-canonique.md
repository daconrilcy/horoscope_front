# Story 66.3 — Créer une entrée applicative LLM canonique

Status: done

## Story

En tant qu'**architecte backend**,  
je veux **que la couche `AIEngineAdapter` soit refactorisée en point d'entrée applicatif LLM à responsabilité explicite et clairement documentée**,  
afin d'**unifier l'entrée de `chat` et `guidance` et de poser le pattern que `natal` suivra à la story 66.7**.

## Note d'architecture — décision de nommage (FIGÉE)

**Décision : Option A — Conservation du nom `AIEngineAdapter`.**

Justification : le blast radius d'un renommage dépasse le périmètre de cette story. Le module est refactorisé en couche applicative canonique ; son nom legacy est assumé jusqu'à un renommage dédié post-epic 66. Aucun alias, aucun wrapper supplémentaire.

**Engagement de traçabilité :** la première ligne du fichier `ai_engine_adapter.py` après refactorisation doit être :
```python
# CANONICAL LLM APPLICATION LAYER (nom legacy conservé post-epic-66 — renommage prévu)
# Rôle : construire LLMExecutionRequest, appeler gateway.execute_request(), mapper les erreurs.
# Renommage futur : LLMApplicationLayer ou équivalent — story dédiée à créer.
```

**Ce commentaire est obligatoire et non négociable.** Il empêche tout futur développeur de traiter ce module comme un simple "adapter technique" et d'y injecter de la logique de plateforme en dehors de son rôle défini.

## Acceptance Criteria

1. [x] **Given** que `generate_chat_reply()` construit aujourd'hui un payload dict  
   **When** la couche est refactorisée  
   **Then** elle construit un `LLMExecutionRequest` typé (story 66.1) et appelle `gateway.execute_request(request, db)` — sans `dict` intermédiaire comme contrat principal

2. [x] **Given** que le comportement réel de `generate_chat_reply()` inclut plusieurs branches  
   **When** la refactorisation est appliquée  
   **Then** les comportements suivants sont **tous** préservés : `conversation_id` porté via `ExecutionUserInput.conversation_id`, détection `chat_turn_stage == "opening"` pour le premier tour (via `ExecutionFlags` ou `extra_context` documenté), test fallback non-production via le générateur de test injecté, mapping précis de chaque type d'erreur

3. [x] **Given** que le mapping d'erreurs couvre plusieurs sous-types  
   **When** le refactoring est appliqué  
   **Then** le mapping suivant est **intégralement** préservé : `UpstreamRateLimitError → 429`, `ContextTooLargeError → 400`, `UpstreamTimeoutError → 504`, `PromptRenderError → 400`, `UnknownUseCaseError → 400`, `GatewayConfigError → 500`, `InputValidationError → 400`, `OutputValidationError → 422`, `GatewayError` générique → 500 ; autres `UpstreamXxx` → 502

4. [x] **Given** que `generate_guidance()` couvre plusieurs use cases  
   **When** la refactorisation est appliquée  
   **Then** `_build_guidance_request()` produit un `LLMExecutionRequest` correct pour les 3 use cases : `guidance_daily`, `guidance_weekly`, `guidance_contextual` — chacun avec ses champs spécifiques (notamment `time_horizon` pour contextual)

5. [x] **Given** que la couche applicative a une responsabilité documentée  
   **When** un développeur lit le module  
   **Then** le header du fichier déclare explicitement : rôle (construire `LLMExecutionRequest`, appeler `execute_request`, mapper les erreurs), non-rôle (validation de sortie, logique provider, logique métier profonde d'un domaine)

6. [x] **Given** que `natal` doit suivre ce pattern à la story 66.7  
   **When** le pattern canonical est établi  
   **Then** il est documenté en commentaire dans le module : "Nouveau use case : créer une méthode `generate_xxx()` qui construit `LLMExecutionRequest` depuis des inputs métier typés et appelle `gateway.execute_request()`"

7. [x] **Given** que `chat` et `guidance` fonctionnent aujourd'hui  
   **When** le refactoring est appliqué  
   **Then** leurs tests d'intégration et les tests de mapping d'erreurs passent sans régression

## Tasks / Subtasks

- [x] Ajouter un header de module et déclarer la responsabilité dans `backend/app/services/ai_engine_adapter.py` (AC: 5, 6)
  - [x] Bloc module-level docstring : rôle canonique, non-rôle, décision de nommage legacy, pattern pour nouveau use case
  - [x] Ne pas modifier de logique dans cette étape — documentation pure

- [x] Refactoriser `generate_chat_reply()` pour produire `LLMExecutionRequest` (AC: 1, 2)
  - [x] Importer `LLMExecutionRequest`, `ExecutionUserInput`, `ExecutionContext`, `ExecutionMessage`, `ExecutionFlags` depuis `llm_orchestration.models`
  - [x] Construire `ExecutionUserInput(use_case="chat_astrologer", locale=locale, message=messages[-1]["content"] if messages else "", conversation_id=conversation_id si présent)`
  - [x] Convertir `messages[:-1]` en `list[ExecutionMessage]` pour `ExecutionContext.history` via `[ExecutionMessage(role=m["role"], content=m["content"]) for m in messages[:-1]]`
  - [x] Pour la détection `chat_turn_stage == "opening"` : si `context.get("chat_turn_stage") == "opening"`, passer `ExecutionFlags(...)` avec une flag dédiée ou via `extra_context["chat_turn_stage"] = "opening"` (documenté comme transitoire)
  - [x] Appeler `gateway.execute_request(request=request, db=db)` au lieu de `gateway.execute(use_case=..., user_input=..., context=..., ...)`
  - [x] Conserver le bloc test fallback (`if self._test_generator: ...`) en tête de méthode, avant construction du request

- [x] Implémenter `_build_guidance_request()` en remplacement de `_build_guidance_gateway_payload()` (AC: 4)
  - [x] Signature : `@staticmethod def _build_guidance_request(use_case: str, context: dict, locale: str) -> LLMExecutionRequest`
  - [x] Pour `guidance_daily` et `guidance_weekly` : `ExecutionUserInput(use_case=use_case, locale=locale, question=context.get("question"), situation=context.get("situation"))`
  - [x] Pour `guidance_contextual` : ajouter `time_horizon` et `objective` dans `ExecutionContext.extra_context` (champs non encore formalisés dans les modèles canoniques — documenter comme transitoire)
  - [x] `ExecutionContext` : renseigner `extra_context` avec `{"context_lines": ..., "objective": ..., "time_horizon": ...}` si présents

- [x] Mettre à jour `generate_guidance()` pour utiliser `_build_guidance_request()` (AC: 4)
  - [x] Remplacer `user_input, ctx = _build_guidance_gateway_payload(...)` par `request = _build_guidance_request(...)`
  - [x] Appeler `gateway.execute_request(request=request, db=db)`

- [x] Auditer et compléter le mapping d'erreurs (AC: 3)
  - [x] Lister tous les types d'exceptions importés et catchés dans le module actuel
  - [x] Vérifier que `PromptRenderError`, `UnknownUseCaseError`, `GatewayConfigError`, `InputValidationError`, `OutputValidationError` sont tous mappés avec le bon code HTTP
  - [x] Si une exception est manquante : ajouter son import et son mapping
  - [x] Ne pas modifier la logique des mappings existants — seulement compléter les manquants

- [x] Créer `backend/app/services/tests/test_ai_engine_adapter_refacto.py` (AC: 7)
  - [x] Test : `generate_chat_reply()` construit un `LLMExecutionRequest` avec `ExecutionContext.history` typé (mock `execute_request`)
  - [x] Test : `generate_chat_reply()` avec `conversation_id` → `ExecutionUserInput.conversation_id` renseigné
  - [x] Test : test fallback non-production activé avant construction du request
  - [x] Test : `generate_guidance("guidance_daily", ...)` → `LLMExecutionRequest` avec `use_case = "guidance_daily"`
  - [x] Test : `generate_guidance("guidance_weekly", ...)` → use_case correct
  - [x] Test : `generate_guidance("guidance_contextual", ...)` → `time_horizon` dans `extra_context`
  - [x] Test mapping d'erreurs : `UpstreamRateLimitError` → 429 (comportement inchangé)
  - [x] Test mapping d'erreurs : `OutputValidationError` → 422
  - [x] Test non-régression — chemins sensibles obligatoires :
    - Premier tour chat `chat_turn_stage == "opening"` → request construit sans régression
    - `guidance_contextual` avec `time_horizon` → champ porté dans `extra_context`
    - `guidance_weekly` → `use_case = "guidance_weekly"` dans request
    - Fallback use case → mapping d'erreur préservé
    - Test generator non-production → activé avant construction request

- [x] Mettre à jour `docs/architecture/llm-processus-architecture.md` **avant merge**
  - [x] Documenter la décision de nommage Option A (AIEngineAdapter conservé, renommage futur prévu)
  - [x] Décrire le rôle canonique : construire `LLMExecutionRequest`, appeler `execute_request()`, mapper erreurs
  - [x] Décrire le pattern pour ajouter un nouveau use case (guide pour natal story 66.7 et futurs)
