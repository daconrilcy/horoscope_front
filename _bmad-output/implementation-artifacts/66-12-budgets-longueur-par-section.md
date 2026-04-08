# Story 66.12 : Pilotage des longueurs par section (budgets de longueur)

Status: ready-for-dev

## Story

En tant qu'**administrateur produit**,
je veux **définir des budgets de longueur à trois niveaux (global max, cible de réponse, cible par section métier)** associés à une combinaison feature/subfeature/plan,
afin de **contrôler finement la densité des réponses LLM sans me limiter au seul `max_output_tokens` côté provider**.

## Intent

Aujourd'hui, la longueur des réponses LLM est uniquement contrôlée par `max_output_tokens` dans la configuration d'exécution — c'est un plafond hard côté provider, pas une instruction éditoriale. Résultat :
- La longueur réelle des réponses est très variable selon le modèle et le prompt.
- On ne peut pas dire "la section `résumé` doit faire 2-3 phrases, la section `analyse` doit faire 1-2 paragraphes".
- La différence free/premium sur la longueur n'est pas pilotée de façon cohérente.

Cette story introduit un **système de budgets de longueur** à trois niveaux :
1. `global_max_tokens` — plafond hard (remplace ou complète `max_output_tokens`)
2. `target_response_length` — instruction éditoriale de longueur cible globale (injectée dans le developer_prompt)
3. `section_budgets` — liste de budgets par section métier nommée (injectée dans le developer_prompt par section)

Ces budgets sont portés par un `LengthBudget` embarqué dans `PromptAssemblyConfig` — et **uniquement là**.

## Décisions d'architecture

**D1 — `LengthBudget` vit exclusivement dans `PromptAssemblyConfig`, jamais dans `ExecutionProfile`.** La longueur éditoriale est une propriété de composition et de rendu : elle appartient à la couche de sélection/composition. Le plafond provider (`max_output_tokens`) est une propriété d'exécution : il appartient à `ExecutionProfile`. Mélanger les deux réintroduirait la confusion de responsabilités que l'architecture canonique vise à éliminer. `LengthBudget` est stocké comme champ JSON dans `PromptAssemblyConfigModel`.

**D2 — `global_max_tokens` dans `LengthBudget` écrase `ExecutionProfile.max_output_tokens` uniquement au moment de la résolution finale dans le gateway.** Ce n'est pas `PromptAssemblyConfig` qui modifie `ExecutionProfile` — c'est le gateway qui, lors de la construction de `ResolvedExecutionPlan`, applique cette priorité de façon explicite et loggée. La règle est : si `LengthBudget.global_max_tokens` est défini, il est propagé dans `ResolvedExecutionPlan.max_output_tokens`, quelle que soit la valeur dans `ExecutionProfile`.

**D3 — L'injection dans le prompt est une instruction textuelle résolue.** `LengthBudgetInjector` traduit le `LengthBudget` en instruction textuelle (`"[LONGUEUR] Cible : court (100-150 mots). Section 'résumé' : 2-3 phrases."`) et l'injecte dans le `developer_prompt` résolu, **avant** le rendu des placeholders utilisateur.

**D4 — Les section_budgets sont optionnels.** Si `section_budgets` est vide, seule l'instruction de longueur globale est injectée.

**D5 — La résolution du budget suit la même waterfall que `PromptAssemblyConfig`.** Le budget du plan le plus spécifique (feature+subfeature+plan) s'applique en priorité.

## Acceptance Criteria

1. **Given** un `LengthBudget` défini sur `feature=natal, plan=free` avec `target_response_length="court (100-150 mots)"` et `section_budgets=[{section: "résumé", target: "2-3 phrases"}]`
   **When** le gateway résout la configuration pour cette combinaison
   **Then** le `rendered_developer_prompt` contient une instruction textuelle de longueur : `"Longueur cible : court (100-150 mots). Section 'résumé' : 2-3 phrases."` injectée dans le bloc developer_prompt avant rendu des placeholders

2. **Given** un `LengthBudget` défini sur `feature=natal, plan=premium` avec `target_response_length="approfondi (400-600 mots)"` et `section_budgets` plus riches
   **When** la même feature est appelée avec `plan=premium`
   **Then** l'instruction de longueur injectée reflète le budget premium — la différence de profondeur entre free et premium est contrôlée par cette instruction, pas par deux use_cases distincts

3. **Given** un `LengthBudget` avec `global_max_tokens=800` défini
   **When** le gateway résout le profil d'exécution
   **Then** `max_output_tokens=800` est utilisé dans l'appel provider, même si `ExecutionConfigAdmin.max_output_tokens` est différent

4. **Given** qu'aucun `LengthBudget` n'est défini pour la combinaison courante
   **When** le gateway résout la configuration
   **Then** aucune instruction de longueur n'est injectée dans le developer_prompt — le comportement existant est préservé sans régression

5. **Given** qu'un admin édite la configuration assembly pour une feature/plan
   **When** il ouvre la section "Budget de longueur"
   **Then** il peut définir `target_response_length` (texte libre), `global_max_tokens` (entier optionnel), et une liste de `section_budgets` (nom de section + description de longueur cible)

