# Story 66.17 : Formaliser la source de vérité canonique de composition

Status: ready-for-dev

## Story

En tant qu'**architecte plateforme**,
je veux **documenter et encoder dans le code les responsabilités canoniques de chaque entité du pipeline de composition LLM**,
afin de **rendre impossible toute confusion de responsabilité entre couches et de disposer d'un référentiel architectural officiel consultable par tout développeur**.

## Prérequis d'implémentation

> **Cette story doit être implémentée en dernier, après stabilisation complète du pipeline : 66.11–66.15 ET 66.18.** La story 66.18 modifie encore `gateway.py`, `responses_client.py` et les règles `max_output_tokens`. Formaliser et geler la doctrine canonique avant que 66.18 soit stable créerait du churn documentaire et technique (règles à réécrire, guards à ajuster).
>
> **Séquence recommandée :** 66.9 → 66.10 → 66.11 → 66.12 → 66.13 → 66.14 → 66.18 → 66.15 → 66.16 → **66.17**.
>
> **Tâche préalable obligatoire (ajoutée en tête des tasks) :** auditer `gateway.py` et `responses_client.py` pour confirmer qu'aucun champ de `ResolvedExecutionPlan` n'est modifié après sa construction initiale dans `_resolve_plan()`. Documenter les exceptions trouvées et les résoudre avant d'activer le frozen.

## Intent

Le pipeline de composition LLM comporte désormais plusieurs entités avec des responsabilités distinctes. Sans règle explicite, des glissements peuvent se produire :
- Un template métier qui embarque des choix d'exécution.
- Une persona qui redéfinit un contrat de sortie.
- Un plan_rule qui modifie la logique métier plutôt que la profondeur.

Cette story formalise noir sur blanc la répartition des responsabilités et ajoute des guards dans le code pour détecter les violations.

### Doctrine canonique de responsabilité

| Entité | Responsabilité exclusive |
|---|---|
| `PromptAssemblyConfig` | Source de vérité de **sélection et composition** : quelle config s'applique, quels blocs sont actifs, dans quel ordre |
| `LlmPromptVersionModel` | Source de vérité du **contenu des blocs textuels** : feature template, subfeature template, plan rules text |
| `LlmPersonaModel` / `PersonaComposer` | Source de vérité du **style** : ton, vocabulaire, chaleur, densité — rien d'autre |
| `ExecutionProfile` (story 66.11) | Source de vérité de l'**exécution** : provider, modèle, paramètres runtime |
| `ResolvedExecutionPlan` | Source de vérité **runtime finale** : tout ce qui est effectivement envoyé au provider, à l'instant T |

### Guards architecturaux à ajouter

Des assertions ou validations statiques à des points clés du pipeline qui détectent si une entité tente de modifier une responsabilité qui ne lui appartient pas.

## Décisions d'architecture

**D1 — La doctrine est encodée dans un fichier `ARCHITECTURE.md` dédié** dans `backend/app/llm_orchestration/` (ou dans `docs/`), pas seulement dans les docstrings.

**D2 — Les guards sont des assertions légères** (assertions Python ou validators Pydantic), pas des contrôles runtime lourds. Ils sont exécutés au moment de la résolution et de la publication, pas à chaque appel LLM.

**D3 — Les guards détectent les violations les plus courantes** :
- Un `LlmPromptVersionModel` contenant des instructions de `model` ou `provider` (devrait être dans `ExecutionProfile`).
- Une `LlmPersonaModel` contenant des instructions de format JSON (devrait être dans `output_contract`).
- Un `plan_rules` contenant de la logique de sélection de feature (devrait être dans `PromptAssemblyConfig`).

**D4 — La règle de résolution est une règle d'architecture explicite :** `ResolvedExecutionPlan` est la seule source de vérité runtime. Aucun composant downstream (persona_composer, prompt_renderer, responses_client) ne doit modifier la logique de résolution une fois `ResolvedExecutionPlan` construit.

**D5 — Les docstrings sont mis à jour** dans les classes et fonctions pivots pour référencer explicitement la doctrine canonique.

## Acceptance Criteria

1. **Given** qu'un développeur cherche les règles de responsabilité du pipeline LLM
   **When** il consulte `docs/llm-prompt-generation-by-feature.md` ou `backend/app/llm_orchestration/ARCHITECTURE.md`
   **Then** il trouve le tableau canonique des responsabilités, les règles de décision "où mettre X", et les exemples de violations à éviter

2. **Given** qu'un `LlmPromptVersionModel` contient le texte `"use model gpt-4"` ou `"provider: openai"` dans son template
   **When** le lint de publication est exécuté
   **Then** un warning structuré est émis : `"template_content_violation: execution concern detected in prompt template — move to ExecutionProfile"`

3. **Given** qu'une `LlmPersonaModel` contient des instructions relatives au format JSON de sortie
   **When** le lint de publication de persona est exécuté (story 66.10)
   **Then** le guard de persona émet un avertissement complémentaire : `"persona_responsibility_violation: output_contract concern in persona — move to output_contract_ref"`

4. **Given** qu'un `plan_rules` contient une instruction conditionnelle de type `"si premium, utilise la feature X"` (sélection de feature dans les plan_rules)
   **When** le lint de publication de la config assembly est exécuté
   **Then** un warning est émis : `"plan_rules_violation: feature_selection concern in plan_rules — plan_rules must only control depth/length/style, not feature routing"`

5. **Given** que `ResolvedExecutionPlan` est construit par `gateway._resolve_plan()`
   **When** un composant downstream tente de modifier `model`, `provider` ou `output_schema` après la construction
   **Then** une assertion Python détecte la mutation (objet frozen/immutable après construction) et lève `AssertionError` avec message `"ResolvedExecutionPlan is immutable after construction"`

