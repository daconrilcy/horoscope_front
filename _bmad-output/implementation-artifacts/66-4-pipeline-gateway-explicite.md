# Story 66.4 — Refactoriser `LLMGateway.execute_request()` en pipeline d'étapes explicites

Status: draft

## Story

En tant que **développeur backend**,  
je veux **que `execute_request()` orchestre des étapes nommées aux responsabilités claires**,  
afin de **réduire l'effet "god orchestrator" et rendre chaque étape indépendamment testable**.

## Acceptance Criteria

1. **Given** que `execute_request()` doit être lisible  
   **When** le refactoring est appliqué  
   **Then** son corps orchestre explicitement 6 étapes nommées dans l'ordre : `_resolve_plan()` (story 66.2), `_build_messages()`, `_call_provider()`, `_validate_and_normalize()`, `_handle_repair_or_fallback()` si nécessaire, `_build_result()` — et chaque étape a une signature avec types explicites

2. **Given** que l'anti-loop check est une logique de sécurité de contrôle de flux  
   **When** le découpage est appliqué  
   **Then** la vérification `visited_use_cases` reste au début de `execute_request()` **avant** `_resolve_plan()` — elle n'est pas dans `_build_messages()`

3. **Given** que `_build_messages()` compose les messages LLM  
   **When** elle retourne son résultat  
   **Then** elle retourne `list[dict[str, str]]` — format attendu par `ResponsesClient.execute()`. Un type `ComposedMessages = list[dict[str, str]]` peut être défini comme alias pour la lisibilité

4. **Given** que `_build_result()` doit construire des métadonnées fiables  
   **When** sa signature est définie  
   **Then** elle reçoit : `provider_result: GatewayResult`, `validation_result: ValidationResult`, `plan: ResolvedExecutionPlan`, `context_quality: str`, `repair_attempts: int`, `fallback_reason: Optional[str]`, `latency_ms: int` — toutes les informations nécessaires à `GatewayMeta` sans dépendre de variables latérales

5. **Given** que `_handle_repair_or_fallback()` modifie les compteurs et traces  
   **When** elle est exécutée  
   **Then** elle retourne un `RecoveryResult` typé contenant `result: GatewayResult`, `repair_attempts: int`, `fallback_reason: Optional[str]` — un objet nommé plutôt qu'un tuple positionnel, pour rester cohérent avec la logique de contrats forts de l'epic

6. **Given** que la logique fonctionnelle est conservée  
   **When** les parcours `natal`, `chat`, `guidance` sont exécutés après refactoring  
   **Then** : `structured_output` identique, comportement de repair et fallback inchangé, champs `GatewayMeta` historiques (`latency_ms`, `model`, `validation_status`, `repair_attempted`, `fallback_triggered`, `validation_errors`) conservés avec les mêmes valeurs

7. **Given** qu'une étape échoue  
   **When** l'exception est propagée  
   **Then** le log structuré identifie l'étape fautive via un champ `"gateway_step": "nom_etape"` sans exposer le contenu des messages ou du prompt

8. **Given** que les étapes sont testables unitairement  
   **When** les tests sont exécutés  
   **Then** chaque méthode extraite est mockable indépendamment, et le suite d'intégration existante passe sans régression

## Tasks / Subtasks

- [ ] Ajouter l'anti-loop check en tête de `execute_request()` dans `backend/app/llm_orchestration/gateway.py` (AC: 2)
  - [ ] Extraire `visited_use_cases = request.flags.visited_use_cases` (depuis story 66.1)
  - [ ] Si `use_case in visited_use_cases` : lever `GatewayLoopError` ou retourner un result d'erreur selon la politique actuelle (lignes ~693-699 — conserver le comportement)

- [ ] Extraire `_build_messages()` depuis `execute()` (AC: 1, 3)
  - [ ] Signature : `def _build_messages(self, request: LLMExecutionRequest, plan: ResolvedExecutionPlan) -> list[dict[str, str]]`
  - [ ] Contenu : validation de la `user_question_policy` (depuis `plan`, pas de `context["..."]`), construction payload via `build_user_payload()`, puis `compose_chat_messages()` ou `compose_structured_messages()` selon `plan.interaction_mode`
  - [ ] Pour `chat_turn_stage == "opening"` : lire depuis `request.context.extra_context.get("chat_turn_stage")` (transitoire story 66.3)
  - [ ] Retourne `list[dict[str, str]]` — alias `ComposedMessages` optionnel pour lisibilité

