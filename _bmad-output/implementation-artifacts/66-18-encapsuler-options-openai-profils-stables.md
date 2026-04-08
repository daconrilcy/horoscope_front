# Story 66.18 : Encapsuler les options OpenAI derrière des profils internes stables

Status: ready-for-dev

## Story

En tant qu'**architecte plateforme**,
je veux **exposer des profils internes stables (reasoning_profile, verbosity_profile, output_mode, tool_mode) au lieu des paramètres OpenAI bruts dans les entités administrables**,
afin de **découpler le système des conventions spécifiques au provider et de permettre un changement de provider sans modifier les configurations de prompt**.

## Contexte de continuité avec 66.11

La story 66.11 a introduit les profils internes stables (`reasoning_profile`, `verbosity_profile`, `output_mode`, `tool_mode`) dans `ExecutionProfile` et un mapper OpenAI minimal. Cette story 66.18 complète ce travail sur deux axes :

1. **Préparation multi-provider** : garder un mapper extensible pour d'autres providers, tout en maintenant **OpenAI comme moteur runtime prioritaire et unique moteur effectivement exécuté** à ce stade.
2. **Clarification de `verbosity_profile`** : préciser exactement comment ce profil agit — une seule source d'effet, pas deux concurrentes.

## Intent

### Traitement de `verbosity_profile` — règle non ambiguë

`verbosity_profile` a deux effets potentiels :
- Une **instruction textuelle** injectée dans le developer_prompt (`"Réponds de façon concise."`)
- Un **`max_output_tokens` recommandé** côté provider

Ces deux effets ne doivent **pas** agir comme deux sources concurrentes non contrôlées. La règle est :

> `verbosity_profile` produit **une instruction textuelle** injectée dans le developer_prompt par `ProviderParameterMapper.resolve_verbosity_instruction()`. Le `max_output_tokens` recommandé associé au profil est utilisé **seulement si** aucun `LengthBudget.global_max_tokens` ni `ExecutionProfile.max_output_tokens` explicite n'est défini. C'est donc un défaut de sécurité, pas une contrainte prioritaire. Le mapper décide de la combinaison — pas deux couches indépendantes.

### Préparation multi-provider

`ProviderParameterMapper` peut exposer des mappings additionnels (ex: Anthropic) pour préparer une extension future. **Cependant, OpenAI reste le moteur prioritaire et le seul moteur effectivement appelé par le gateway en production courante.** Si un profil d'exécution déclare un provider non supporté en runtime, le gateway retombe sur le chemin stable `openai`/`resolve_model()`.

## Décisions d'architecture

**D1 — Les profils internes stables sont définis en 66.11 et ne changent pas ici.** Cette story n'introduit pas de nouveau champ dans `ExecutionProfile` ou `ExecutionProfileAdmin`.

**D2 — `ProviderParameterMapper` est extensible, pas réécrit.** Des mappings supplémentaires peuvent être ajoutés sans changer les profils internes. **Mais l'exécution runtime reste prioritairement OpenAI** tant qu'aucun client provider alternatif n'est intégré de bout en bout.

**D3 — `verbosity_profile` produit une instruction textuelle ET un `max_output_tokens` recommandé, mais le mapper arbitre la priorité** selon la règle de D4.

**D4 — Règle de priorité sur `max_output_tokens` :** `LengthBudget.global_max_tokens` > `ExecutionProfile.max_output_tokens` > `verbosity_profile` default tokens. Le mapper `resolve_verbosity_instruction()` retourne `(instruction_text, Optional[int])` — la valeur `Optional[int]` n'est utilisée par le gateway que si les deux premières sources sont `None`.

**D5 — Rétrocompatibilité avec `ExecutionConfigAdmin` (story 66.8).** `ExecutionConfigAdmin` garde ses champs bruts pour la compatibilité. Une migration progressive vers les profils internes est documentée mais hors scope.

## Acceptance Criteria

1. **Given** qu'un `ExecutionProfile` est configuré avec `provider="openai", reasoning_profile="deep", verbosity_profile="concise"`
   **When** le gateway construit l'appel via `ResponsesClient`
   **Then** `ProviderParameterMapper.map_for_openai()` produit : `reasoning_effort="high"`, `temperature=None` ; `resolve_verbosity_instruction("concise")` retourne l'instruction textuelle de concision qui est injectée dans le developer_prompt **en une seule passe** — il n'y a pas d'injection concurrente depuis deux couches différentes

