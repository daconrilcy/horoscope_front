# Story 66.4 — Refactoriser `LLMGateway.execute_request()` en pipeline d'étapes explicites

Status: done

## Story

En tant que **développeur backend**,  
je veux **que `execute_request()` orchestre des étapes nommées aux responsabilités uniques**,  
afin de **rendre le flux d'orchestration lisible, extensible et facile à debugger**.

## Architecture du Pipeline (6 étapes)

Le nouveau flux `execute_request` doit suivre strictement cet enchaînement :

1.  **Stage 1: Resolve Plan** (`_resolve_plan`) — Résolution de la config, du modèle, des prompts et du persona.
2.  **Stage 2: Build Messages** (`_build_messages`) — Composition des couches 1 à 4 (System, Developer, Persona, History, User).
3.  **Stage 3: Call Provider** (`_call_provider`) — Exécution de l'appel technique vers l'AI Client.
4.  **Stage 4: Validate & Normalize** (`_validate_and_normalize`) — Validation du format de sortie et parsing JSON.
5.  **Stage 5: Recovery (Repair/Fallback)** (`_handle_repair_or_fallback`) — Gestion récursive des erreurs de validation.
6.  **Stage 6: Build Final Result** (`_build_result`) — Assemblage du résultat final et des métadonnées unifiées.

## Acceptance Criteria

1. [x] **Given** qu'une requête arrive dans `execute_request()`  
   **When** le pipeline s'exécute  
   **Then** chaque étape est isolée dans une méthode privée dédiée (`_stage_name`) respectant la signature et la responsabilité définie dans le plan d'architecture.

2. [x] **Given** que la sécurité est prioritaire  
   **When** l'exécution commence  
   **Then** le check anti-boucle (circuit breaker sur `visited_use_cases`) est la toute première opération effectuée, avant même la résolution du plan.

3. [x] **Given** que la composition des messages est complexe  
   **When** `_build_messages` est appelé  
   **Then** il retourne un type aliasé `ComposedMessages = list[dict[str, Any]]` et encapsule toute la logique des "Layers" (1-4) ainsi que la gestion du `chat_turn_stage`.

4. [x] **Given** que le résultat doit être consistant  
   **When** `_build_result` finalise l'objet  
   **Then** il garantit que `GatewayMeta` contient toutes les informations de traçabilité (latence, modèle réel, IDs de schémas) et que les flags `repair_attempted` / `fallback_triggered` sont correctement positionnés.

5. [x] **Given** qu'une erreur de validation survient  
   **When** `_handle_repair_or_fallback` est sollicité  
   **Then** il orchestre soit un appel de réparation (is_repair_call=True), soit un basculement vers le `fallback_use_case`, en utilisant récursivement `execute_request` pour garantir la cohérence du pipeline.

6. [x] **Given** que le système doit rester monitorable  
   **When** une étape échoue  
   **Then** l'erreur est catchée, logguée avec le nom de l'étape fautive (ex: `gateway_step_failed:call_provider`), et les compteurs de performance sont mis à jour avant de propager l'exception.

## Tasks / Subtasks

- [x] Définir `RecoveryResult` dans `backend/app/llm_orchestration/models.py` (AC: 5)
  - [x] Champs : `result: GatewayResult`, `repair_attempts: int`, `fallback_reason: Optional[str]`

- [x] Extraire les étapes du pipeline dans `backend/app/llm_orchestration/gateway.py` (AC: 1, 3)
  - [x] Créer `ComposedMessages` type alias
  - [x] Implémenter `_build_messages(request, plan) -> ComposedMessages`
  - [x] Implémenter `_call_provider(messages, plan, request) -> GatewayResult`
  - [x] Implémenter `_validate_and_normalize(raw_output, plan, request) -> ValidationResult`
  - [x] Implémenter `_handle_repair_or_fallback(validation, request, plan, provider_result, db) -> RecoveryResult`
  - [x] Implémenter `_build_result(provider_result, validation, plan, recovery, latency_ms) -> GatewayResult`

- [x] Refactoriser `execute_request()` pour orchestrer le pipeline (AC: 1, 2, 6)
  - [x] Déplacer le check anti-boucle au sommet de la méthode
  - [x] Enchaîner les 6 stages avec blocs `try/except` par étape pour un logging précis
  - [x] Mesurer la latence globale du pipeline
  - [x] Supprimer la méthode legacy `_handle_validation` (absorbée par les stages 4 et 5)

- [x] Créer `backend/app/llm_orchestration/tests/test_gateway_pipeline.py` (AC: 1, 4, 5)
  - [x] Test : flux nominal complet (Stage 1 -> 6) avec mocks des couches basses
  - [x] Test : déclenchement correct du Stage 5 (Repair) sur sortie invalide
  - [x] Test : protection anti-boucle immédiate
  - [x] Test : intégrité des métadonnées dans `_build_result`
  - [x] Test non-régression : preservation du comportement `chat_turn_stage == "opening"` via Stage 2

- [x] Mettre à jour `docs/architecture/llm-processus-architecture.md` **avant merge**
  - [x] Documenter les 6 étapes du pipeline d'orchestration
  - [x] Mettre à jour le diagramme Mermaid pour refléter les stages nommés
