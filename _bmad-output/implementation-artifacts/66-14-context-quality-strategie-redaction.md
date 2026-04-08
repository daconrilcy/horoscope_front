# Story 66.14 : Utiliser context_quality comme paramètre de stratégie de rédaction

Status: ready-for-dev

## Story

En tant qu'**architecte plateforme**,
je veux **transformer `context_quality` d'un constat d'état passif en un paramètre actif de stratégie de rédaction du prompt**,
afin de **garantir que le système adapte consciemment la rédaction au niveau de contexte disponible, plutôt que de subir silencieusement l'absence d'informations avec une dégradation non contrôlée de la qualité de sortie**.

## Intent

Aujourd'hui, `context_quality = full | partial | minimal` est calculé par `CommonContextBuilder` et exposé dans le contexte enrichi. Mais le pipeline de composition des prompts ne l'utilise pas comme paramètre de stratégie : le même template est rendu quelle que soit la qualité de contexte. La différence de sortie est uniquement due à la présence ou absence de variables injectées.

La cible de cette story est de permettre aux templates et à l'assembly d'adapter leur rédaction selon `context_quality` :
- `full` → prompt riche, toutes les variables disponibles, ton affirmatif.
- `partial` → prompt compensé, mentions explicites des trous, ton plus prudent sur les points manquants.
- `minimal` → prompt pédagogique, moins affirmatif, plus d'ouverture, explication du niveau de certitude limité.

Deux mécanismes sont introduits :
1. **Blocs conditionnels dans les templates** : `{{#if context_quality == "minimal"}}...{{/if}}` (ou équivalent).
2. **Instructions de compensation injectées par `ContextQualityInjector`** : un bloc d'instruction automatique ajouté au developer_prompt selon le niveau de qualité.

## Note d'architecture : ordre canonique des transformations du pipeline de rendu

L'ordre exact des transformations appliquées par `PromptRenderer.render()` après cette story — et après 66.18 (injection verbosity_profile) — est le suivant. Cet ordre est **normatif** et doit être respecté par toute évolution future :

1. **Résolution des blocs conditionnels `context_quality`** — `{{#context_quality:VALUE}}...{{/context_quality}}` activés ou supprimés selon le niveau courant.
2. **Injection de l'instruction de compensation `ContextQualityInjector`** — addendum conditionnel en fin de developer_prompt si le template ne gère pas le niveau explicitement.
3. **Injection de l'instruction de verbosité `verbosity_profile`** — instruction textuelle issue de `ProviderParameterMapper.resolve_verbosity_instruction()`, injectée en fin de developer_prompt par le gateway (story 66.18) ; cette étape a lieu **après** les injections éditoriales et **avant** le rendu des placeholders.
4. **Rendu des placeholders simples** — `{{variable}}` remplacés selon l'allowlist et la classification required/optional/fallback (story 66.13).
5. **Validation finale** — assertion qu'aucun `{{...}}` ne subsiste dans le prompt résolu.

Cet ordre est également appliqué lors de la preview admin avec le niveau `context_quality` simulé. L'étape 3 n'est pas dans le renderer lui-même — elle est appliquée par le gateway **avant** d'appeler `render()` — ce qui évite que le renderer porte une dépendance sur `ExecutionProfile`.

## Décisions d'architecture

**D1 — Deux mécanismes complémentaires, non exclusifs :**
- Les **blocs conditionnels** permettent aux rédacteurs de templates de personnaliser finement le contenu par niveau.
- L'**injector automatique** est un filet de sécurité : si le template ne gère pas explicitement `context_quality`, l'injector ajoute quand même une instruction de base.

**D2 — Syntaxe des blocs conditionnels dans les templates :** `{{#context_quality:minimal}}...{{/context_quality}}` — syntaxe simple, sans logique complexe, étendue dans `PromptRenderer`.

**D3 — `ContextQualityInjector` est configurable par feature** : certaines features (ex: `natal`) ont des instructions de compensation spécifiques ; d'autres ont une instruction générique.

**D4 — `context_quality` est disponible dans le contexte de rendu** via `common_context` (déjà calculé par `CommonContextBuilder`). Aucune modification du contrat d'entrée n'est requise.

