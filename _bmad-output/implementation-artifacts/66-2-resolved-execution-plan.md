# Story 66.2 — Introduire un `ResolvedExecutionPlan`

Status: draft

## Story

En tant que **moteur d'orchestration**,  
je veux **matérialiser la configuration finale réellement résolue avant l'appel provider**,  
afin d'**avoir un artefact canonique unique, loggable et immuable qui porte tout ce dont le pipeline a besoin — sans recalcul dispersé après la phase de résolution**.

## Note d'architecture — frontière résolution vs composition

`ResolvedExecutionPlan` contient **uniquement des artefacts résolus et rendus** — jamais les messages finaux composés. La frontière est :

| Dans le plan ✅ | Hors du plan ❌ |
|---|---|
| `rendered_developer_prompt` (prompt rendu) | Messages OpenAI composés (`list[dict]`) |
| `system_core` (hard policy résolue) | Historique de conversation |
| `persona_block` (texte persona résolu) | Payload utilisateur final |
| `output_schema` (schéma résolu) | Layer composition (chat/structured) |

La composition des messages reste la responsabilité exclusive de `_build_messages()` (story 66.4). Si un artefact n'est pas un **résultat de résolution de config**, il n'appartient pas au plan.

## Note d'architecture — journalisation des overrides

Quand `ExecutionOverrides` est présent et non-None sur un champ, `to_log_dict()` doit exposer une clé `"overrides_applied": {"interaction_mode": "...", ...}` pour auditabilité. Cela permet de distinguer dans les logs un appel en config normale d'un appel avec surcharge explicite.

## Acceptance Criteria

1. **Given** que le gateway vient de résoudre use_case, modèle, prompt, persona, schéma et hard policy  
   **When** la phase de résolution est terminée  
   **Then** un `ResolvedExecutionPlan` est produit portant **tous** les artefacts résolus nécessaires au pipeline : `model_id`, `model_source`, `rendered_developer_prompt`, `system_core` (hard policy résolue), `persona_id`, `persona_block` (texte résolu), `output_schema_id`, `output_schema` (dict consommable), `output_schema_version`, `interaction_mode`, `user_question_policy`, `temperature`, `max_output_tokens`, `response_format` (objet typé), `reasoning_effort`, `verbosity`, `context_quality` (état du `QualifiedContext`, `"unknown"` acceptable pour cette story)

2. **Given** que plusieurs chemins de résolution de modèle existent  
   **When** `model_source` est évalué  
   **Then** il prend l'une des 4 valeurs : `"os_granular"` (override OS granulaire), `"os_legacy"` (override OS legacy), `"config"` (config DB résolue), `"stub"` (fallback USE_CASE_STUBS) — alignées strictement sur les 4 branches réelles de `_resolve_config()`

3. **Given** que `response_format` est un paramètre technique structurant pour certains modèles  
   **When** il est inclus dans le plan  
   **Then** il est de type `Optional[ResponseFormatConfig]` où `ResponseFormatConfig` est un Pydantic model avec `type: Literal["json_schema", "text"]` et `schema: Optional[dict] = None` — jamais `Optional[dict]` libre

4. **Given** que le plan est loggé avant l'appel provider  
   **When** `plan.to_log_dict()` est appelé  
   **Then** il retourne un dict JSON-sérialisable excluant : `rendered_developer_prompt`, `persona_block`, `system_core`, `output_schema` — ces artefacts verbeux ne figurent pas dans les logs opérationnels

5. **Given** que le gateway utilise le plan  
   **When** l'appel provider est effectué  
   **Then** toutes les valeurs viennent du plan — `model_id`, `temperature`, `max_output_tokens`, `reasoning_effort`, `response_format`, `output_schema_version` — sans recalcul dans `execute_request()` après `_resolve_plan()`

6. **Given** qu'un use case inconnu est demandé  
   **When** `_resolve_plan()` est exécutée  
   **Then** `model_source = "stub"` et le log expose cette information avec niveau `WARNING`

7. **Given** que les tests couvrent la résolution  
   **When** les tests sont exécutés  
   **Then** `_resolve_plan()` est testable unitairement avec mock DB, et les **4 valeurs** de `model_source` sont chacune couvertes par au moins un test

## Tasks / Subtasks

