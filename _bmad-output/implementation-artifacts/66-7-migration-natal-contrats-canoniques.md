# Story 66.7 — Migrer le parcours natal vers l'entrée applicative canonique

Status: done

## Story

En tant que **domaine natal**,  
je veux **entrer dans la plateforme LLM via la couche applicative canonique avec un contrat typé explicite**,  
afin de **supprimer la construction manuelle de payloads complexes dans le service métier et bénéficier de la validation et du suivi unifiés**.

## Note d'architecture — responsabilité du contrat

Le contrat `NatalExecutionInput` est le point de vérité pour les entrées du domaine natal. Il est construit par `NatalInterpretationServiceV2` et consommé par `AIEngineAdapter.generate_natal_interpretation()`. Ce dernier transforme ce contrat métier en `LLMExecutionRequest` plateforme.

## Acceptance Criteria

1. [x] **Given** que `NatalInterpretationServiceV2` appelle aujourd'hui `gateway.execute()`  
   **When** la migration est effectuée  
   **Then** il appelle exclusivement `AIEngineAdapter.generate_natal_interpretation(natal_input, db)` — la dépendance directe au gateway est supprimée du service métier

2. [x] **Given** que les entrées natales sont riches et variées  
   **When** le contrat est défini  
   **Then** `NatalExecutionInput` inclut explicitement : `use_case_key`, `level` (short/complete), `chart_json`, `natal_data` (dict), `evidence_catalog`, `persona_id`, `validation_strict`, `module`, `variant_code`, et les identifiants de runtime (`user_id`, `request_id`, `trace_id`)

3. [x] **Given** que la résolution du persona est aujourd'hui manuelle dans le service natal  
   **When** la migration est effectuée  
   **Then** cette logique est supprimée du service métier — le persona est simplement passé par ID dans le contrat, et sa résolution (nom, prompt) est déléguée à la plateforme via le gateway (Stage 1)

4. [x] **Given** que le socle de contexte est désormais géré par la plateforme  
   **When** le contrat est rempli  
   **Then** le service natal ne transmet que les champs **spécifiques** au domaine (données du thème) — les champs communs (`today_date`, `astrologer_profile`, etc.) sont injectés par le builder de contexte de la plateforme

5. [x] **Given** que le parcours "Free Short" est un cas particulier (prompt `natal_long_free`)  
   **When** il est exécuté  
   **Then** il passe également par l'adapter canonique avec son propre `NatalExecutionInput` configuré pour ce use case spécifique

6. [x] **Given** que le résultat doit être persisté en DB  
   **When** la réponse revient de l'adapter  
   **Then** le service métier utilise les métadonnées enrichies de `GatewayMeta` (story 66.6) pour remplir les champs `was_fallback`, `prompt_version_id`, et `execution_path` dans la table `user_natal_interpretations`

7. [x] **Given** que les tests couvrent le parcours natal  
   **When** ils sont exécutés  
   **Then** les tests d'intégration `natal` (interprétation complète, short, modules thématiques, free short) passent sans régression via l'entrée canonique

## Tasks / Subtasks

- [x] Définir `NatalExecutionInput` dans `backend/app/llm_orchestration/models.py` (AC: 2)
  - [x] Champs : `use_case_key: str`, `locale: str`, `level: Literal["short", "complete"]`, `chart_json: str`, `natal_data: dict`, `evidence_catalog: list | dict`, `persona_id: Optional[str]`, `validation_strict: bool`, `question: Optional[str]`, `astro_context: Optional[str]`, `module: Optional[str]`, `variant_code: Optional[str]`
  - [x] Champs runtime : `user_id: int`, `request_id: str`, `trace_id: str`

- [x] Implémenter `generate_natal_interpretation()` dans `backend/app/services/ai_engine_adapter.py` (AC: 1, 3, 4, 5)
  - [x] Signature : `async def generate_natal_interpretation(cls, natal_input: NatalExecutionInput, db: Session) -> GatewayResult`
  - [x] Construire `LLMExecutionRequest` (Story 66.1) à partir de `natal_input`
  - [x] Remplir `ExecutionContext` avec les données natales brutes
  - [x] Remplir `ExecutionFlags` avec `validation_strict` et `evidence_catalog`
  - [x] Appeler `gateway.execute_request(request, db)`
  - [x] Mapper les erreurs via `_handle_gateway_error` (Stage 3 de la Story 66.3)

- [x] Refactoriser `NatalInterpretationServiceV2.interpret()` (AC: 1, 3, 4, 6)
  - [x] Supprimer la résolution manuelle du persona (AC: 3)
  - [x] Supprimer la construction manuelle du payload gateway (AC: 4)
  - [x] Construire `NatalExecutionInput`
  - [x] Appeler `AIEngineAdapter.generate_natal_interpretation()`
  - [x] Mettre à jour la persistence DB pour utiliser `gateway_result.meta.prompt_version_id` et `was_fallback` synchronisé avec `execution_path`

- [x] Refactoriser `NatalInterpretationServiceV2._generate_free_short()` (AC: 5)
  - [x] Supprimer l'appel direct au gateway
  - [x] Utiliser l'adapter avec `use_case_key="natal_long_free"`

- [x] Supprimer les helpers obsolètes de persona dans `natal_interpretation_service_v2.py` (AC: 3)
  - [x] `_build_persona_prompt_profile`
  - [x] `_normalize_persona_field`

- [x] Créer `backend/app/services/tests/test_natal_interpretation_service_v2_refacto.py` (AC: 7)
  - [x] Test : `interpret()` (complete) passe par l'adapter et construit le bon `NatalExecutionInput`
  - [x] Test : `_generate_free_short()` passe par l'adapter avec `natal_long_free`
  - [x] Test non-régression : mapping des erreurs natal (429, 504, 422) préservé via l'adapter

- [x] Mettre à jour `docs/architecture/llm-processus-architecture.md` **avant merge**
  - [x] Ajouter le parcours Natal au diagramme Mermaid (via `AIEngineAdapter`)
  - [x] Documenter le contrat `NatalExecutionInput`
