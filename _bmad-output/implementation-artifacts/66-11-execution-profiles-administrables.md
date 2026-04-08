# Story 66.11 : Introduire les ExecutionProfiles administrables

Status: ready-for-dev

## Story

En tant qu'**administrateur plateforme**,
je veux **piloter les paramètres d'exécution moteur (provider, modèle, profils reasoning/verbosity, tokens, timeout, tools policy) via une entité administrable dédiée liée à la feature/subfeature/plan**,
afin de **séparer complètement le choix d'exécution du texte du prompt et de pouvoir faire évoluer l'un sans toucher à l'autre**.

## Intent

Aujourd'hui, le choix du modèle et des paramètres d'exécution est résolu par `resolve_model()` dans `backend/app/prompts/catalog.py` via un mécanisme de priorités environnement/catalogue/fallback. Cette résolution est fonctionnelle mais :
- Elle est implicitement liée au use_case, pas à la feature/subfeature/plan.
- Les paramètres comme `reasoning_effort`, `verbosity`, `max_output_tokens` sont partiellement administrables via `ExecutionConfigAdmin` (story 66.8) mais sans entité DB dédiée propre au profil d'exécution.
- Un admin ne peut pas dire "pour la feature `natal`, plan `premium`, utilise le profil deep-reasoning avec 4000 tokens" sans modifier le code ou les variables d'environnement.

Cette story introduit `ExecutionProfile` comme **entité administrable DB dédiée**, séparée du texte du prompt, liée à `feature/subfeature/plan` via une résolution waterfall similaire à `PromptAssemblyConfig`.

## Décisions d'architecture

**D1 — `ExecutionProfile` est une entité DB distincte de `PromptAssemblyConfig`.** Elle peut être référencée depuis `PromptAssemblyConfig` via `execution_profile_ref`, ou résolue indépendamment par le gateway.

**D2 — La résolution du profil d'exécution suit un waterfall :** `feature + subfeature + plan` → `feature + subfeature` → `feature` → défaut système. Ce waterfall est implémenté dans un `ExecutionProfileRegistry` similaire à `AssemblyRegistry`.

**D3 — `resolve_model()` existant devient un fallback de compatibilité.** Quand aucun `ExecutionProfile` n'est trouvé pour la combinaison courante, `resolve_model()` reste actif. Cela garantit la non-régression.

**D4 — Les profils internes stables sont introduits dès cette story.** `ExecutionProfile` expose d'emblée les abstractions stables (`reasoning_profile`, `verbosity_profile`, `output_mode`, `tool_mode`) au lieu des paramètres OpenAI bruts (`reasoning_effort`, `verbosity`). Un `ProviderParameterMapper` minimal (OpenAI uniquement) est inclus dans le scope. La story 66.18 étend ce mapper pour le support multi-provider et clarifie le traitement de `verbosity_profile` (instruction textuelle vs contrainte tokens). Il n'y a pas de churn de modèle entre 66.11 et 66.18 : 66.11 construit la structure cible dès le départ.

**D5 — `fallback_profile_id`** permet de chaîner un profil de fallback (ex: si le modèle principal est indisponible, utiliser un profil backup).

**D6 — Mapping `reasoning_profile` → paramètres OpenAI (implémenté dans cette story) :**
- `off` → pas de `reasoning_effort`, `temperature` applicable
- `light` → `reasoning_effort="low"`, `temperature=None`
- `medium` → `reasoning_effort="medium"`, `temperature=None`
- `deep` → `reasoning_effort="high"`, `temperature=None`

## Acceptance Criteria

1. **Given** qu'un `ExecutionProfile` est créé en DB pour la combinaison `feature=natal, plan=premium` avec `reasoning_profile="deep", verbosity_profile="detailed"`
   **When** le gateway résout un appel portant `feature=natal, plan=premium`
   **Then** le `ResolvedExecutionPlan` contient les profils internes (`reasoning_profile`, `verbosity_profile`, `output_mode`, `tool_mode`) et les paramètres OpenAI traduits (`reasoning_effort="high"`, `temperature=None`) — `resolve_model()` n'est pas appelé

