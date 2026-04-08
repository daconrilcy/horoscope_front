# Story 66.13 : Durcir la gestion des placeholders

Status: ready-for-dev

## Story

En tant qu'**architecte plateforme**,
je veux **classifier les placeholders en required/optional/avec fallback explicite et empêcher qu'un placeholder non résolu survive silencieusement dans le prompt final**,
afin de **garantir qu'aucun appel LLM ne part avec un template partiellement résolu et que les administrateurs peuvent voir précisément l'état de résolution de chaque variable**.

## Intent

Aujourd'hui, `PromptRenderer.render()` remplace les placeholders `{{variable}}` avec les valeurs disponibles dans `user_input + context + common_context`. Si une variable est absente, le placeholder `{{variable}}` reste littéralement dans le prompt envoyé au LLM — silencieusement, sans log structuré, sans blocage.

Cette story corrige ce comportement en trois dimensions :

1. **Classification des placeholders :** chaque placeholder déclaré dans un template doit être classifié comme `required`, `optional`, ou `optional_with_fallback` (valeur par défaut si absente).
2. **Runtime :** log structuré si un placeholder n'est pas résolu, blocage pour les features sensibles, jamais de placeholder brut envoyé au provider.
3. **Preview admin :** afficher l'état résolu/non résolu de chaque placeholder dans la preview de configuration.

## Décisions d'architecture

**D1 — La classification est définie dans `PLACEHOLDER_ALLOWLIST[feature]`.** L'allowlist existante (story 66.8) est étendue pour porter, pour chaque placeholder autorisé, sa classification : `required | optional | optional_with_fallback`.

**D2 — `PromptRenderer.render()` est étendu** pour détecter les placeholders non résolus et les traiter selon leur classification :
- `required` + absent → `PromptRenderError` (exception) pour les features sensibles, log ERROR pour les autres.
- `optional` + absent → suppression du placeholder (remplacé par chaîne vide) + log WARNING.
- `optional_with_fallback` + absent → remplacement par la valeur de fallback + log INFO.

