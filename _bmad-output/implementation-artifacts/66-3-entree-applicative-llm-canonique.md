# Story 66.3 — Créer une entrée applicative LLM canonique

Status: draft

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

1. **Given** que `generate_chat_reply()` construit aujourd'hui un payload dict  
   **When** la couche est refactorisée  
   **Then** elle construit un `LLMExecutionRequest` typé (story 66.1) et appelle `gateway.execute_request(request, db)` — sans `dict` intermédiaire comme contrat principal

2. **Given** que le comportement réel de `generate_chat_reply()` inclut plusieurs branches  
   **When** la refactorisation est appliquée  
   **Then** les comportements suivants sont **tous** préservés : `conversation_id` porté via `ExecutionUserInput.conversation_id`, détection `chat_turn_stage == "opening"` pour le premier tour (via `ExecutionFlags` ou `extra_context` documenté), test fallback non-production via le générateur de test injecté, mapping précis de chaque type d'erreur

3. **Given** que le mapping d'erreurs couvre plusieurs sous-types  
   **When** le refactoring est appliqué  
   **Then** le mapping suivant est **intégralement** préservé : `UpstreamRateLimitError → 429`, `ContextTooLargeError → 400`, `UpstreamTimeoutError → 504`, `PromptRenderError → 400`, `UnknownUseCaseError → 400`, `GatewayConfigError → 500`, `InputValidationError → 400`, `OutputValidationError → 422`, `GatewayError` générique → 500 ; autres `UpstreamXxx` → 502

4. **Given** que `generate_guidance()` couvre plusieurs use cases  
   **When** la refactorisation est appliquée  
   **Then** `_build_guidance_request()` produit un `LLMExecutionRequest` correct pour les 3 use cases : `guidance_daily`, `guidance_weekly`, `guidance_contextual` — chacun avec ses champs spécifiques (notamment `time_horizon` pour contextual)