- [ ] Extraire `_call_provider()` (AC: 1)
  - [ ] Signature : `async def _call_provider(self, messages: list[dict[str, str]], plan: ResolvedExecutionPlan, request: LLMExecutionRequest) -> GatewayResult`
  - [ ] Contenu : `await self.client.execute(messages=messages, model=plan.model_id, temperature=plan.temperature, max_output_tokens=plan.max_output_tokens, reasoning_effort=plan.reasoning_effort, response_format=plan.response_format.model_dump() if plan.response_format else None, request_id=request.request_id, trace_id=request.trace_id, use_case=request.user_input.use_case)`

- [ ] Extraire `_validate_and_normalize()` (AC: 1)
  - [ ] Signature : `def _validate_and_normalize(self, raw_output: str, plan: ResolvedExecutionPlan) -> ValidationResult`
  - [ ] Contenu : `validate_output(raw_output=raw_output, json_schema=plan.output_schema, evidence_catalog=..., strict=..., use_case=request.user_input.use_case, schema_version=plan.output_schema_version)`
  - [ ] `evidence_catalog` et `strict` : depuis `request.flags.evidence_catalog` et `request.flags.validation_strict`

- [ ] Créer `RecoveryResult` dans `backend/app/llm_orchestration/models.py` (AC: 5)
  - [ ] Définir : `result: GatewayResult`, `repair_attempts: int = 0`, `fallback_reason: Optional[str] = None`

- [ ] Extraire `_handle_repair_or_fallback()` depuis `_handle_validation()` (AC: 5)
  - [ ] Signature : `async def _handle_repair_or_fallback(self, validation_result: ValidationResult, request: LLMExecutionRequest, plan: ResolvedExecutionPlan, messages: list[dict]) -> RecoveryResult`
  - [ ] Retourne : `RecoveryResult(result=..., repair_attempts=..., fallback_reason=...)`
  - [ ] Logique repair : si `not validation_result.valid and not request.flags.is_repair_call` → appel récursif `execute_request()` avec `request.flags.is_repair_call = True` et `visited_use_cases` mis à jour ; incrémenter `repair_attempts`
  - [ ] Logique fallback : si repair échoue et fallback config existe → `execute_request()` avec use_case de fallback ; `fallback_reason = validation_result.errors[0]` ou équivalent
  - [ ] Si tout échoue : lever `OutputValidationError`

- [ ] Implémenter `_build_result()` avec signature complète (AC: 4, 6)
  - [ ] Signature : `def _build_result(self, provider_result: GatewayResult, validation_result: ValidationResult, plan: ResolvedExecutionPlan, recovery: RecoveryResult, context_quality: str, latency_ms: int) -> GatewayResult`
  - [ ] Construire `GatewayMeta` avec : champs historiques inchangés (`latency_ms`, `model=plan.model_id`, `persona_id=plan.persona_id`, `validation_status`, `repair_attempted=repair_attempts > 0`, `fallback_triggered=fallback_reason is not None`, `output_schema_id=plan.output_schema_id`, `schema_version=plan.output_schema_version`) + nouveaux champs story 66.6 initialisés à défaut
  - [ ] `execution_path` calculé : `"repaired"` si `repair_attempts > 0`, `"fallback_use_case"` si `fallback_reason`, `"nominal"` sinon — pas de `"degraded_context"` (story 66.6 le gère)

- [ ] Refactoriser `execute_request()` comme orchestrateur des 6 étapes (AC: 1, 7)
  - [ ] Corps : 1) anti-loop check, 2) `plan = await _resolve_plan()`, 3) log start + `plan.to_log_dict()`, 4) `messages = _build_messages()`, 5) `provider_result = await _call_provider()`, 6) `validation = _validate_and_normalize()`, 7) si `not validation.valid` : `recovery = await _handle_repair_or_fallback()`, sinon : `recovery = RecoveryResult(result=provider_result)` ; 8) `return _build_result(provider_result, validation, plan, recovery, context_quality, latency_ms)`
  - [ ] Chaque appel d'étape dans un bloc try/except loguant `"gateway_step": "nom"` sans exposer le contenu prompt