**D3 — La liste des features "sensibles"** (où un placeholder required manquant bloque l'exécution) est configurable dans `PLACEHOLDER_POLICY`. Initialement : `natal`, `guidance_contextual`.

**D4 — `PromptAssemblyPreview` expose le statut de résolution** de chaque placeholder pour la preview admin.

**D5 — La migration des allowlists existantes est progressive.** Les placeholders existants sans classification sont traités comme `optional` par défaut lors de la migration.

## Acceptance Criteria

1. **Given** un template contenant `{{natal_data}}` classifié `required` pour la feature `natal`
   **When** `PromptRenderer.render()` est appelé avec un contexte ne contenant pas `natal_data`
   **Then** une `PromptRenderError` est levée avec le message `"Required placeholder '{{natal_data}}' not resolved for feature 'natal'"` et l'appel LLM n'est pas effectué

2. **Given** un template contenant `{{situation}}` classifié `optional` pour la feature `guidance`
   **When** `PromptRenderer.render()` est appelé sans `situation` dans le contexte
   **Then** `{{situation}}` est remplacé par une chaîne vide dans le prompt résolu, et un log WARNING structuré est émis : `{"event": "placeholder_not_resolved", "placeholder": "situation", "feature": "guidance", "classification": "optional"}`

3. **Given** un template contenant `{{last_user_msg}}` classifié `optional_with_fallback: "[message non disponible]"` pour la feature `chat`
   **When** `PromptRenderer.render()` est appelé sans `last_user_msg`
   **Then** `{{last_user_msg}}` est remplacé par `"[message non disponible]"` dans le prompt résolu, et un log INFO structuré est émis

4. **Given** qu'aucun placeholder non résolu ne doit survivre dans le prompt final
   **When** `PromptRenderer.render()` termine
   **Then** le prompt résolu ne contient aucune occurrence de `{{...}}` — si un placeholder inconnu est détecté (non dans l'allowlist), il est remplacé par chaîne vide en production et un log ERROR est émis : `"Unknown placeholder '{{xyz}}' detected — not in allowlist for feature '{feature}'"`

5. **Given** qu'un admin ouvre la preview d'une configuration assembly pour une feature
   **When** la preview est générée avec un contexte de fixture
   **Then** `PromptAssemblyPreview.placeholder_resolution_status` expose pour chaque placeholder : `name`, `status: resolved|missing_optional|missing_required|fallback_used|unknown`, `value_preview` (10 premiers caractères de la valeur résolue ou `null`) — un placeholder `unknown` (hors allowlist) est affiché avec un badge d'erreur visible dans la preview, **pas absorbé silencieusement**

6. **Given** qu'une feature non sensible a un placeholder `required` non résolu
   **When** `PromptRenderer.render()` est appelé
   **Then** un log ERROR structuré est émis mais l'exécution continue (pas d'exception) — le placeholder est remplacé par chaîne vide — ce comportement moins strict s'applique aux features hors liste `PLACEHOLDER_POLICY.blocking_features`

7. **Given** qu'un admin publie une configuration assembly avec un template contenant un placeholder `required` mais sans valeur de fixture dans la preview
   **When** la preview affiche le statut
   **Then** le placeholder `required` non résolu est mis en évidence avec un badge `"REQUIRED — non résolu"` dans la preview admin

## Tasks / Subtasks

- [ ] Étendre `PLACEHOLDER_ALLOWLIST` avec la classification (AC: 1, 2, 3)
  - [ ] Modifier la structure de `PLACEHOLDER_ALLOWLIST` dans `backend/app/llm_orchestration/assembly_resolver.py` (ou fichier dédié) :
    - Avant : `{"natal": ["natal_data", "chart_json", ...]}`
    - Après : `{"natal": [PlaceholderDef(name="natal_data", classification="required"), PlaceholderDef(name="birth_date", classification="optional_with_fallback", fallback="[date non disponible]"), ...]}`
  - [ ] `PlaceholderDef` : `name: str`, `classification: Literal["required", "optional", "optional_with_fallback"]`, `fallback: Optional[str] = None`
  - [ ] Migrer les placeholders existants avec classification `optional` par défaut

- [ ] Étendre `PromptRenderer.render()` (AC: 1, 2, 3, 4, 6)
  - [ ] Détecter tous les placeholders non résolus après le remplacement initial
  - [ ] Pour chaque placeholder non résolu : appliquer la logique selon classification
  - [ ] Pour les placeholders inconnus (hors allowlist) : remplacer par vide + log ERROR
  - [ ] Garantir l'absence de `{{...}}` dans la chaîne finale retournée

- [ ] Créer `PLACEHOLDER_POLICY` (AC: 1, 6)
  - [ ] Créer dans `backend/app/llm_orchestration/placeholder_policy.py` :
    - `blocking_features: list[str]` = `["natal", "guidance_contextual"]` (placeholder required manquant → exception)
    - Extensible via config

- [ ] Ajouter `placeholder_resolution_status` à `PromptAssemblyPreview` (AC: 5, 7)
  - [ ] Ajouter `PlaceholderResolutionStatus` dans `backend/app/llm_orchestration/admin_models.py` : `name: str, status: Literal["resolved", "missing_optional", "missing_required", "fallback_used"], value_preview: Optional[str]`
  - [ ] Ajouter `placeholder_resolution_status: list[PlaceholderResolutionStatus]` à `PromptAssemblyPreview`
  - [ ] Renseigner ce champ dans `build_assembly_preview()` avec un contexte de fixture

- [ ] Mettre à jour `PromptRenderer.extract_placeholders()` (AC: 5)
  - [ ] Déjà introduit en story 66.8 — s'assurer qu'il retourne aussi la classification depuis l'allowlist

- [ ] Tests (toutes AC)
  - [ ] Test unitaire : placeholder `required` absent + feature sensible → `PromptRenderError`
  - [ ] Test unitaire : placeholder `required` absent + feature non sensible → log ERROR, pas d'exception
  - [ ] Test unitaire : placeholder `optional` absent → chaîne vide + log WARNING
  - [ ] Test unitaire : placeholder `optional_with_fallback` absent → valeur fallback + log INFO
  - [ ] Test unitaire : placeholder inconnu → chaîne vide + log ERROR
  - [ ] Test unitaire : prompt final sans aucun `{{...}}`
  - [ ] Test unitaire preview : `placeholder_resolution_status` correctement renseigné

## Dev Notes

- **Fichiers principaux à toucher :**
  - `backend/app/llm_orchestration/services/assembly_resolver.py` — `PLACEHOLDER_ALLOWLIST` étendu avec classification
  - `backend/app/llm_orchestration/services/prompt_renderer.py` — logique de résolution des placeholders (chemin canonique : `backend/app/llm_orchestration/services/prompt_renderer.py` — **ne pas modifier** `backend/app/prompts/` si ce module existe encore en doublon)
  - `backend/app/llm_orchestration/placeholder_policy.py` (nouveau)
  - `backend/app/llm_orchestration/admin_models.py` — `PlaceholderResolutionStatus`, `PromptAssemblyPreview`
  - `backend/app/llm_orchestration/services/assembly_resolver.py` — `build_assembly_preview()`

- **Chemin canonique du renderer :** `backend/app/llm_orchestration/services/prompt_renderer.py` est le module actif. Si `backend/app/prompts/prompt_renderer.py` existe encore, vérifier s'il est utilisé ; sinon ne pas le modifier pour éviter de toucher le mauvais module.

- **Non-régression :** Les features existantes sans `PLACEHOLDER_ALLOWLIST` explicite (chemin use_case-first) ne doivent pas être affectées. La nouvelle logique ne s'applique qu'au chemin assembly.

- **Attention :** Ne pas élever toutes les features non sensibles en mode bloquant immédiatement. La phase 1 est log + remplacement par vide. Le blocage dur est réservé aux features dans `PLACEHOLDER_POLICY.blocking_features`.

### References

- [Source: docs/llm-prompt-generation-by-feature.md#Couche éditoriale métier]
- [Source: backend/app/llm_orchestration/services/assembly_resolver.py — PLACEHOLDER_ALLOWLIST]
- [Source: _bmad-output/implementation-artifacts/66-8-catalogue-administrable-composition-llm.md#PromptRenderer.extract_placeholders()]
- [Source: backend/app/prompts/prompt_renderer.py]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
