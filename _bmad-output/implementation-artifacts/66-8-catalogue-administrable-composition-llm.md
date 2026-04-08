# Story 66.8 — Introduire une résolution administrable des prompts LLM avec preview du rendu final

Status: done

## Story

En tant qu'**administrateur produit / plateforme**,
je veux **piloter dans l'interface admin ce qui est réellement demandé au moteur pour une combinaison feature / subfeature / plan**,
afin de **modifier les blocs configurables, la configuration d'exécution et le contrat de sortie sans casser les couches immuables ni recréer un prompt monolithique fragile**.

## Intent

Cette story ne vise **pas** à exposer un unique gros JSON libre représentant le prompt final complet.

Elle vise à introduire un **catalogue administrable de composition LLM** permettant de :

- cibler une combinaison `feature / subfeature / plan / locale / persona_id` ;
- éditer les **blocs configurables autorisés** ;
- associer une **config d'exécution** typée et validée ;
- associer un **contrat de sortie** versionné ;
- visualiser le **prompt final résolu** et le **plan d'exécution résolu** pour un cas donné ;
- préserver la **couche immuable** de policy / safety déjà portée par `hard_policy.py`.

**Cette story ajoute une couche d'assemblage administrable au-dessus du runtime canonique existant. Elle ne crée pas une seconde source de vérité parallèle : la résolution se repose entièrement sur les artefacts déjà consommés par le pipeline (`PromptRenderer`, `PromptRegistryV2`, `ResolvedExecutionPlan`).**

## Décisions d'architecture (arbitrages explicites)

Ces trois arbitrages sont tranchés et non rediscutables dans cette story :

**D1 — Persistance DB incluse dans le scope.** `PromptAssemblyConfig` est persistée dans une table `llm_assembly_configs`. Sans persistance, `save/publish/rollback` ne sont pas opérationnels. Une migration Alembic est requise.

**D2 — Les refs explicites sont la source de vérité des templates.** `feature_template_ref` et `subfeature_template_ref` dans `PromptAssemblyConfig` sont la source de vérité runtime. `FEATURE_USE_CASE_MAP` est un helper de découverte/bootstrap uniquement — il ne pilote pas la résolution prod.

**D3 — Intégration runtime explicite.** `_resolve_plan()` dans `gateway.py` est étendu pour activer `assembly_resolver` quand la requête porte des métadonnées `feature/subfeature/plan` (via `ExecutionUserInput`) ou une `assembly_config_id`. Fallback sur le chemin canonique existant si ces métadonnées sont absentes.

## Architecture Note

La composition reste séparée en 5 couches :

1. **Immutable policy layer** — `backend/app/llm_orchestration/policies/hard_policy.py` (profils `astrology`, `support`, `transactional`). Non éditable par l'admin standard. Visible en lecture seule dans la preview. **Non injectée dans `rendered_developer_prompt`** — projetée séparément dans la couche immuable du pipeline runtime.

2. **Product prompt layer** — Bloc feature + bloc subfeature. Chaque bloc est un **enregistrement distinct dans `LlmPromptVersionModel`**, identifié par son UUID.
   - `feature_template_ref` = template de base de la feature (obligatoire, aussi utilisé comme fallback si `subfeature_template_ref` est absent)
   - `subfeature_template_ref` = surcharge optionnelle spécifique à la subfeature
   - Si `subfeature_template_ref` est `None` → `feature_template_ref` sert de fallback, `template_source = "fallback_default"`
   - `FEATURE_USE_CASE_MAP` n'est **pas** impliqué dans la résolution runtime des templates (D2)

3. **Persona layer** — `LlmPersonaModel` / `LlmPersonaBase` déjà présents dans `admin_models.py` et en DB.

4. **User/context payload layer** — Placeholders validés contre une allowlist hardcodée par feature (dérivée des champs disponibles dans `ExecutionContext` et `ExecutionUserInput`).

5. **Execution layer** — `model`, `temperature`, `max_output_tokens`, `reasoning_effort`, `verbosity` dans `ExecutionConfigAdmin`. Validation provider-aware via `is_reasoning_model()`. `output_contract_ref` est dans `PromptAssemblyConfig`, pas dans `ExecutionConfigAdmin`.

## Acceptance Criteria

1. **Given** qu'un admin sélectionne une combinaison `feature / subfeature / plan / locale`
   **When** il ouvre l'écran de configuration LLM
   **Then** il voit la résolution hiérarchique appliquée — `feature_template`, `subfeature_template` ou fallback `default`, `persona`, `plan_rules`, `execution_config`, `output_contract` — **ainsi que la source de chaque élément résolu** (`explicit_subfeature`, `fallback_default`, `inherited`, `immutable`)

2. **Given** qu'une subfeature n'a pas de configuration dédiée (`subfeature_template_ref` est `None`)
   **When** la résolution est calculée
   **Then** le système utilise `feature_template_ref` comme fallback de la feature, et expose ce fallback via `template_source: "fallback_default"` — **aucun lookup par mapping runtime n'est effectué**