- [ ] Créer `ResponseFormatConfig` dans `backend/app/llm_orchestration/models.py` (AC: 3)
  - [ ] Définir : `type: Literal["json_schema", "text"] = "text"`, `schema: Optional[dict[str, Any]] = None`
  - [ ] Utilisé dans `ResolvedExecutionPlan` et dans l'appel `ResponsesClient.execute()`

- [ ] Créer `ResolvedExecutionPlan` dans `backend/app/llm_orchestration/models.py` (AC: 1, 2, 3, 4)
  - [ ] Champs modèle : `model_id: str`, `model_source: Literal["os_granular", "os_legacy", "config", "stub"]`
  - [ ] Champs prompt : `rendered_developer_prompt: str`, `system_core: str` (hard policy résolue)
  - [ ] Champs persona : `persona_id: Optional[str] = None`, `persona_block: Optional[str] = None`
  - [ ] Champs schéma : `output_schema_id: Optional[str] = None`, `output_schema: Optional[dict[str, Any]] = None`, `output_schema_version: str = "v1"`
  - [ ] Champs stratégie (résolus depuis config) : `interaction_mode: Literal["structured", "chat"]`, `user_question_policy: Literal["none", "optional", "required"]`
  - [ ] Champs provider : `temperature: float`, `max_output_tokens: int`, `response_format: Optional[ResponseFormatConfig] = None`, `reasoning_effort: Optional[str] = None`, `verbosity: Optional[str] = None`
  - [ ] Champs état : `context_quality: str = "unknown"` (mis à jour story 66.6)
  - [ ] Méthode `def to_log_dict(self) -> dict` : exclure `rendered_developer_prompt`, `persona_block`, `system_core`, `output_schema` ; inclure `"overrides_applied": {k: v for k, v in overrides.items() if v is not None}` si `overrides` était présent dans le request

- [ ] Implémenter `_resolve_plan()` dans `backend/app/llm_orchestration/gateway.py` (AC: 1, 2, 5, 6)
  - [ ] Signature : `async def _resolve_plan(self, request: LLMExecutionRequest, db: Optional[Session]) -> ResolvedExecutionPlan`
  - [ ] Étape 1 — résolution config : `config = await self._resolve_config(db, request.user_input.use_case, ...)`, déduire `model_source` depuis la branche empruntée
  - [ ] Étape 2 — hard policy : `system_core = get_hard_policy(config.safety_profile)` (lignes ~800-804)
  - [ ] Étape 3 — persona : `persona_block, persona_id = await self._resolve_persona(db, config, ...)` (lignes ~806-809)
  - [ ] Étape 4 — schéma : `output_schema, output_schema_id, output_schema_version = self._resolve_schema(db, config, ...)` (lignes ~491-532)
  - [ ] Étape 5 — rendu prompt : construire `render_vars` depuis `request.user_input` + `request.context` ; appeler `self.renderer.render(config.developer_prompt, render_vars, ...)` ; stocker dans `rendered_developer_prompt`
  - [ ] Étape 6 — `interaction_mode` et `user_question_policy` : depuis `config`, surchargés par `request.overrides` si présent et non `None`
  - [ ] Construire et retourner `ResolvedExecutionPlan` avec tous les champs
  - [ ] Logger `plan.to_log_dict()` après construction
  - [ ] Si `model_source = "stub"` : `logger.warning("ResolvedExecutionPlan: use_case fell back to stub", use_case=..., ...)`

- [ ] Modifier `execute_request()` pour utiliser `_resolve_plan()` (AC: 5)
  - [ ] `plan = await self._resolve_plan(request, db)` — remplace les appels dispersés à `_resolve_config()`, `_resolve_persona()`, `_resolve_schema()` au niveau de `execute()`
  - [ ] Passer `plan.model_id`, `plan.temperature`, `plan.max_output_tokens`, `plan.response_format`, `plan.reasoning_effort` à `_call_provider()` (story 66.4)
  - [ ] Passer `plan.output_schema`, `plan.output_schema_version`, `plan.output_schema_id` à `_validate_and_normalize()` (story 66.4)
  - [ ] Pour le repair : `_resolve_plan()` est court-circuité — le prompt repair est construit directement sans passer par le rendu template standard (comportement lignes ~770-779 préservé)