**D5 — Les instructions de compensation ne remplacent pas le template métier.** Elles sont injectées en fin de developer_prompt, après les blocs feature/subfeature/plan, comme un addendum conditionnel.

## Acceptance Criteria

1. **Given** un template contenant un bloc conditionnel `{{#context_quality:minimal}}Attention : le contexte natal est incomplet. Formule avec prudence.{{/context_quality}}`
   **When** `PromptRenderer.render()` est appelé avec `context_quality = "minimal"`
   **Then** le bloc est inclus dans le developer_prompt résolu

2. **Given** le même template avec le même bloc conditionnel
   **When** `PromptRenderer.render()` est appelé avec `context_quality = "full"`
   **Then** le bloc conditionnel est absent du developer_prompt résolu (ni le tag ni le contenu)

3. **Given** qu'un template ne contient aucun bloc conditionnel `context_quality`
   **When** `context_quality = "minimal"` et la feature est `natal`
   **Then** `ContextQualityInjector` ajoute automatiquement à la fin du developer_prompt l'instruction générique pour `minimal` : `"[CONTEXTE LIMITÉ] Les données disponibles sont incomplètes. Formule tes interprétations avec prudence et pédagogie, en évitant les affirmations trop catégoriques."`

4. **Given** qu'un template ne contient aucun bloc conditionnel `context_quality`
   **When** `context_quality = "partial"` et la feature est `guidance`
   **Then** `ContextQualityInjector` ajoute l'instruction pour `partial` : `"[CONTEXTE PARTIEL] Certaines informations sont manquantes. Compense les trous en restant cohérent avec les données disponibles."`

5. **Given** que `context_quality = "full"`
   **When** `ContextQualityInjector` est appelé
   **Then** aucune instruction additionnelle n'est injectée (le contexte complet ne nécessite pas de compensation)

6. **Given** qu'un admin ouvre la preview d'une configuration assembly
   **When** il sélectionne un niveau de `context_quality` de simulation (`full`, `partial`, `minimal`)
   **Then** la preview du `rendered_developer_prompt` reflète le niveau sélectionné : blocs conditionnels activés/désactivés et instructions de compensation présentes/absentes

7. **Given** que `context_quality` est `minimal` pour une feature `natal`
   **When** le `ResolvedExecutionPlan` est loggué
   **Then** `context_quality: "minimal"` apparaît dans `to_log_dict()` et le champ `context_quality_instruction_injected: true` indique qu'une instruction de compensation a été ajoutée

8. **Given** que le pipeline de rendu applique ses transformations
   **When** `PromptRenderer.render()` est exécuté sur un template avec blocs conditionnels et placeholders, après enrichissement éventuel du `developer_prompt` par le gateway
   **Then** l'ordre canonique est strictement respecté : (1) résolution des blocs `context_quality`, (2) injection `ContextQualityInjector`, (3) injection de l'instruction `verbosity_profile` par le gateway avant `render()`, (4) rendu des placeholders, (5) validation absence de `{{...}}` — aucun placeholder ne peut être résolu avant qu'un bloc conditionnel soit supprimé, ce qui pourrait laisser des artefacts dans le prompt

## Tasks / Subtasks

- [ ] Étendre `PromptRenderer.render()` pour les blocs conditionnels `context_quality` (AC: 1, 2)
  - [ ] Ajouter dans `backend/app/llm_orchestration/services/prompt_renderer.py` la résolution des blocs `{{#context_quality:VALUE}}...{{/context_quality}}`
  - [ ] La résolution se fait avant le remplacement des autres placeholders
  - [ ] Support des valeurs : `full`, `partial`, `minimal`
  - [ ] Nettoyage complet des tags conditionnels non activés (le tag et son contenu sont supprimés)

- [ ] Créer `ContextQualityInjector` (AC: 3, 4, 5)
  - [ ] Créer `backend/app/llm_orchestration/services/context_quality_injector.py`
  - [ ] `CONTEXT_QUALITY_INSTRUCTIONS: dict[str, dict[str, str]]` — clé : `feature`, valeur : dict `context_quality → instruction`
  - [ ] Instruction générique par défaut pour toutes les features si pas de règle spécifique
  - [ ] `inject(developer_prompt: str, feature: str, context_quality: str) -> str` — retourne le developer_prompt augmenté ou inchangé selon le niveau