3. **Given** qu'un admin veut modifier ce qui est demandé au moteur
   **When** il édite la configuration
   **Then** il peut modifier uniquement les **blocs autorisés** : bloc feature, bloc subfeature, bloc persona, règles liées au plan, **référence au contrat de sortie versionné**, config d'exécution validée — la couche `hard_policy` n'est pas modifiable

4. **Given** que la plateforme possède une couche immuable de policy / safety (`hard_policy.py`)
   **When** un admin standard consulte ou édite la configuration
   **Then** cette couche est visible en lecture seule dans la preview, tagged `immutable`, **affichée séparément des blocs métier et non concaténée au `rendered_developer_prompt`**

5. **Given** qu'une configuration d'exécution moteur est associée
   **When** l'admin modifie modèle, reasoning effort, verbosity, max tokens, timeout ou fallback model
   **Then** ces paramètres sont validés via `ExecutionConfigAdmin` **au save comme au publish**, et les champs incompatibles (ex: `reasoning_effort` sur modèles non-reasoning, `temperature` non-None sur modèle reasoning, `fallback_model` de famille incompatible) sont rejetés immédiatement

6. **Given** qu'un template utilise des variables injectées
   **When** l'admin sauvegarde ou publie la configuration
   **Then** tous les placeholders `{{variable}}` sont extraits via `PromptRenderer.extract_placeholders()` et validés contre `PLACEHOLDER_ALLOWLIST[feature]` — tout placeholder inconnu ou interdit bloque l'opération

7. **Given** qu'un admin visualise une configuration
   **When** il ouvre la zone de preview
   **Then** il peut voir séparément et distinctement :
   - les **blocs du prompt métier** (feature / subfeature / persona / plan_rules) avec leur source (`explicit_subfeature`, `fallback_default`, `inherited`) ;
   - la **couche immuable** (`hard_policy`) affichée séparément en lecture seule, tagged `immutable` ;
   - les **variables injectables disponibles** avec type, origine et exemple ;
   - le `rendered_developer_prompt` final résolu (assemblage des blocs métier avec variables de fixture) ;
   - le **contrat de sortie** associé ;
   - la **config d'exécution résolue** ;
   - un marqueur explicite `draft_preview: true` indiquant que ce rendu n'est pas la configuration active en production

8. **Given** qu'une configuration est sauvegardée
   **When** l'admin modifie l'activation des blocs configurables
   **Then** il peut activer ou désactiver les blocs de la couche autorisée (feature, subfeature, persona, plan_rules), sans jamais désactiver la couche immuable — **le réordonnancement libre entre blocs n'est pas dans le scope de cette story**