- [ ] Créer `backend/app/llm_orchestration/tests/test_gateway_pipeline.py` (AC: 8)
  - [ ] Test : `_build_messages()` mode `"chat"` retourne messages avec historique (mock plan avec `interaction_mode="chat"`)
  - [ ] Test : `_build_messages()` mode `"structured"` retourne messages sans historique
  - [ ] Test : `_call_provider()` passe `plan.model_id` et `plan.temperature` à `client.execute()` (mock client)
  - [ ] Test : `_validate_and_normalize()` appelle `validate_output()` avec `plan.output_schema_version` (mock)
  - [ ] Test : `_handle_repair_or_fallback()` retourne `(result, 1, None)` après un repair réussi
  - [ ] Test : `_build_result()` avec `repair_attempts=1` → `repair_attempted=True` dans `GatewayMeta`
  - [ ] Test : `_build_result()` avec `fallback_reason="..."` → `fallback_triggered=True`
  - [ ] Test non-régression — chemins sensibles obligatoires :
    - Fallback use case (repair échoue + fallback config) → `recovery.fallback_reason` renseigné
    - Repair success (1 repair puis valid) → `recovery.repair_attempts = 1`, `execution_path = "repaired"`
    - Common context partial → `context_quality = "partial"` dans `GatewayMeta`

- [ ] Mettre à jour `docs/architecture/llm-processus-architecture.md` **avant merge**
  - [ ] Documenter le pipeline en 6 étapes (noms, signatures, responsabilités)
  - [ ] Documenter `RecoveryResult` et son rôle entre `_handle_repair_or_fallback()` et `_build_result()`
  - [ ] Mettre à jour le diagramme de flux si présent

### File List

- `backend/app/llm_orchestration/models.py` — ajout de `RecoveryResult`
- `backend/app/llm_orchestration/gateway.py` — extraction de `_build_messages()`, `_call_provider()`, `_validate_and_normalize()`, `_handle_repair_or_fallback()`, `_build_result()` ; refactorisation de `execute_request()` ; `_handle_validation()` remplacée
- `docs/architecture/llm-processus-architecture.md` — mise à jour obligatoire avant merge

### Contexte architectural

- **Ordre des étapes actuel dans `execute()`** : les 12 étapes se consolident en 6 méthodes — anti-loop et log sont des préambules de `execute_request()`, le reste est délégué aux méthodes
- **`_handle_validation()` actuelle** : lignes 533-656 — mélange validation + repair recursif + fallback. La décomposer en `_validate_and_normalize()` (validation pure, délègue à `output_validator.py`) + `_handle_repair_or_fallback()` (logique de récupération)
- **Repair récursif** : `_handle_validation()` appelle `await self.execute(use_case=..., is_repair_call=True, ...)` avec un contexte enrichi (prompt repair). Dans `_handle_repair_or_fallback()`, construire la `LLMExecutionRequest` repair avec `flags.is_repair_call = True` et `flags.visited_use_cases` mis à jour pour inclure le use_case courant
- **`compose_chat_messages()` et `compose_structured_messages()`** : méthodes existantes lignes 237-282 — `_build_messages()` les appelle selon `plan.interaction_mode`
- **`build_user_payload()`** : méthode existante lignes 184-235 — appelée dans `_build_messages()` avec `plan.user_question_policy` et le message de `request.user_input`
- **`response_format`** dans `_call_provider()` : `plan.response_format.model_dump() if plan.response_format else None` — le client attend un dict OpenAI compatible

### Sécurité critique

- Les blocs try/except avec `"gateway_step"` ne doivent jamais logguer `plan.rendered_developer_prompt`, `plan.persona_block` ni le contenu des `messages` — seulement le nom de l'étape et le type d'exception

### Project Structure Notes

- `_handle_validation()` peut être supprimée une fois les deux nouvelles méthodes en place et validées
- `ComposedMessages = list[dict[str, str]]` : alias type optionnel en tête de `gateway.py` pour lisibilité

### References

- `execute()` : `backend/app/llm_orchestration/gateway.py` ligne ~674
- `_handle_validation()` : lignes 533-656
- `compose_chat_messages()` : lignes 237-264
- `compose_structured_messages()` : lignes 266-282
- `build_user_payload()` : lignes 184-235
- Anti-loop : lignes ~693-699
- Epic 66 FR66-5, NFR66-2, NFR66-4 : `_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md`
- Story 66.2 (ResolvedExecutionPlan) : `_bmad-output/implementation-artifacts/66-2-resolved-execution-plan.md`

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List