2. **Given** qu'aucun `ExecutionProfile` n'est défini pour la combinaison courante
   **When** le gateway tente la résolution waterfall (`feature+subfeature+plan` → `feature+subfeature` → `feature`)
   **Then** si aucun profil n'est trouvé à aucun niveau, le fallback sur `resolve_model()` existant est activé avec un log `execution_profile_fallback: resolve_model_used`

3. **Given** qu'un `ExecutionProfile` référence un `fallback_profile_id`
   **When** l'exécution principale échoue (timeout ou erreur provider)
   **Then** le gateway tente automatiquement avec le profil de fallback référencé

4. **Given** qu'un admin ouvre l'interface de gestion des profils d'exécution
   **When** il crée un nouveau profil
   **Then** il peut définir : `provider`, `model`, `reasoning_profile` (`off|light|medium|deep`), `verbosity_profile` (`concise|balanced|detailed`), `output_mode` (`free_text|structured_json`), `tool_mode` (`none|optional|required`), `max_output_tokens`, `timeout_seconds`, `fallback_profile_id`, et la combinaison `feature/subfeature/plan` cible — **aucun paramètre OpenAI brut n'est exposé directement**

5. **Given** qu'un admin tente de créer un profil avec `reasoning_profile` non-`off` sur un modèle identifié comme non-reasoning
   **When** il sauvegarde le profil
   **Then** la validation Pydantic rejette la combinaison avec `"reasoning_profile '{value}' requires a reasoning-capable model — got: {model}"`

6. **Given** que `PromptAssemblyConfig` référence un `execution_profile_ref`
   **When** le gateway résout la configuration assembly
   **Then** le profil d'exécution est chargé depuis `ExecutionProfileRegistry` via ce ref, avec priorité sur la résolution waterfall par feature

7. **Given** un `ExecutionProfile` est publié et actif
   **When** il est inclus dans le `ResolvedExecutionPlan`
   **Then** les champs `execution_profile_id`, `reasoning_profile`, `verbosity_profile`, `output_mode`, `tool_mode`, `provider`, `model`, `max_output_tokens` apparaissent dans `to_log_dict()` — les paramètres provider traduits (`reasoning_effort`, etc.) sont également loggués séparément sous `translated_provider_params`

## Tasks / Subtasks

- [ ] Créer les types Pydantic pour les profils internes stables (AC: 4, 5)
  - [ ] Créer `backend/app/llm_orchestration/execution_profiles_types.py` :
    - `ReasoningProfile = Literal["off", "light", "medium", "deep"]`
    - `VerbosityProfile = Literal["concise", "balanced", "detailed"]`
    - `OutputMode = Literal["free_text", "structured_json"]`
    - `ToolMode = Literal["none", "optional", "required"]`
  - [ ] Ces types sont **les seules abstractions exposées à l'admin** — pas de `reasoning_effort` brut

- [ ] Créer `ProviderParameterMapper` (scope minimal OpenAI, extensible 66.18) (AC: 1)
  - [ ] Créer `backend/app/llm_orchestration/services/provider_parameter_mapper.py`
  - [ ] `map_for_openai(reasoning_profile, verbosity_profile, output_mode, tool_mode) -> dict` selon D6
  - [ ] La gestion multi-provider et le traitement complet de `verbosity_profile` (instruction textuelle vs contrainte tokens) sont dans le scope de 66.18

- [ ] Créer le modèle DB `ExecutionProfileModel` et la migration Alembic (AC: 1, 4)
  - [ ] Créer `backend/app/infra/db/models/execution_profile.py` avec les profils internes (pas de `reasoning_effort` brut) :
    - `id: uuid.UUID` (PK)
    - `name: str` (label admin)
    - `provider: str`
    - `model: str`
    - `reasoning_profile: str` (default `"off"`)
    - `verbosity_profile: str` (default `"balanced"`)
    - `output_mode: str` (default `"free_text"`)
    - `tool_mode: str` (default `"none"`)
    - `max_output_tokens: int`
    - `timeout_seconds: int`
    - `fallback_profile_id: Optional[uuid.UUID]` (FK → self)
    - `feature: Optional[str]`, `subfeature: Optional[str]`, `plan: Optional[str]`
    - `status: PromptStatus`
    - `created_at: datetime`, `created_by: str`, `published_at: Optional[datetime]`
  - [ ] Créer la migration Alembic
  - [ ] Ajouter au `backend/app/infra/db/models/__init__.py`