6. **Given** que la preview admin est ouverte pour une configuration avec `LengthBudget`
   **When** le rendu du developer_prompt est affiché
   **Then** l'instruction de longueur injectée est visible dans le `rendered_developer_prompt` de la preview

7. **Given** qu'un astrologue A a un profil "synthétique" et qu'un astrologue B a un profil "ample"
   **When** la persona est résolue avec un `LengthBudget` issu de la config assembly
   **Then** le budget de longueur s'applique indépendamment de la persona — la persona peut affiner le style mais pas court-circuiter le budget de longueur

## Tasks / Subtasks

- [ ] Créer le modèle Pydantic `LengthBudget` (AC: 1, 2, 3, 4)
  - [ ] Créer dans `backend/app/llm_orchestration/admin_models.py` :
    - `target_response_length: Optional[str]` — description textuelle libre (ex: `"court (100-150 mots)"`)
    - `global_max_tokens: Optional[int]` — plafond hard optionnel
    - `section_budgets: list[SectionBudget]`
  - [ ] `SectionBudget` : `section_name: str`, `target: str` (description textuelle)

- [ ] Ajouter `length_budget: Optional[LengthBudget]` à `PromptAssemblyConfig` (AC: 5)
  - [ ] Modifier `PromptAssemblyConfig` dans `backend/app/llm_orchestration/admin_models.py`
  - [ ] Modifier `PromptAssemblyConfigModel` dans `backend/app/infra/db/models/llm_assembly.py` : ajouter colonne `length_budget: JSON nullable`
  - [ ] Créer la migration Alembic

- [ ] Implémenter `LengthBudgetInjector` (AC: 1, 2, 6)
  - [ ] Créer `backend/app/llm_orchestration/services/length_budget_injector.py`
  - [ ] `resolve_length_instruction(budget: LengthBudget) -> str` — traduit le budget en instruction textuelle
  - [ ] `inject_into_developer_prompt(developer_prompt: str, budget: LengthBudget) -> str` — injecte l'instruction en fin de developer_prompt (avant les placeholders utilisateur)

- [ ] Intégrer dans `assembly_resolver.resolve_assembly()` (AC: 1, 2, 4)
  - [ ] Si `PromptAssemblyConfig` a un `length_budget`, appeler `LengthBudgetInjector.inject_into_developer_prompt()` après l'assemblage des blocs
  - [ ] Si pas de `length_budget`, ne rien injecter (non-régression)

- [ ] Intégrer `global_max_tokens` dans la résolution d'exécution (AC: 3)
  - [ ] Dans `gateway._resolve_plan()`, si `ResolvedAssembly.length_budget.global_max_tokens` est défini, le propager dans `ResolvedExecutionPlan.max_output_tokens` (priorité sur `ExecutionConfigAdmin`)

- [ ] Mettre à jour la preview admin (AC: 6)
  - [ ] L'instruction de longueur injectée doit apparaître dans `PromptAssemblyPreview.rendered_developer_prompt`
  - [ ] Ajouter `length_budget` dans `PromptAssemblyPreview` pour affichage explicite

- [ ] Tests (toutes AC)
  - [ ] Test unitaire `resolve_length_instruction()` : budget avec section_budgets → instruction textuelle correcte
  - [ ] Test unitaire injection dans developer_prompt
  - [ ] Test unitaire : `global_max_tokens` dans budget → priorité sur `ExecutionConfigAdmin.max_output_tokens`
  - [ ] Test unitaire : pas de budget → aucune injection (non-régression)

## Dev Notes

- **Fichiers principaux à toucher :**
  - `backend/app/llm_orchestration/admin_models.py`
  - `backend/app/infra/db/models/llm_assembly.py`
  - `backend/app/llm_orchestration/services/length_budget_injector.py` (nouveau)
  - `backend/app/llm_orchestration/services/assembly_resolver.py`
  - `backend/app/llm_orchestration/gateway.py`

- **Format de l'instruction textuelle injectée :** à définir précisément. Exemple : `"\n\n[LONGUEUR] Cible : court (100-150 mots). Résumé : 2-3 phrases. Analyse : 1 paragraphe."` — utiliser un préfixe reconnaissable pour faciliter le debug.

- **Ne pas confondre** `target_response_length` (instruction éditoriale) et `global_max_tokens` (paramètre hard provider). Les deux peuvent coexister.

- **Story 66.9 complémentaire :** Les budgets de longueur sont le mécanisme recommandé pour remplacer les différences free/full codées dans des use_cases distincts quand la seule différence est la longueur.

### References

- [Source: docs/llm-prompt-generation-by-feature.md#Couche éditoriale métier]
- [Source: backend/app/llm_orchestration/services/assembly_resolver.py]
- [Source: backend/app/llm_orchestration/admin_models.py]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

- `backend/app/llm_orchestration/admin_models.py`
- `backend/app/infra/db/models/llm_assembly.py`
- `backend/app/llm_orchestration/services/length_budget_injector.py`
- `backend/app/llm_orchestration/services/assembly_resolver.py`
- `backend/app/llm_orchestration/gateway.py`
- `docs/llm-prompt-generation-by-feature.md`
- `_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md`
- `backend/app/llm_orchestration/tests/test_story_66_12_length_budgets.py`
- `backend/migrations/versions/5e52f7244424_add_length_budget_to_assembly.py`