5. **Given** que la couche applicative a une responsabilité documentée  
   **When** un développeur lit le module  
   **Then** le header du fichier déclare explicitement : rôle (construire `LLMExecutionRequest`, appeler `execute_request`, mapper les erreurs), non-rôle (validation de sortie, logique provider, logique métier profonde d'un domaine)

6. **Given** que `natal` doit suivre ce pattern à la story 66.7  
   **When** le pattern canonical est établi  
   **Then** il est documenté en commentaire dans le module : "Nouveau use case : créer une méthode `generate_xxx()` qui construit `LLMExecutionRequest` depuis des inputs métier typés et appelle `gateway.execute_request()`"

7. **Given** que `chat` et `guidance` fonctionnent aujourd'hui  
   **When** le refactoring est appliqué  
   **Then** leurs tests d'intégration et les tests de mapping d'erreurs passent sans régression

## Tasks / Subtasks

- [ ] Ajouter un header de module et déclarer la responsabilité dans `backend/app/services/ai_engine_adapter.py` (AC: 5, 6)
  - [ ] Bloc module-level docstring : rôle canonique, non-rôle, décision de nommage legacy, pattern pour nouveau use case
  - [ ] Ne pas modifier de logique dans cette étape — documentation pure

- [ ] Refactoriser `generate_chat_reply()` pour produire `LLMExecutionRequest` (AC: 1, 2)
  - [ ] Importer `LLMExecutionRequest`, `ExecutionUserInput`, `ExecutionContext`, `ExecutionMessage`, `ExecutionFlags` depuis `llm_orchestration.models`
  - [ ] Construire `ExecutionUserInput(use_case="chat_astrologer", locale=locale, message=messages[-1]["content"] if messages else "", conversation_id=conversation_id si présent)`
  - [ ] Convertir `messages[:-1]` en `list[ExecutionMessage]` pour `ExecutionContext.history` via `[ExecutionMessage(role=m["role"], content=m["content"]) for m in messages[:-1]]`
  - [ ] Pour la détection `chat_turn_stage == "opening"` : si `context.get("chat_turn_stage") == "opening"`, passer `ExecutionFlags(...)` avec une flag dédiée ou via `extra_context["chat_turn_stage"] = "opening"` (documenté comme transitoire)
  - [ ] Appeler `gateway.execute_request(request=request, db=db)` au lieu de `gateway.execute(use_case=..., user_input=..., context=..., ...)`
  - [ ] Conserver le bloc test fallback (`if self._test_generator: ...`) en tête de méthode, avant construction du request

- [ ] Implémenter `_build_guidance_request()` en remplacement de `_build_guidance_gateway_payload()` (AC: 4)
  - [ ] Signature : `@staticmethod def _build_guidance_request(use_case: str, context: dict, locale: str) -> LLMExecutionRequest`
  - [ ] Pour `guidance_daily` et `guidance_weekly` : `ExecutionUserInput(use_case=use_case, locale=locale, question=context.get("question"), situation=context.get("situation"))`
  - [ ] Pour `guidance_contextual` : ajouter `time_horizon` et `objective` dans `ExecutionContext.extra_context` (champs non encore formalisés dans les modèles canoniques — documenter comme transitoire)
  - [ ] `ExecutionContext` : renseigner `extra_context` avec `{"context_lines": ..., "objective": ..., "time_horizon": ...}` si présents

- [ ] Mettre à jour `generate_guidance()` pour utiliser `_build_guidance_request()` (AC: 4)
  - [ ] Remplacer `user_input, ctx = _build_guidance_gateway_payload(...)` par `request = _build_guidance_request(...)`
  - [ ] Appeler `gateway.execute_request(request=request, db=db)`

- [ ] Auditer et compléter le mapping d'erreurs (AC: 3)
  - [ ] Lister tous les types d'exceptions importés et catchés dans le module actuel
  - [ ] Vérifier que `PromptRenderError`, `UnknownUseCaseError`, `GatewayConfigError`, `InputValidationError`, `OutputValidationError` sont tous mappés avec le bon code HTTP
  - [ ] Si une exception est manquante : ajouter son import et son mapping
  - [ ] Ne pas modifier la logique des mappings existants — seulement compléter les manquants

- [ ] Créer `backend/app/services/tests/test_ai_engine_adapter_refacto.py` (AC: 7)
  - [ ] Test : `generate_chat_reply()` construit un `LLMExecutionRequest` avec `ExecutionContext.history` typé (mock `execute_request`)
  - [ ] Test : `generate_chat_reply()` avec `conversation_id` → `ExecutionUserInput.conversation_id` renseigné
  - [ ] Test : test fallback non-production activé avant construction du request
  - [ ] Test : `generate_guidance("guidance_daily", ...)` → `LLMExecutionRequest` avec `use_case = "guidance_daily"`
  - [ ] Test : `generate_guidance("guidance_weekly", ...)` → use_case correct
  - [ ] Test : `generate_guidance("guidance_contextual", ...)` → `time_horizon` dans `extra_context`
  - [ ] Test mapping d'erreurs : `UpstreamRateLimitError` → 429 (comportement inchangé)
  - [ ] Test mapping d'erreurs : `OutputValidationError` → 422
  - [ ] Test non-régression — chemins sensibles obligatoires :
    - Premier tour chat `chat_turn_stage == "opening"` → request construit sans régression
    - `guidance_contextual` avec `time_horizon` → champ porté dans `extra_context`
    - `guidance_weekly` → `use_case = "guidance_weekly"` dans request
    - Fallback use case → mapping d'erreur préservé
    - Test generator non-production → activé avant construction request

- [ ] Mettre à jour `docs/architecture/llm-processus-architecture.md` **avant merge**
  - [ ] Documenter la décision de nommage Option A (AIEngineAdapter conservé, renommage futur prévu)
  - [ ] Décrire le rôle canonique : construire `LLMExecutionRequest`, appeler `execute_request()`, mapper erreurs
  - [ ] Décrire le pattern pour ajouter un nouveau use case (guide pour natal story 66.7 et futurs)

### File List

- `backend/app/services/ai_engine_adapter.py` — ajout header canonique, refactorisation de `generate_chat_reply()`, `generate_guidance()`, `_build_guidance_gateway_payload()` → `_build_guidance_request()`
- `docs/architecture/llm-processus-architecture.md` — mise à jour obligatoire avant merge

### Contexte architectural

- **`generate_chat_reply()` actuelle** : ligne ~432 — construit `user_input` et `context` dicts, appelle `LLMGateway.execute(use_case="chat_astrologer", ...)`. Le test generator (lignes ~435-440) doit rester en garde en tête
- **`chat_turn_stage == "opening"`** : logique spéciale premier tour chat — actuellement dans `context`. La flag `chat_turn_stage` doit transiter via `ExecutionContext.extra_context["chat_turn_stage"]` pour cette story (transitoire — à formaliser dans un futur modèle si le comportement se stabilise)
- **`_build_guidance_gateway_payload()` actuelle** : retourne un tuple `(user_input_dict, context_dict)`. Remplacée par `_build_guidance_request()` qui retourne `LLMExecutionRequest`. L'ancienne méthode peut être supprimée après remplacement
- **Mapping d'erreurs actuel** : lignes ~480-590 — blocs try/except sur les sous-classes de `GatewayError` et `UpstreamXxx`. Identifier exactement quels types sont catchés pour ne rien oublier lors du mapping complet. Vérifier la présence de `PromptRenderError`, `UnknownUseCaseError`, `GatewayConfigError`, `InputValidationError`, `OutputValidationError`
- **`ProviderNotConfiguredError` fallback non-prod** : si ce type est levé en non-production, l'adapter retourne un résultat mock — conserver ce comportement intact
- **`estimate_tokens()`** : méthode utilitaire statique — ne pas toucher
- **Pattern pour natal** : `generate_natal_interpretation()` sera ajouté à la story 66.7 en suivant exactement le même patron que `generate_chat_reply()` et `generate_guidance()`

### Sécurité critique

- Le mapping `OutputValidationError → 422` ne doit pas exposer les détails d'erreur internes dans le message HTTP — vérifier que le message remonté est générique

### Project Structure Notes

- Tests dans `backend/app/services/tests/` — vérifier existence du dossier, créer `__init__.py` si absent
- `_build_guidance_gateway_payload()` peut être supprimée une fois `_build_guidance_request()` utilisée — ne pas garder les deux en doublon

### References

- `generate_chat_reply()` : `backend/app/services/ai_engine_adapter.py` ligne ~432
- `generate_guidance()` : ligne ~590
- `_build_guidance_gateway_payload()` : ligne ~620 approx
- Mapping erreurs : lignes ~480-590
- `ProviderNotConfiguredError` fallback : chercher dans le module
- Epic 66 FR66-3, FR66-10, NFR66-1, NFR66-4 : `_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md`
- Story 66.1 (LLMExecutionRequest, ExecutionMessage) : `_bmad-output/implementation-artifacts/66-1-llm-execution-request.md`

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List