2. **Given** que `verbosity_profile="concise"` et qu'aucun `LengthBudget.global_max_tokens` ni `ExecutionProfile.max_output_tokens` n'est défini
   **When** le gateway résout `max_output_tokens` final
   **Then** le `max_output_tokens` recommandé par `resolve_verbosity_instruction()` est utilisé comme valeur par défaut de sécurité

3. **Given** que `verbosity_profile="detailed"` et que `LengthBudget.global_max_tokens=800` est défini
   **When** le gateway résout `max_output_tokens` final
   **Then** `max_output_tokens=800` s'applique (priorité LengthBudget) — le `max_output_tokens` recommandé par `verbosity_profile` est ignoré ; seule l'instruction textuelle `"detailed"` est injectée dans le prompt

4. **Given** qu'un `ExecutionProfile` cible un provider non supporté en runtime
   **When** le gateway résout l'exécution
   **Then** le provider runtime effectif est réinitialisé sur `openai`, le modèle repasse par `resolve_model()` et un warning structuré signale le fallback — l'exécution reste stable

5. **Given** qu'un provider inconnu est spécifié dans `ExecutionProfile`
   **When** le gateway tente de mapper les profils internes
   **Then** `ProviderParameterMapper` lève `NotImplementedError: "No parameter mapping for provider: {provider}"` avec suggestion d'ajouter `map_for_{provider}()` — le fallback sur `resolve_model()` est activé

6. **Given** qu'une configuration `ExecutionConfigAdmin` existante (story 66.8) utilise `reasoning_effort="medium"` (champ brut)
   **When** la plateforme est déployée avec cette story
   **Then** les anciens champs bruts dans `ExecutionConfigAdmin` continuent de fonctionner via un chemin de compatibilité — une note de dépréciation est loguée mais pas d'exception

7. **Given** que `reasoning_profile="off"` et `provider="openai"`
   **When** `ProviderParameterMapper.map_for_openai()` est appelé
   **Then** `reasoning_effort` n'est pas inclus dans les paramètres de l'appel et `temperature` est inclus (modèle standard GPT)

## Tasks / Subtasks

- [ ] Garder `ProviderParameterMapper` extensible pour des providers futurs (AC: 4, 5)
  - [ ] Dans `backend/app/llm_orchestration/services/provider_parameter_mapper.py` (créé en 66.11) :
  - [ ] Conserver `map(provider: str, ...) -> dict` extensible
  - [ ] Si le provider n'est pas supporté en runtime, laisser le gateway retomber sur le chemin stable `openai`
  - [ ] La signature de `resolve_verbosity_instruction(verbosity_profile) -> tuple[str, Optional[int]]` est celle définie en 66.11 — s'assurer que le `Optional[int]` (max_tokens recommandé) n'est utilisé qu'en dernier recours selon la règle D4

- [ ] Implémenter la règle de priorité `max_output_tokens` dans le gateway (AC: 2, 3)
  - [ ] Dans `backend/app/llm_orchestration/gateway.py`, lors de la construction de `ResolvedExecutionPlan.max_output_tokens` :
    - Priorité 1 : `LengthBudget.global_max_tokens` (si défini)
    - Priorité 2 : `ExecutionProfile.max_output_tokens` (si défini)
    - Priorité 3 : `resolve_verbosity_instruction()[1]` (default recommandé par verbosity_profile)
  - [ ] Loguer la source utilisée : `max_output_tokens_source: "length_budget" | "execution_profile" | "verbosity_default"`

- [ ] Injecter l'instruction textuelle `verbosity_profile` dans le pipeline (AC: 1)
  - [ ] L'injection est faite par le **gateway** (`gateway._resolve_plan()`) après résolution du profil d'exécution, **avant** l'appel à `PromptRenderer.render()` — le renderer n'a pas de dépendance sur `ExecutionProfile`
  - [ ] Position dans l'ordre canonique des transformations (défini en 66.14) : étape 3, après injections éditoriales (context_quality, ContextQualityInjector) et avant rendu des placeholders
  - [ ] Le developer_prompt augmenté de l'instruction verbosity est passé à `render()` — `render()` ne sait pas que l'instruction a été ajoutée, il traite simplement le texte reçu
  - [ ] Vérifier dans `gateway.py` qu'il n'y a **aucun autre endroit** qui injecte une instruction de verbosité (notamment dans `ResponsesClient`) pour garantir une seule passe

- [ ] Compatibilité `ExecutionConfigAdmin` existant (AC: 6)
  - [ ] Dans le gateway, si le chemin assembly 66.8 est utilisé (sans `ExecutionProfile`), construire un profil interne par inférence depuis `ExecutionConfigAdmin` brut : `reasoning_effort="medium"` → `reasoning_profile="medium"`, etc.
  - [ ] Logger une note de dépréciation structurée