- [ ] Intégrer `ContextQualityInjector` dans le pipeline (AC: 3, 4, 5, 7)
  - [ ] Appeler `ContextQualityInjector.inject()` dans `assembly_resolver.resolve_assembly()` après l'assemblage des blocs et l'injection du budget de longueur
  - [ ] Propager `context_quality` dans le `ResolvedAssembly` et `ResolvedExecutionPlan`
  - [ ] Ajouter `context_quality_instruction_injected: bool` à `to_log_dict()`

- [ ] Mettre à jour la preview admin (AC: 6)
  - [ ] Ajouter un sélecteur `context_quality` dans la preview admin (`full|partial|minimal`)
  - [ ] `build_assembly_preview()` accepte un paramètre `simulated_context_quality: str`
  - [ ] Le developer_prompt résolu dans la preview reflète le niveau sélectionné

- [ ] Mettre à jour `CONTEXT_QUALITY_INSTRUCTIONS` pour les features prioritaires (AC: 3, 4)
  - [ ] Définir les instructions spécifiques pour `natal`, `guidance`, `chat`
  - [ ] Instruction générique pour les features non listées

- [ ] Tests (toutes AC)
  - [ ] Test unitaire : bloc conditionnel `{{#context_quality:minimal}}` avec `context_quality="minimal"` → inclus
  - [ ] Test unitaire : bloc conditionnel avec `context_quality="full"` → exclu
  - [ ] Test unitaire `ContextQualityInjector` : `minimal` → instruction injectée
  - [ ] Test unitaire `ContextQualityInjector` : `full` → aucune injection
  - [ ] Test unitaire : template sans bloc conditionnel + `minimal` → injection automatique
  - [ ] Test unitaire : `to_log_dict()` contient `context_quality` et `context_quality_instruction_injected`

## Dev Notes

- **Fichiers principaux à toucher :**
  - `backend/app/llm_orchestration/services/prompt_renderer.py` — blocs conditionnels context_quality
  - `backend/app/llm_orchestration/services/context_quality_injector.py` (nouveau)
  - `backend/app/llm_orchestration/services/assembly_resolver.py` — intégration de l'injector
  - `backend/app/llm_orchestration/gateway.py` — propagation de `context_quality`
  - `backend/app/llm_orchestration/admin_models.py` — `PromptAssemblyPreview` avec sélecteur

- **`context_quality` est déjà calculé** par `CommonContextBuilder` (`backend/app/prompts/common_context.py`) et disponible dans le contexte de rendu. Pas besoin de le recalculer.

- **Ordre canonique dans le developer_prompt final :** blocs feature+subfeature+plan → instruction de longueur (66.12) → instruction de compensation `context_quality` (66.14) → instruction de `verbosity_profile` injectée par le gateway (66.18) → rendu des placeholders utilisateur → validation finale d'absence de `{{...}}`.

- **Ne pas sur-compiler le conditionnel** : la syntaxe `{{#context_quality:VALUE}}` est intentionnellement simple — pas de `else`, pas d'opérateurs logiques. Si des cas plus complexes sont nécessaires, préférer plusieurs blocs.

### References

- [Source: docs/llm-prompt-generation-by-feature.md#Axe orthogonal : qualité de contexte]
- [Source: backend/app/prompts/common_context.py — CommonContextBuilder]
- [Source: backend/app/llm_orchestration/services/prompt_renderer.py]
- [Source: backend/app/llm_orchestration/services/assembly_resolver.py]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

- `backend/app/llm_orchestration/services/prompt_renderer.py`
- `backend/app/llm_orchestration/services/context_quality_injector.py`
- `backend/app/llm_orchestration/services/assembly_resolver.py`
- `backend/app/llm_orchestration/gateway.py`
- `backend/app/llm_orchestration/models.py`
- `backend/app/llm_orchestration/admin_models.py`
- `docs/llm-prompt-generation-by-feature.md`
- `_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md`
- `backend/app/llm_orchestration/tests/test_story_66_14_context_quality.py`