- [ ] Créer `backend/app/llm_orchestration/tests/test_resolved_execution_plan.py` (AC: 7)
  - [ ] Test `model_source = "config"` : mock DB retourne une config complète sans OS override
  - [ ] Test `model_source = "os_granular"` : mock DB retourne un OS granulaire override
  - [ ] Test `model_source = "os_legacy"` : mock DB retourne un OS legacy override
  - [ ] Test `model_source = "stub"` : mock DB soulève une exception ou retourne rien → fallback USE_CASE_STUBS
  - [ ] Test `to_log_dict()` : n'expose pas `rendered_developer_prompt`, `persona_block`, `system_core`, `output_schema`
  - [ ] Test : le plan est JSON-sérialisable via `json.dumps(plan.to_log_dict())`
  - [ ] Test : `interaction_mode` est surchargé par `ExecutionOverrides` si présent et non `None`
  - [ ] Test non-régression : `pytest backend/app/llm_orchestration/tests/` verts

- [ ] Mettre à jour `docs/architecture/llm-processus-architecture.md` **avant merge**
  - [ ] Ajouter section : `ResolvedExecutionPlan` — champs, rôle, frontière résolution vs composition
  - [ ] Documenter les 4 valeurs de `model_source` et leur correspondance avec les branches de `_resolve_config()`
  - [ ] Documenter la journalisation `overrides_applied` dans `to_log_dict()`

### File List

- `backend/app/llm_orchestration/models.py` — ajout de `ResponseFormatConfig`, `ResolvedExecutionPlan`
- `backend/app/llm_orchestration/gateway.py` — ajout de `_resolve_plan()`, modification de `execute_request()` pour l'utiliser
- `docs/architecture/llm-processus-architecture.md` — mise à jour obligatoire avant merge

### Contexte architectural

- **`_resolve_config()` existante** : `gateway.py` lignes 284-409 — retourne `UseCaseConfig`. La logique de branchement OS Granular (`use_case_os_granular`) / OS Legacy (`use_case_os`) / config direct / fallback stub correspond aux 4 valeurs de `model_source`
- **`get_hard_policy()`** : lignes ~800-804 — retourne `system_core` string. Doit figurer dans le plan
- **`_resolve_persona()`** : lignes 411-489 — retourne `(persona_block: str, persona_id: Optional[str])`. `persona_block` doit être dans le plan (c'est un artefact résolu, pas seulement un ID)
- **`_resolve_schema()`** : lignes 491-532 — retourne le dict JSON schema + version. `output_schema` et `output_schema_id` sont les noms cibles (harmonisés avec `GatewayMeta.output_schema_id` existant)
- **Rendu prompt actuel** : lignes 770-798 — `render_vars = {**user_input, **context}`. Dans `_resolve_plan()`, construire `render_vars` depuis les attributs typés de `request.user_input` + `request.context` + `request.context.extra_context`
- **`response_format`** : utilisé pour JSON schema mode dans `ResponsesClient.execute()` — c'est le schema de format output, distinct de `output_schema` qui est le schema de validation interne
- **Repair prompt** : quand `request.flags.is_repair_call = True`, le prompt est construit avec un template hardcodé (lignes ~770-779) — `_resolve_plan()` doit court-circuiter le rendu template dans ce cas, en construisant `rendered_developer_prompt` depuis le template repair direct

### Project Structure Notes

- `ResponseFormatConfig` et `ResolvedExecutionPlan` dans `models.py`, après les modèles `ExecutionXxx` de la story 66.1
- `_resolve_plan()` reste méthode privée de `LLMGateway` dans `gateway.py`
- Les méthodes `_resolve_config()`, `_resolve_persona()`, `_resolve_schema()` sont préservées telles quelles — `_resolve_plan()` les orchestre

### References

- `_resolve_config()` : `backend/app/llm_orchestration/gateway.py` lignes 284-409
- `_resolve_persona()` : lignes 411-489
- `_resolve_schema()` : lignes 491-532
- Hard policy : lignes ~800-804
- `GatewayMeta.output_schema_id` : `backend/app/llm_orchestration/models.py` ligne ~75
- Epic 66 FR66-4, NFR66-2, NFR66-5 : `_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md`
- Story 66.1 (LLMExecutionRequest, ExecutionOverrides) : `_bmad-output/implementation-artifacts/66-1-llm-execution-request.md`

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List