- [ ] Tests (toutes AC)
  - [ ] Test unitaire provider runtime non supporté → fallback cohérent vers `openai`
  - [ ] Test unitaire règle priorité `max_output_tokens` : LengthBudget présent → override verbosity default
  - [ ] Test unitaire : `verbosity_profile="detailed"` + `LengthBudget.global_max_tokens=800` → `max_output_tokens=800`, instruction textuelle `detailed` injectée, pas de double contrainte
  - [ ] Test unitaire : `verbosity_profile="concise"` sans LengthBudget ni ExecutionProfile.max_output_tokens → default tokens recommandé utilisé
  - [ ] Test unitaire `ExecutionConfigAdmin` legacy → inférence profils internes sans exception

## Dev Notes

- **Fichiers principaux à toucher :**
  - `backend/app/llm_orchestration/execution_profiles_types.py` (nouveau)
  - `backend/app/llm_orchestration/services/provider_parameter_mapper.py` (nouveau)
  - `backend/app/llm_orchestration/admin_models.py` — `ExecutionProfileAdmin` mis à jour
  - `backend/app/llm_orchestration/providers/responses_client.py` — intégration mapper
  - `backend/app/llm_orchestration/gateway.py` — compatibilité `ExecutionConfigAdmin` legacy

- **Mapping reasoning_profile → OpenAI reasoning_effort :**
  - `off` → pas de reasoning (modèles standard GPT)
  - `light` → `reasoning_effort="low"` (modèles o-series)
  - `medium` → `reasoning_effort="medium"`
  - `deep` → `reasoning_effort="high"`

- **`verbosity_profile` affecte deux choses :** (1) une instruction textuelle dans le developer_prompt, (2) un `max_output_tokens` recommandé (si `LengthBudget` non défini). Si `LengthBudget` est défini (story 66.12), il prend priorité sur le max_tokens recommandé par verbosity.

- **Story complémentaire 66.11 :** `ExecutionProfile` est l'entité DB créée en 66.11 avec les profils internes stables déjà en place. Cette story 66.18 **n'introduit pas de nouveaux champs dans `ExecutionProfile`** — elle clarifie la règle de priorité `max_output_tokens`, le traitement de `verbosity_profile` et le fait qu'**OpenAI reste le moteur runtime prioritaire**. L'ordre d'implémentation : 66.11 d'abord, puis 66.18 en extension. Pas de churn de modèle DB entre les deux.

### References

- [Source: backend/app/llm_orchestration/providers/responses_client.py]
- [Source: backend/app/llm_orchestration/admin_models.py — ExecutionConfigAdmin]
- [Source: _bmad-output/implementation-artifacts/66-8-catalogue-administrable-composition-llm.md#ExecutionConfigAdmin]
- [Source: _bmad-output/implementation-artifacts/66-11-execution-profiles-administrables.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Implémentation runtime consolidée autour d'OpenAI comme moteur effectivement exécuté ; les providers non supportés ou non implémentés retombent explicitement sur `openai` via `resolve_model()`.
- `response_format.type` a été élargi pour accepter `json_schema`, `json_object` et `text`, afin d'aligner le contrat de plan avec les paramètres traduits par provider.
- La priorité `max_output_tokens` a été stabilisée dans le gateway : `LengthBudget` > `ExecutionProfile.max_output_tokens` > recommandation issue de `verbosity_profile`.
- Régression corrigée après intégration 66.18 : `context_quality_instruction_injected` pouvait rester non initialisé dans `gateway._resolve_plan()` lorsque `feature` était absente ; initialisation défensive ajoutée avant construction de `ResolvedExecutionPlan`.
- Couverture ciblée ajoutée pour le fallback provider (`anthropic` ou provider inconnu) et pour la propagation du mode `json_object`.

### File List

- `backend/app/llm_orchestration/services/provider_parameter_mapper.py`
- `backend/app/llm_orchestration/gateway.py`
- `backend/app/llm_orchestration/models.py`
- `docs/llm-prompt-generation-by-feature.md`
- `_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md`
- `backend/app/llm_orchestration/tests/test_story_66_18_stable_profiles.py`

### Change Log

- 2026-04-08 : Alignement runtime OpenAI prioritaire, fallback cohérent pour provider non supporté, prise en charge `json_object`, et correction de la régression `context_quality_instruction_injected` non initialisé dans le gateway.