6. **Given** que les docstrings sont mis à jour
   **When** un développeur lit le docstring de `PromptAssemblyConfig`, `LlmPromptVersionModel`, `PersonaComposer`, `ExecutionProfile`, `ResolvedExecutionPlan`
   **Then** chaque docstring contient une ligne `"Source of truth for: <responsabilité>"` et un lien vers `ARCHITECTURE.md`

7. **Given** que la doctrine est formalisée
   **When** le document `docs/llm-prompt-generation-by-feature.md` est mis à jour
   **Then** la section "Doctrine canonique de composition" existante est étendue avec les responsabilités de `ExecutionProfile` (story 66.11) et `LengthBudget` (story 66.12) qui n'existaient pas lors de la rédaction initiale

## Tasks / Subtasks

- [ ] **Audit préalable : vérifier que `ResolvedExecutionPlan` est déjà "build once"** (prérequis AC: 5)
  - [ ] Lire `backend/app/llm_orchestration/gateway.py` intégralement — identifier tout endroit où `ResolvedExecutionPlan` est modifié après sa construction initiale dans `_resolve_plan()`
  - [ ] Vérifier `backend/app/llm_orchestration/providers/responses_client.py` — repair call, fallback, métadonnées finales
  - [ ] Documenter les exceptions trouvées dans un commentaire dans le PR
  - [ ] Résoudre ces exceptions (refactorer pour construire `ResolvedExecutionPlan` en une seule passe) **avant** d'activer le frozen

- [ ] Créer ou mettre à jour `backend/app/llm_orchestration/ARCHITECTURE.md` (AC: 1)
  - [ ] Tableau canonique des 5 entités avec responsabilité exclusive
  - [ ] Section "Règles de décision" : comment choisir où mettre une information
  - [ ] Section "Violations fréquentes à éviter" avec exemples
  - [ ] Section "Ordre de résolution dans le gateway" : diagramme textuel du flux

- [ ] Implémenter le guard de template content (AC: 2)
  - [ ] Dans `backend/app/prompts/validators.py` : créer `validate_template_content(template_text: str) -> list[ArchitectureViolation]`
  - [ ] Patterns interdits dans les templates : références à des modèles spécifiques, instructions de provider
  - [ ] Appeler cette validation dans `PromptRegistryV2` au publish

- [ ] Implémenter le guard de plan_rules (AC: 4)
  - [ ] Créer `validate_plan_rules_content(plan_rules_text: str) -> list[ArchitectureViolation]`
  - [ ] Patterns interdits : conditions de sélection de feature, références à d'autres use_cases
  - [ ] Appeler au publish de `PromptAssemblyConfig`

- [ ] Rendre `ResolvedExecutionPlan` immutable après construction (AC: 5)
  - [ ] Modifier `backend/app/llm_orchestration/models.py` (ou l'endroit où `ResolvedExecutionPlan` est défini) : utiliser `model_config = ConfigDict(frozen=True)` si Pydantic v2, ou équivalent
  - [ ] Vérifier que les composants downstream ne tentent pas de modifier l'objet après construction

- [ ] Mettre à jour les docstrings des classes pivots (AC: 6)
  - [ ] `PromptAssemblyConfig` — `"Source of truth for: prompt composition selection and block activation"`
  - [ ] `LlmPromptVersionModel` — `"Source of truth for: prompt block textual content"`
  - [ ] `PersonaComposer` / `LlmPersonaModel` — `"Source of truth for: stylistic voice and tone"`
  - [ ] `ExecutionProfile` — `"Source of truth for: runtime execution parameters"`
  - [ ] `ResolvedExecutionPlan` — `"Source of truth for: final runtime truth at execution time — immutable after construction"`

- [ ] Mettre à jour `docs/llm-prompt-generation-by-feature.md` (AC: 7)
  - [ ] Étendre la section "Doctrine canonique de composition" avec `ExecutionProfile` et `LengthBudget`
  - [ ] Mettre à jour le schéma récapitulatif de gouvernance
  - [ ] Ajouter la section "Violations à éviter" avec exemples concrets

- [ ] Tests (toutes AC)
  - [ ] Test unitaire `validate_template_content` : template avec `"use model"` → warning
  - [ ] Test unitaire `validate_plan_rules_content` : plan_rules avec sélection de feature → warning
  - [ ] Test unitaire : mutation de `ResolvedExecutionPlan` après construction → `ValidationError` ou `TypeError`

## Dev Notes

- **Fichiers principaux à toucher :**
  - `backend/app/llm_orchestration/ARCHITECTURE.md` (nouveau ou à créer)
  - `backend/app/prompts/validators.py` — nouveaux guards
  - `backend/app/llm_orchestration/models.py` — `ResolvedExecutionPlan` frozen
  - `backend/app/llm_orchestration/admin_models.py` — docstrings
  - `docs/llm-prompt-generation-by-feature.md`

- **`ArchitectureViolation` :** une dataclass simple : `entity: str, violation_type: str, severity: Literal["WARNING", "ERROR"], excerpt: str`.

- **Tous les guards de cette story sont des warnings, pas des blocages.** L'exception est `ResolvedExecutionPlan` frozen — là, une mutation est une erreur de code, pas une configuration invalide.

- **Complémentaire à story 66.10** (bornes persona) : les guards de cette story sont plus généraux et couvrent toutes les entités. La story 66.10 gère spécifiquement le lint de persona.

### References

- [Source: docs/llm-prompt-generation-by-feature.md#Doctrine canonique de composition]
- [Source: docs/llm-prompt-generation-by-feature.md#Source de vérité par couche]
- [Source: backend/app/llm_orchestration/models.py — ResolvedExecutionPlan]
- [Source: _bmad-output/implementation-artifacts/66-8-catalogue-administrable-composition-llm.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