- [ ] Créer les modèles Pydantic `ExecutionProfileAdmin` et `ResolvedExecutionProfile` (AC: 4, 5, 7)
  - [ ] `ExecutionProfileAdmin` dans `backend/app/llm_orchestration/admin_models.py` — utilise les types de `execution_profiles_types.py`
  - [ ] Validator `@model_validator(mode="after")` : `reasoning_profile != "off"` et modèle non-reasoning → erreur (réutiliser `is_reasoning_model()`)
  - [ ] `ResolvedExecutionProfile` : version runtime avec `source: Literal["explicit", "waterfall", "fallback_resolve_model"]` + `translated_provider_params: dict` (params OpenAI traduits pour log)

- [ ] Créer `ExecutionProfileRegistry` (AC: 1, 2, 3)
  - [ ] Créer `backend/app/llm_orchestration/services/execution_profile_registry.py`
  - [ ] Implémenter `get_active_profile(feature, subfeature, plan) -> Optional[ExecutionProfileModel]` avec waterfall
  - [ ] Cache invalidation similaire à `AssemblyRegistry`

- [ ] Intégrer dans `gateway._resolve_plan()` (AC: 1, 2, 3, 6)
  - [ ] Modifier `backend/app/llm_orchestration/gateway.py` : après résolution assembly, tenter `ExecutionProfileRegistry.get_active_profile()`
  - [ ] Si profil trouvé → utiliser ses paramètres dans `ResolvedExecutionPlan`
  - [ ] Si profil non trouvé → fallback sur `resolve_model()` avec log
  - [ ] Si `PromptAssemblyConfig.execution_profile_ref` présent → résolution directe par ID

- [ ] Étendre `ResolvedExecutionPlan` (AC: 7)
  - [ ] Ajouter `execution_profile_id: Optional[uuid.UUID]`, `execution_profile_source: str` à `ResolvedExecutionPlan`
  - [ ] Inclure ces champs dans `to_log_dict()`

- [ ] Endpoints admin CRUD `ExecutionProfile` (AC: 4, 5)
  - [ ] Créer `backend/app/routers/admin/execution_profiles.py` avec : list, get, create, update, publish, rollback
  - [ ] Réutiliser le pattern des endpoints `llm_assembly_configs`

- [ ] Tests (toutes AC)
  - [ ] Test unitaire waterfall : feature+subfeature+plan → feature+subfeature → feature → fallback
  - [ ] Test unitaire validator Pydantic : reasoning_effort + non-reasoning model → erreur
  - [ ] Test d'intégration : appel gateway avec feature/plan → profil résolu correctement

## Dev Notes

- **Fichiers principaux à toucher :**
  - `backend/app/infra/db/models/execution_profile.py` (nouveau)
  - `backend/app/llm_orchestration/admin_models.py`
  - `backend/app/llm_orchestration/gateway.py`
  - `backend/app/llm_orchestration/services/execution_profile_registry.py` (nouveau)
  - `backend/app/routers/admin/execution_profiles.py` (nouveau)

- **Non-régression critique :** `resolve_model()` dans `catalog.py` ne doit pas être supprimé. Il devient le fallback de dernier recours. Les use_cases existants qui n'ont pas de `ExecutionProfile` en DB continuent de fonctionner via `resolve_model()`.

- **Story 66.18 complémentaire :** Cette story introduit les profils internes et un mapper OpenAI minimal. La story 66.18 étend le mapper pour le support multi-provider (Anthropic, etc.) et clarifie la gestion de `verbosity_profile` (instruction textuelle injectée dans le prompt vs contrainte `max_output_tokens` provider — les deux aspects sont traités dans 66.18 pour éviter un double effet non contrôlé). Il n'y a **pas de réécriture de modèle** entre 66.11 et 66.18 — la structure DB et les profils internes sont stables dès 66.11.

### References

- [Source: docs/llm-prompt-generation-by-feature.md#Choix du modèle et exécution provider]
- [Source: backend/app/llm_orchestration/gateway.py]
- [Source: backend/app/prompts/catalog.py — resolve_model()]
- [Source: _bmad-output/implementation-artifacts/66-8-catalogue-administrable-composition-llm.md#ExecutionConfigAdmin]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