9. **Given** qu'une configuration est publiée
   **When** elle devient active
   **Then** elle est persiste en DB (`llm_assembly_configs`), versionnée via `AssemblyConfigRegistry` suivant le **même pattern que `PromptRegistryV2`** (archive l'actif, publie le nouveau, invalide le cache) ; la version précédente reste consultable ; un rollback vers une version archivée est possible

10. **Given** qu'une configuration active pilote une feature en production
    **When** le gateway résout un appel portant `feature/subfeature/plan` dans la requête
    **Then** `_resolve_plan()` active `assembly_resolver`, et le `ResolvedExecutionPlan` résultant expose : `template_source`, `feature`, `subfeature`, `plan`, `persona_id` — ces champs apparaissent dans `to_log_dict()`

11. **Given** qu'un plan d'abonnement différent est sélectionné
    **When** la configuration est résolue
    **Then** le système applique les règles liées au plan depuis `PLAN_RULES_REGISTRY` — uniquement un bloc de texte d'instruction additionnel et/ou une contrainte de `max_output_tokens` à la baisse — sans dupliquer ni remplacer le template feature/subfeature

12. **Given** qu'un admin veut tester une configuration avant publication
    **When** il lance une preview de rendu sur fixture
    **Then** le système produit un `PromptAssemblyPreview` via `build_assembly_preview()` — **aucun appel LLM réel n'est requis ni déclenché** ; la preview est purement une résolution locale + rendu via `PromptRenderer.render()`

## Tasks / Subtasks

- [ ] Introduire le modèle DB `PromptAssemblyConfigModel` et la migration Alembic (AC: 9 — D1)
  - [ ] Créer `PromptAssemblyConfigModel` dans `backend/app/infra/db/models/llm_assembly.py` :
    - `id: uuid.UUID` (PK)
    - `feature: str`, `subfeature: Optional[str]`, `plan: Optional[str]`, `locale: str`
    - `feature_template_ref: uuid.UUID` (FK → `llm_prompt_versions.id`)
    - `subfeature_template_ref: Optional[uuid.UUID]` (FK → `llm_prompt_versions.id`, nullable)
    - `persona_ref: Optional[uuid.UUID]` (FK → `llm_personas.id`, nullable)
    - `plan_rules_ref: Optional[str]` (clé de `PLAN_RULES_REGISTRY`)
    - `execution_config: JSON` (sérialisé depuis `ExecutionConfigAdmin`)
    - `output_contract_ref: Optional[str]` (clé dans `LlmOutputSchemaModel`)
    - `feature_enabled: bool = True`, `subfeature_enabled: bool = True`, `persona_enabled: bool = True`, `plan_rules_enabled: bool = True` (flags d'activation par couche — requis par AC8)
    - `status: PromptStatus` (réutiliser l'enum `PromptStatus` de `llm_prompt.py`)
    - `created_by: str`, `created_at: datetime`, `published_at: Optional[datetime]`
    - `__table_args__` : index unique partiel sur `(feature, COALESCE(subfeature, ''), COALESCE(plan, ''), locale)` filtré `WHERE status = 'published'` — les colonnes nullables sont normalisées en chaîne vide dans l'index pour éviter les doublons silencieux (comportement PostgreSQL avec NULL dans un unique index)
  - [ ] Créer la migration Alembic correspondante
  - [ ] Ajouter `PromptAssemblyConfigModel` à `backend/app/infra/db/models/__init__.py`

- [ ] Introduire les modèles Pydantic admin pour la composition LLM (AC: 1, 2, 3, 5, 9)
  - [ ] Créer `PromptAssemblyTarget` dans `backend/app/llm_orchestration/admin_models.py` :
    - `feature: str`, `subfeature: Optional[str]`, `plan: Optional[str]`, `locale: str = "fr-FR"`, `persona_id: Optional[str]`
  - [ ] Créer `PromptAssemblyConfig` dans `backend/app/llm_orchestration/admin_models.py` — modèle Pydantic de lecture/écriture (miroir de `PromptAssemblyConfigModel`) :
    - `id: Optional[uuid.UUID]`
    - `feature_template_ref: uuid.UUID` (source de vérité — D2)
    - `subfeature_template_ref: Optional[uuid.UUID]`
    - `plan_rules_ref: Optional[str]`
    - `persona_ref: Optional[uuid.UUID]`
    - `execution_config: ExecutionConfigAdmin` (embarqué inline)
    - `output_contract_ref: Optional[str]`
    - `feature_enabled: bool = True`, `subfeature_enabled: bool = True`, `persona_enabled: bool = True`, `plan_rules_enabled: bool = True`
    - `status: PromptStatus`
  - [ ] Créer `ResolvedAssembly` dans `backend/app/llm_orchestration/admin_models.py` — **artefact intermédiaire** entre config admin et `ResolvedExecutionPlan` ; produit par `resolve_assembly()` :
    - `target: PromptAssemblyTarget`
    - `feature_template_prompt: str` (developer_prompt brut chargé depuis `LlmPromptVersionModel`)
    - `subfeature_template_prompt: Optional[str]`
    - `template_source: Literal["explicit_subfeature", "fallback_default"]`
    - `persona_ref: Optional[uuid.UUID]`
    - `persona_block: Optional[str]`
    - `plan_rules_content: Optional[str]` (texte résolu depuis `PLAN_RULES_REGISTRY`)
    - `execution_config: ExecutionConfigAdmin`
    - `output_contract: Optional[dict]`
    - `available_placeholders: List[PlaceholderInfo]`
    - `policy_layer_content: str` (depuis `hard_policy.get_hard_policy()`, **non injecté dans le rendered prompt**)
  - [ ] Créer `PromptAssemblyPreview` dans `backend/app/llm_orchestration/admin_models.py` — produit par `build_assembly_preview()` :
    - `target: PromptAssemblyTarget`
    - `blocks: List[AssemblyBlockPreview]` (type, content, source: `explicit_subfeature | fallback_default | inherited | immutable`)
    - `available_placeholders: List[PlaceholderInfo]`
    - `rendered_developer_prompt: str` (assemblage des blocs métier uniquement — sans `policy_layer_content`)
    - `policy_layer_preview: str` (couche immuable, affiché séparément)
    - `output_contract: Optional[dict]`
    - `execution_config: ExecutionConfigAdmin`
    - `draft_preview: bool = True`

- [ ] Créer le modèle `ExecutionConfigAdmin` provider-aware (AC: 5)
  - [ ] Créer dans `backend/app/llm_orchestration/admin_models.py` :
    - `provider: str`, `model: str`, `temperature: Optional[float]`
    - `reasoning_effort: Optional[Literal["low", "medium", "high"]]`
    - `verbosity: Optional[Literal["verbose", "normal", "concise"]]` — voir Dev Notes pour le mapping runtime
    - `max_output_tokens: int`, `timeout_seconds: int`
    - `fallback_model: Optional[str]` — doit appartenir à la même famille que `model` (`is_reasoning_model`)
    - **Pas de `output_schema_ref`** — l'output contract est géré dans `PromptAssemblyConfig.output_contract_ref` uniquement
  - [ ] Ajouter un `@model_validator(mode="after")` :
    - `is_reasoning_model(model) == True` → `temperature` doit être `None`
    - `is_reasoning_model(model) == False` → `reasoning_effort` doit être `None`
    - `fallback_model` non-None → `is_reasoning_model(fallback_model) == is_reasoning_model(model)` sinon `ValueError`
  - [ ] Réutiliser `is_reasoning_model()` de `backend/app/llm_orchestration/models.py:15` — NE PAS dupliquer

- [ ] Ajouter `PromptRenderer.extract_placeholders()` (AC: 6)
  - [ ] Ajouter `@staticmethod extract_placeholders(template: str) -> List[str]` dans `services/prompt_renderer.py`
  - [ ] Le pattern `re.findall(r"\{\{([a-zA-Z0-9_]+)\}\}", template)` est **centralisé ici uniquement** — ne pas le dupliquer dans `assembly_resolver.py` ni ailleurs
  - [ ] Cette méthode est utilisée par `validate_placeholders()` et par `build_assembly_preview()`

- [ ] Introduire la hiérarchie de résolution feature / subfeature / default (AC: 1, 2, 10, 11)
  - [ ] Créer `backend/app/llm_orchestration/services/assembly_resolver.py` avec `resolve_assembly(target: PromptAssemblyTarget, config: PromptAssemblyConfig, db: Session) -> ResolvedAssembly` exécutant 5 étapes dans l'ordre :
    - **Étape 1 — Template** : charger `LlmPromptVersionModel` via `config.feature_template_ref` (source D2) ; si `config.subfeature_template_ref` non-None → charger aussi ; déduire `template_source` ; si `feature_template_ref` ne correspond pas à un prompt publié → `GatewayConfigError`
    - **Étape 2 — Persona** : si `config.persona_ref` → résoudre `LlmPersonaModel` et appeler `compose_persona_block()` de `persona_composer.py`
    - **Étape 3 — Execution config** : le `@model_validator` de `ExecutionConfigAdmin` valide déjà à l'instanciation ; dériver `safety_profile` depuis `LlmUseCaseConfigModel` pour le `use_case_key` du template feature
    - **Étape 4 — Output contract** : si `config.output_contract_ref` → résoudre `LlmOutputSchemaModel`
    - **Étape 5 — Plan rules** : si `target.plan` et `config.plan_rules_ref` → résoudre depuis `PLAN_RULES_REGISTRY` (voir Dev Notes)
    - Dériver `policy_layer_content` depuis `hard_policy.get_hard_policy(safety_profile)`
    - Retourner `ResolvedAssembly` complet
  - [ ] Définir `FEATURE_USE_CASE_MAP` comme helper de bootstrap (pas source de vérité prod) — utilisé uniquement pour la découverte lors de la création d'une nouvelle config admin
  - [ ] Utiliser `PromptRegistryV2.get_active_prompt()` pour vérifier le statut des templates référencés — NE PAS recréer de logique de cache

- [ ] Introduire la validation des placeholders (AC: 6)
  - [ ] Définir `PLACEHOLDER_ALLOWLIST: dict[str, list[str]]` dans `assembly_resolver.py` — indexé par `feature`, hardcodé pour cette story (voir Dev Notes)
  - [ ] Créer `validate_placeholders(template: str, feature: str) -> List[str]` dans `assembly_resolver.py` :
    - Appelle `PromptRenderer.extract_placeholders(template)`
    - Vérifie chaque placeholder contre `PLACEHOLDER_ALLOWLIST.get(feature, [])`
    - Retourne les placeholders inconnus ou interdits
  - [ ] `validate_placeholders()` est appelé au save **et** au publish — les deux opérations sont bloquées si la liste est non vide

- [ ] Introduire la preview admin complète (AC: 7, 12)
  - [ ] Créer `build_assembly_preview(target, config, fixture_vars: dict, db: Session) -> PromptAssemblyPreview` dans `assembly_resolver.py`
  - [ ] Appeler `resolve_assembly()` pour obtenir `ResolvedAssembly`
  - [ ] Construire les `AssemblyBlockPreview` avec source annotée pour chaque bloc
  - [ ] Produire `rendered_developer_prompt` via `PromptRenderer.render(assembled_blocks, fixture_vars)` — **`policy_layer_content` n'est pas injecté dans ce rendu** ; il alimente `policy_layer_preview` séparément
  - [ ] Marquer `draft_preview = True`
  - [ ] Aucun appel LLM ne doit être déclenché

- [ ] Introduire `AssemblyConfigRegistry` pour la persistance, publication et rollback (AC: 9 — D1)
  - [ ] Créer `AssemblyConfigRegistry` dans `backend/app/llm_orchestration/services/assembly_registry.py` — **fichier séparé de `assembly_resolver.py`** (séparation des responsabilités : registry = persistance + cache, resolver = résolution pure)
  - [ ] Suivre **exactement le même pattern que `PromptRegistryV2`** :
    - `get_active_config(db, feature, subfeature, plan, locale) -> Optional[PromptAssemblyConfigModel]` (avec cache TTL)
    - `publish_config(db, config_id) -> PromptAssemblyConfigModel` (archive l'actif, publie le nouveau)
    - `rollback_config(db, feature, subfeature, plan, locale, target_id?) -> PromptAssemblyConfigModel`
    - `invalidate_cache(...)`
  - [ ] NE PAS réécrire `PromptRegistryV2` — l'adapter le pattern, pas le modifier

- [ ] Étendre `ResolvedExecutionPlan` avec les champs de traçabilité assembly (AC: 10 — D3)
  - [ ] Dans `backend/app/llm_orchestration/models.py`, ajouter à `ResolvedExecutionPlan` :
    - `feature: Optional[str] = None`
    - `subfeature: Optional[str] = None`
    - `plan: Optional[str] = None`
    - `template_source: Optional[Literal["explicit_subfeature", "fallback_default", "stub", "registry"]] = None`
  - [ ] Mettre à jour `to_log_dict()` pour inclure ces 4 champs (non volumineux, pas à filtrer)

- [ ] Étendre `_resolve_plan()` pour activer `assembly_resolver` (AC: 10 — D3)
  - [ ] Étendre `ExecutionUserInput` dans `models.py` avec des champs optionnels :
    - `feature: Optional[str] = None`
    - `subfeature: Optional[str] = None`
    - `plan: Optional[str] = None`
    - `assembly_config_id: Optional[uuid.UUID] = None`
  - [ ] Dans `gateway.py::_resolve_plan()`, en début de méthode : si `request.user_input.feature` ou `request.user_input.assembly_config_id` est présent → appeler `resolve_assembly()` et utiliser les champs de `ResolvedAssembly` pour alimenter `ResolvedExecutionPlan` (`rendered_developer_prompt`, `persona_block`, `output_contract`, `execution_config`, `template_source`, `feature`, `subfeature`, `plan`)
  - [ ] Fallback sur le chemin canonique existant si ces champs sont absents — **aucune régression sur les parcours `chat`, `guidance`, `natal` existants**

- [ ] Introduire les tests (AC: 2, 5, 6, 9, 10, 12)
  - [ ] `backend/app/llm_orchestration/tests/test_assembly_resolver.py` :
    - Test : `feature_template_ref` valide + `subfeature_template_ref` valide → `template_source = "explicit_subfeature"`
    - Test : `subfeature_template_ref` absent → `feature_template_ref` utilisé comme template principal → `template_source = "fallback_default"`
    - Test : `feature_template_ref` pointe vers un prompt non publié → `GatewayConfigError`
    - Test : `subfeature_enabled = False` → même comportement que `subfeature_template_ref` absent
    - Test : `temperature` non-None rejeté sur modèle reasoning
    - Test : `reasoning_effort` non-None rejeté sur modèle non-reasoning
    - Test : `fallback_model` d'une famille différente → `ValueError`
    - Test : placeholder `{{unknown_var}}` → bloque save et publish
    - Test : `build_assembly_preview()` retourne `draft_preview = True` et `policy_layer_preview` séparé de `rendered_developer_prompt`
    - Test : `publish_config` archive la version précédente et retourne la nouvelle
    - Test : `rollback_config` réactive la version archivée
    - Test : `ResolvedExecutionPlan.to_log_dict()` inclut `feature`, `subfeature`, `plan`, `template_source`
    - Test : `_resolve_plan()` sans `feature` → chemin canonique (pas d'appel à `assembly_resolver`)

## Dev Notes

### Contexte architectural — NE PAS dupliquer

- `is_reasoning_model(model)` dans `models.py:15` — réutiliser dans `ExecutionConfigAdmin`, ne pas dupliquer
- `PromptRenderer.render()` dans `services/prompt_renderer.py` — **y ajouter `extract_placeholders()`** dans cette story
- `compose_persona_block()` dans `services/persona_composer.py` — composition persona dans `resolve_assembly()`, ne pas modifier
- `PromptRegistryV2` dans `services/prompt_registry_v2.py` — `get_active_prompt()` utilisé pour vérifier les templates référencés, ne pas recréer
- `PromptStatus` (DRAFT/PUBLISHED/ARCHIVED) dans `infra/db/models/llm_prompt.py` — réutiliser pour `PromptAssemblyConfigModel.status`
- `hard_policy.get_hard_policy(safety_profile)` dans `policies/hard_policy.py` — alimente `policy_layer_content` dans `ResolvedAssembly` et `policy_layer_preview` dans `PromptAssemblyPreview`
- `LlmPersonaModel`, `LlmUseCaseConfigModel`, `LlmOutputSchemaModel` dans `infra/db/models/` — modèles DB à interroger dans `resolve_assembly()`

### Dimension nouvelle — Hiérarchie admin/résolution

La structure actuelle est **plate** : `use_case_key = "guidance_daily"`. Cette story introduit une hiérarchie admin/résolution : `feature = "guidance"`, `subfeature = "daily"`, `plan = "premium"`.

**La hiérarchie feature/subfeature/plan est une abstraction de la couche admin et de la résolution. Le runtime reste compatible avec les `use_case_key` existants tant que la plateforme n'a pas basculé nativement.** Les parcours `chat`, `guidance`, `natal` sans `feature` dans la requête continuent sur le chemin canonique sans modification.

### Source de vérité des templates (D2)

`FEATURE_USE_CASE_MAP` est un **helper de bootstrapping uniquement** :

```python
# assembly_resolver.py — discovery helper, pas source de vérité prod
FEATURE_USE_CASE_MAP: dict[tuple[str, str], str] = {
    ("guidance", "daily"): "guidance_daily",
    ("guidance", "weekly"): "guidance_weekly",
    ("natal", "complete"): "natal_long_free",
    # convention par défaut appliquée si absent : f"{feature}_{subfeature}"
}
```

**En prod, la résolution charge les templates par UUID** (`feature_template_ref`, `subfeature_template_ref`). Le map sert uniquement à pré-remplir les sélecteurs lors de la création d'une nouvelle config admin.

### Plan rules — périmètre borné

`PLAN_RULES_REGISTRY` est un **dict Python hardcodé** dans `assembly_resolver.py`. Les règles sont des petits textes d'instruction. Elles ne peuvent pas modifier la hard_policy, le template feature/subfeature, le modèle ou la persona.

```python
PLAN_RULES_REGISTRY: dict[str, PlanRule] = {
    "premium_depth": PlanRule(
        instruction="Pour ce compte premium, inclure une analyse approfondie des maisons angulaires.",
        max_output_tokens_override=None,  # None = pas de contrainte
    ),
    "free_limit": PlanRule(
        instruction=None,
        max_output_tokens_override=800,
    ),
}
```

`PlanRule` est un dataclass/Pydantic avec : `instruction: Optional[str]`, `max_output_tokens_override: Optional[int]`.

### Algorithme de résolution complet (5 étapes)

```
1. TEMPLATE (source D2 — refs explicites uniquement, pas de lookup mapping) :
   → charger LlmPromptVersionModel par UUID (feature_template_ref)
     si non publié ou introuvable → GatewayConfigError("feature_template_ref invalid or not published")
   → si subfeature_template_ref non-None et config.subfeature_enabled :
       charger LlmPromptVersionModel par UUID (subfeature_template_ref)
       si non publié → GatewayConfigError("subfeature_template_ref not published")
       template_source = "explicit_subfeature"
   → sinon (subfeature_template_ref est None ou subfeature_enabled = False) :
       utiliser feature_template_ref comme template principal
       template_source = "fallback_default"
   → FEATURE_USE_CASE_MAP n'est JAMAIS consulté dans ce chemin

2. PERSONA :
   → si config.persona_ref → résoudre LlmPersonaModel, appeler compose_persona_block()
   → sinon : persona_block = None

3. EXECUTION CONFIG :
   → le @model_validator de ExecutionConfigAdmin valide à l'instanciation
   → dériver safety_profile depuis LlmUseCaseConfigModel[use_case_key du feature template]

4. OUTPUT CONTRACT :
   → si config.output_contract_ref → résoudre LlmOutputSchemaModel
   → sinon : None

5. PLAN RULES :
   → si target.plan et config.plan_rules_ref → PLAN_RULES_REGISTRY[plan_rules_ref]
   → appliquer instruction et/ou max_output_tokens_override
   → retourner ResolvedAssembly
```

### Intégration runtime (D3)

`ExecutionUserInput` reçoit 4 champs optionnels supplémentaires (`feature`, `subfeature`, `plan`, `assembly_config_id`). Tous sont `None` par défaut — **les parcours existants ne sont pas impactés**.

**Règle de sélection runtime de la config assembly (ordre de priorité strict) :**

```
1. Si assembly_config_id est fourni → charger cette config par UUID (priorité absolue)
2. Sinon → chercher la config PUBLISHED par (feature, subfeature, plan, locale)
3. Si aucune config publiée n'est trouvée → GatewayConfigError
4. Aucun fallback implicite cross-plan ou cross-locale n'est autorisé
```

Dans `_resolve_plan()` :

```python
if request.user_input.feature or request.user_input.assembly_config_id:
    # 1. Sélectionner la config via la règle de priorité ci-dessus
    # 2. Appeler resolve_assembly(target, config, db)
    # 3. Alimenter ResolvedExecutionPlan depuis ResolvedAssembly
else:
    # chemin canonique existant inchangé
```

### Effet des plan_rules sur execution_config

`ResolvedAssembly.execution_config` contient la **configuration finale effective** après application éventuelle des contraintes `plan_rules`. Concrètement, si `PlanRule.max_output_tokens_override` est non-None et inférieur à `execution_config.max_output_tokens`, la valeur override remplace la valeur config dans `ResolvedAssembly.execution_config.max_output_tokens`. Le dev ne doit pas appliquer l'override ailleurs — il est déjà absorbé dans `ResolvedAssembly.execution_config`.

### Placeholder allowlist

`PLACEHOLDER_ALLOWLIST` est indexé par `feature` uniquement (pas `feature/subfeature`) pour éviter la sur-fragmentation. Granularité subfeature en follow-up si besoin.

```python
PLACEHOLDER_ALLOWLIST: dict[str, list[str]] = {
    "guidance": ["locale", "use_case", "situation", "last_user_msg"],
    "natal": ["locale", "use_case", "chart_json", "natal_data", "birth_date"],
    "chat": ["locale", "use_case", "last_user_msg"],
}
```

### Validation provider-aware — verbosity

`verbosity: Optional[Literal["verbose", "normal", "concise"]]` — l'enum est intentionnellement simple. Le mapping vers le paramètre réel du provider (ex: `detail_level` chez certains providers) est réalisé dans `ResponsesClient` au moment de l'appel. Si le provider actuel ne supporte pas ce paramètre, il est ignoré en **best effort avec un log structuré de debug** (`logger.debug("verbosity not supported by provider, skipping")`). **Ne pas inventer de mapping dans cette story** — documenter dans les Completion Notes si un mapping spécifique est découvert nécessaire.

### `policy_layer_content` — séparation stricte

`policy_layer_content` dans `ResolvedAssembly` et `policy_layer_preview` dans `PromptAssemblyPreview` sont des champs **séparés du `rendered_developer_prompt`**. La couche immuable est projetée dans le `system_core` par le pipeline runtime — elle n'est jamais concaténée au developer prompt.

### Structure des fichiers

```
backend/app/
├── infra/db/models/
│   └── llm_assembly.py          # CRÉER : PromptAssemblyConfigModel
├── llm_orchestration/
│   ├── admin_models.py          # ÉTENDRE : PromptAssemblyTarget, PromptAssemblyConfig,
│   │                            #   ResolvedAssembly, PromptAssemblyPreview,
│   │                            #   ExecutionConfigAdmin, AssemblyBlock,
│   │                            #   AssemblyBlockPreview, PlaceholderInfo, PlanRule
│   ├── models.py                # ÉTENDRE : ResolvedExecutionPlan (+4 champs),
│   │                            #   ExecutionUserInput (+4 champs)
│   ├── gateway.py               # ÉTENDRE : _resolve_plan() (branchement assembly)
│   ├── services/
│   │   ├── assembly_resolver.py # CRÉER — résolution pure + preview :
│   │   │                        #   resolve_assembly(), validate_placeholders(),
│   │   │                        #   build_assembly_preview(),
│   │   │                        #   FEATURE_USE_CASE_MAP (bootstrap uniquement),
│   │   │                        #   PLACEHOLDER_ALLOWLIST, PLAN_RULES_REGISTRY
│   │   ├── assembly_registry.py # CRÉER — persistance + publication + cache :
│   │   │                        #   AssemblyConfigRegistry (get_active_config,
│   │   │                        #   publish_config, rollback_config, invalidate_cache)
│   │   └── prompt_renderer.py   # ÉTENDRE : extract_placeholders()
│   └── tests/
│       └── test_assembly_resolver.py  # CRÉER
└── alembic/versions/
    └── xxxx_add_llm_assembly_configs.py  # CRÉER (migration)
```

**Séparation des responsabilités** :
- `assembly_resolver.py` = résolution, validation, preview — pas de DB write, pas de cache write
- `assembly_registry.py` = persistance, status cycle, cache TTL — même pattern que `PromptRegistryV2`

### Project Structure Notes

- `PROMPT_CATALOG` dans `backend/app/prompts/catalog.py` — ne pas toucher ; la résolution assembly utilise `LlmPromptVersionModel` par UUID, pas le catalog hardcodé.
- `USE_CASE_STUBS` dans `gateway.py` — restent en place ; le branchement assembly se fait avant, si absent, le fallback stubs reste actif.
- `persona_composer.py` — utilisé tel quel, ne pas modifier.
- `PromptRegistryV2` — utilisé tel quel pour vérification du statut des templates ; `AssemblyConfigRegistry` suit le même pattern pour la config assembly.

### Sécurité critique

- Placeholders validés contre `PLACEHOLDER_ALLOWLIST` au save **et** au publish.
- Fixtures de preview anonymisées — aucune donnée réelle dans les previews.
- `hard_policy` non injectée dans `rendered_developer_prompt` — affichée séparément dans `policy_layer_preview`.
- `fallback_model` contraint à la même famille de modèles que `model`.
- `AssemblyConfigRegistry` invalide le cache à chaque publish/rollback.

### References

- `backend/app/llm_orchestration/models.py` — `ResolvedExecutionPlan`, `ExecutionUserInput`, `is_reasoning_model`
- `backend/app/llm_orchestration/admin_models.py` — modèles Pydantic admin existants
- `backend/app/llm_orchestration/services/prompt_registry_v2.py` — pattern à reproduire dans `AssemblyConfigRegistry`
- `backend/app/llm_orchestration/services/prompt_renderer.py` — `render()` + nouvelle `extract_placeholders()`
- `backend/app/llm_orchestration/services/persona_composer.py` — `compose_persona_block()`
- `backend/app/llm_orchestration/policies/hard_policy.py` — couche immuable
- `backend/app/infra/db/models/llm_prompt.py` — `LlmPromptVersionModel`, `PromptStatus`
- Epic 66 : `_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md`
- Stories 66.1–66.7 : `_bmad-output/implementation-artifacts/66-*.md`

## File List

- `backend/app/infra/db/models/llm_assembly.py` — création : `PromptAssemblyConfigModel`
- `backend/app/infra/db/models/__init__.py` — extension : ajout de l'import
- `backend/migrations/versions/1a16484f6ae0_add_llm_assembly_configs.py` — création : migration initiale
- `backend/migrations/versions/432a48efb602_add_assembly_interaction_fields.py` — extension : ajout de `interaction_mode`, `user_question_policy`, `fallback_use_case`
- `backend/app/llm_orchestration/admin_models.py` — extension : `PromptAssemblyTarget`, `PromptAssemblyConfig`, `ResolvedAssembly`, `PromptAssemblyPreview`, `ExecutionConfigAdmin`, `AssemblyBlock`, `AssemblyBlockPreview`, `PlaceholderInfo`, `PlanRule`
- `backend/app/llm_orchestration/models.py` — extension : `ResolvedExecutionPlan` (+4 champs), `ExecutionUserInput` (+4 champs), `to_log_dict()` mis à jour
- `backend/app/llm_orchestration/gateway.py` — extension : `_resolve_plan()` branché sur `assembly_resolver`
- `backend/app/llm_orchestration/services/assembly_resolver.py` — création : `resolve_assembly()`, `validate_placeholders()`, `build_assembly_preview()`, `FEATURE_USE_CASE_MAP` (bootstrap), `PLACEHOLDER_ALLOWLIST`, `PLAN_RULES_REGISTRY`
- `backend/app/llm_orchestration/services/assembly_registry.py` — création : `AssemblyConfigRegistry` (get_active_config, publish_config, rollback_config, invalidate_cache)
- `backend/app/llm_orchestration/services/prompt_renderer.py` — extension : `PromptRenderer.extract_placeholders()`
- `backend/app/llm_orchestration/tests/test_assembly_resolution.py` — couverture résolution, fallback, rollback hot-cache, validation multi-templates, mode chat assembly
- `backend/app/llm_orchestration/services/prompt_registry_v2.py` — correction cache TTL : sérialisation de `reasoning_effort` et `verbosity`

## Contexte architectural

- Cette story ne remplace pas la couche immuable de policy : elle la rend visible séparément dans la preview, non injectée dans le developer prompt, non modifiable.
- Le runtime canonique continue de consommer un `ResolvedExecutionPlan` ; il ne reçoit jamais un JSON admin brut.
- La hiérarchie `feature/subfeature/plan` est une abstraction admin/résolution — le runtime reste compatible avec les `use_case_key` existants via le chemin canonique.
- Le plan d'abonnement agit comme couche de contrainte bornée (texte additionnel + contrainte `max_output_tokens`) — il ne remplace ni le template ni la persona.
- `ResolvedAssembly` est le seul artefact intermédiaire entre la config admin et `ResolvedExecutionPlan` ; aucune couche ne consomme la config admin brute directement.
- `PromptAssemblyPreview.rendered_developer_prompt` ne contient jamais `policy_layer_content` — la séparation des couches est préservée à la preview comme au runtime. Ce champ représente le rendu preview de la **couche éditoriale / developer** des blocs métier assemblés ; il n'est pas le payload provider complet, qui inclut aussi `system_core`, `policy_layer_content` et la composition de messages multi-turn.

## Dev Agent Record

### Agent Model Used

- Codex GPT-5

### Debug Log References

- `gateway_step_failed:build_result use_case=* error="GatewayMeta" object has no field "template_source"` — corrigé par ajout de `template_source` dans `GatewayMeta`
- `gateway_adjust_reasoning model=gpt-5 effort=low` suivi d'un second passage avec `effort=None` — corrigé par enrichissement du cache TTL de `PromptRegistryV2` pour conserver `reasoning_effort` et `verbosity`
- revue post-implémentation : détection puis correction d'une migration incomplète sur `fallback_use_case`

### Completion Notes List

- implémentation finalisée avec persistance DB, preview locale, branchement runtime du gateway et traçabilité assembly dans `ResolvedExecutionPlan` / `GatewayMeta`
- correctif post-review : conservation de `interaction_mode`, `user_question_policy` et `fallback_use_case` dans le runtime assembly
- correctif post-review : rollback rendu fiable même avec cache chaud via `UPDATE` direct sur la config publiée courante
- correctif post-review : validation des placeholders étendue au `subfeature_template` au save et au publish
- correctif post-review : migration complémentaire ajoutée pour aligner le schéma SQL réel avec le modèle ORM (`interaction_mode`, `user_question_policy`, `fallback_use_case`)
- correctif de compatibilité admin : réintroduction des schémas Pydantic attendus par `admin_llm.py` dans `admin_models.py`
- correctif de compatibilité runtime : ajout de `template_source` dans `GatewayMeta`
- correctif de cache runtime : sérialisation de `reasoning_effort` et `verbosity` dans `PromptRegistryV2` pour éviter la perte de paramètres GPT-5 sur lecture TTL
- validation finale confirmée en local : `pytest -q` -> `2757 passed, 3 skipped`
