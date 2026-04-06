# Story 66.2 — Introduire un `ResolvedExecutionPlan`

Status: done

## Story

En tant que **moteur d'orchestration**,  
je veux **matérialiser la configuration finale réellement résolue avant l'appel provider**,  
afin d'**avoir un objet unique transportant toutes les décisions (modèle, prompts, schémas, stratégie) et facilitant la journalisation structurée**.

## Acceptance Criteria

1. [x] **Given** qu'une requête d'exécution est en cours  
   **When** la phase de résolution est terminée  
   **Then** tous les artefacts (developer prompt rendu, system core, persona, output schema, paramètres provider) sont regroupés dans un objet `ResolvedExecutionPlan`

2. [x] **Given** que l'origine du modèle est cruciale pour le débogage  
   **When** le plan est résolu  
   **Then** il contient un champ `model_source` valant soit : `"os_granular"` (env var spécifique), `"os_legacy"` (env var globale legacy), `"config"` (issu de PromptRegistryV2 / DB), `"stub"` (issu des dictionnaires codés en dur)

3. [x] **Given** qu'OpenAI exige une structure spécifique pour `response_format`  
   **When** le plan est construit  
   **Then** il contient un sous-objet `ResponseFormatConfig` encapsulant la logique `json_schema` vs `text`

4. [x] **Given** que les logs de plan sont ingérés par des outils d'analyse  
   **When** `plan.to_log_dict()` est appelé  
   **Then** il retourne une version filtrée du plan **excluant** les contenus volumineux (le prompt rendu, le bloc persona complet, le schéma JSON brut) pour ne garder que les métadonnées et identifiants

5. [x] **Given** que le gateway doit exécuter l'appel  
   **When** il appelle le provider  
   **Then** il utilise **exclusivement** les valeurs portées par le `ResolvedExecutionPlan` — aucune résolution de logique ne doit avoir lieu au moment de l'appel client

6. [x] **Given** que le gateway expose `execute_request()`  
   **When** cette méthode est appelée  
   **Then** la première étape est l'appel à `_resolve_plan(request, db) -> ResolvedExecutionPlan`, suivie de l'utilisation de ce plan pour la suite du pipeline

## Tasks / Subtasks

- [x] Créer `ResponseFormatConfig` dans `backend/app/llm_orchestration/models.py` (AC: 3)
  - [x] Champs : `type: Literal["json_schema", "text"]`, `schema_dict: Optional[dict[str, Any]]` (aliasé `"schema"`)

- [x] Créer `ResolvedExecutionPlan` dans `backend/app/llm_orchestration/models.py` (AC: 1, 2, 4)
  - [x] Bloc Model resolution : `model_id: str`, `model_source: Literal["os_granular", "os_legacy", "config", "stub"]`
  - [x] Bloc Prompts/Persona : `rendered_developer_prompt: str`, `system_core: str`, `persona_id: Optional[str]`, `persona_block: Optional[str]`
  - [x] Bloc Schemas : `output_schema_id: Optional[str]`, `output_schema: Optional[dict[str, Any]]`, `output_schema_version: str = "v1"`
  - [x] Bloc Strategy : `interaction_mode`, `user_question_policy`, `overrides_applied: dict[str, Any]` (les champs effectivement surchargés par `ExecutionOverrides`)
  - [x] Bloc Provider params : `temperature`, `max_output_tokens`, `response_format: Optional[ResponseFormatConfig]`, `reasoning_effort`, `verbosity`
  - [x] Implémenter `to_log_dict()` : exclusion des champs `rendered_developer_prompt`, `persona_block`, `system_core`, `output_schema`

- [x] Implémenter `_resolve_plan()` dans `backend/app/llm_orchestration/gateway.py` (AC: 1, 2, 6)
  - [x] Signature : `async def _resolve_plan(self, request: LLMExecutionRequest, db: Optional[Session]) -> ResolvedExecutionPlan`
  - [x] Étape 1 — résolution config : `config = await self._resolve_config(db, request.user_input.use_case, ...)`, déduire `model_source` depuis la branche empruntée (AC: 2)
  - [x] Étape 2 — résolution persona : `persona_block, persona_id = await self._resolve_persona(db, config, ...)`
  - [x] Étape 3 — résolution schéma : `schema_dict, _, schema_version = self._resolve_schema(db, config, ...)`
  - [x] Étape 4 — rendu prompt : appel `self.renderer.render(...)` avec les variables de `request.user_input` et `request.context`
  - [x] Étape 5 — application overrides : si `request.overrides`, injecter les valeurs dans le plan et remplir `overrides_applied`
  - [x] Centraliser le log `logger.info("llm_resolved_plan %s", plan.to_log_dict())`

- [x] Réfracter `execute_request()` pour utiliser le plan (AC: 5, 6)
  - [x] Appeler `plan = await self._resolve_plan(request, db)`
  - [x] Utiliser `plan.model_id`, `plan.temperature`, `plan.max_output_tokens`, `plan.response_format`, `plan.reasoning_effort`, `plan.verbosity` dans l'appel `self.client.execute()`
  - [x] Utiliser `plan.system_core`, `plan.rendered_developer_prompt`, `plan.persona_block` dans la composition des messages
  - [x] Utiliser les métadonnées du plan (`output_schema_id`, `output_schema_version`) pour finaliser `result.meta`

- [x] Créer `backend/app/llm_orchestration/tests/test_resolved_execution_plan.py` (AC: 1, 2, 4)
  - [x] Test : résolution d'un plan complet pour `natal_long_free`
  - [x] Test : détection correcte de `model_source` quand une env var OS est présente
  - [x] Test : `to_log_dict()` ne contient pas les champs volumineux
  - [x] Test : `overrides_applied` est correctement rempli si `ExecutionOverrides` est utilisé
  - [x] Test non-régression : les paramètres passés à `client.execute` sont strictement ceux du plan
