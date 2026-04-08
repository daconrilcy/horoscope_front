# Story 66.9 : Unifier la doctrine d'abonnement dans la couche LLM

Status: ready-for-dev

## Story

En tant qu'**architecte plateforme**,
je veux **établir une doctrine canonique et appliquée de la façon dont l'abonnement agit sur la composition des prompts LLM**,
afin de **réduire la dette liée aux use_cases dupliqués free/full et d'unifier le point de variation d'abonnement dans le pipeline**.

## Intent

Aujourd'hui, l'abonnement agit de trois façons différentes dans la plateforme LLM :

1. **use_case distinct par plan** — ex: `horoscope_daily_free` vs `horoscope_daily_full`, `natal_long_free` — la différence de plan est encodée dans le nom du use_case et porte un prompt, un modèle et parfois un schéma de sortie distincts.
2. **plan dans l'assembly** — via `PromptAssemblyConfig.plan` et les `plan_rules` — même feature, variation légère par plan sans changer de use_case.
3. **entitlements amont** — contrôle d'accès/quota avant même l'entrée dans le gateway LLM.

La cible de cette story est de :
- **documenter et fixer la doctrine officielle** : `entitlements > plan assembly > use_case distinct` ;
- **identifier les use_cases existants** où la différence free/full n'est qu'une différence de profondeur ou de longueur (pas de contrat de sortie distinct) et qui doivent être migrés vers le mécanisme `plan` assembly ;
- **migrer ces use_cases** vers des `plan_rules` dans `PromptAssemblyConfig` ;
- **ajouter un garde-fou architectural** empêchant la création de nouveaux use_cases dupliqués par plan quand ce n'est pas justifié.

**Cette story ne vise pas à migrer tous les use_cases en une seule fois.** Elle établit la doctrine, identifie les candidats prioritaires, effectue la migration des cas simples (longueur/profondeur seulement), et pose les bases pour les migrations futures.

## Décisions d'architecture

**D1 — Doctrine officielle canonique :**
- `entitlements` = contrôle d'accès avant le gateway ; ne touche pas au prompt.
- `plan` dans `PromptAssemblyConfig` = variation de profondeur, de longueur, de richesse dans le prompt ; même contrat de sortie.
- `use_case distinct par plan` = réservé aux cas où le **contrat de sortie change vraiment** (schéma JSON différent, structure métier différente).

**D2 — Critère de migration :** Un use_case dupliqué par plan est éligible à la migration vers `plan_rules` si et seulement si son contrat de sortie (`output_schema`) est identique à la variante complémentaire.

**D3 — Candidats identifiés (à confirmer dans la codebase) :**
- `horoscope_daily_free` vs `horoscope_daily_full` → différence probable de longueur uniquement → migrable.
- `natal_long_free` → existence d'un `natal_long` standard à confirmer → migrable si schéma identique.
- Les use_cases `natal_*` spécialisés (profil psy, ombre, leadership...) ne sont pas des doublons de plan → non migrables.

**D4 — Le garde-fou architectural** est une validation dans `PromptRegistryV2` ou un lint de catalogue qui détecte les noms de use_case terminant par `_free` ou `_full` et émet un avertissement si aucun `output_schema` différent n'est détecté.

## Acceptance Criteria

1. **Given** un document d'architecture mis à jour
   **When** un développeur cherche comment implémenter une variation d'abonnement dans la couche LLM
   **Then** il trouve la doctrine canonique (`entitlements > plan assembly > use_case distinct`) écrite explicitement dans `docs/llm-prompt-generation-by-feature.md` avec les règles de décision et les exemples

2. **Given** les use_cases `horoscope_daily_free` et `horoscope_daily_full` ont été analysés
   **When** leurs contrats de sortie sont identiques (même schéma JSON ou aucun schéma structuré)
   **Then** la variation free/full est migrée vers une `PromptAssemblyConfig` avec `plan_rules` distincts, et les deux use_cases sont marqués `deprecated` dans le catalogue

3. **Given** le use_case `natal_long_free` a été analysé
   **When** son contrat de sortie est identique à la variante non-free
   **Then** la variation est migrée vers un `plan_rules: free` dans la config assembly `natal`, et le use_case `natal_long_free` est marqué `deprecated`

4. **Given** un admin tente de créer ou publier un nouveau use_case dont le nom se termine par `_free` ou `_full`
   **When** le catalogue est validé (lint ou check au publish)
   **Then** un avertissement explicite est émis : `"use_case suffix '_free'/'_full' detected — prefer plan_rules in PromptAssemblyConfig unless output schema differs"` — le publish n'est pas bloqué mais l'avertissement est loggué

5. **Given** que les use_cases dupliqués sont migrés
   **When** le gateway reçoit une requête portant l'ancien use_case
   **Then** un fallback de compatibilité (mapping `deprecated_use_case → feature + plan`) est résolu sans erreur, avec un log `deprecation_warning` structuré indiquant l'ancien et le nouveau chemin

6. **Given** un use_case dont le contrat de sortie diffère réellement selon le plan (schéma JSON structurellement différent)
   **When** la doctrine est appliquée
   **Then** ce use_case est explicitement maintenu comme use_case distinct et documenté comme tel dans le catalogue avec le flag `plan_differentiation: output_contract`

## Tasks / Subtasks

- [ ] Analyser les use_cases candidats à la migration (AC: 2, 3, 6)
  - [ ] Inspecter `backend/app/prompts/catalog.py` et `PromptRegistryV2` pour lister tous les use_cases contenant `_free` ou `_full`
  - [ ] Pour chaque use_case dupliqué, comparer les `output_schema` dans `LlmOutputSchemaModel` ou les stubs
  - [ ] Classifier : migrable (même schéma) vs non migrable (schéma différent) vs non migrable (structure métier différente)
  - [ ] **Archiver le tableau de classification dans `docs/llm-prompt-generation-by-feature.md`** sous une section dédiée (pas seulement dans le PR — cette décision doit être consultable durablement par tout développeur)

- [ ] Créer les `plan_rules` pour les cas migrables (AC: 2, 3)
  - [ ] Ajouter `plan_rules_free` et `plan_rules_full` (ou `plan_rules_basic`, `plan_rules_premium`) dans `PLAN_RULES_REGISTRY` (`backend/app/llm_orchestration/assembly_resolver.py` ou fichier dédié)
  - [ ] Créer les `PromptAssemblyConfig` correspondantes avec `plan: "free"` et `plan: "premium"` pour les features `horoscope_daily` et `natal` (migration `natal_long_free`)
  - [ ] S'assurer que les plan_rules contiennent uniquement des instructions de longueur/profondeur, pas de logique métier

- [ ] Ajouter le fallback de compatibilité (AC: 5)
  - [ ] Créer un mapping `DEPRECATED_USE_CASE_MAPPING` dans `backend/app/prompts/catalog.py` : `{"horoscope_daily_free": {"feature": "horoscope_daily", "plan": "free"}, ...}`
  - [ ] Dans `gateway._resolve_plan()`, si `use_case` est dans `DEPRECATED_USE_CASE_MAPPING`, rediriger vers assembly avec log structuré `deprecation_warning`
  - [ ] Tests unitaires du fallback

- [ ] Marquer les use_cases migrés comme deprecated (AC: 2, 3)
  - [ ] Ajouter un champ `deprecated: bool` et `deprecation_note: str` dans la structure du catalogue use_case
  - [ ] Marquer les use_cases migrés avec `deprecated: True` et une note pointant vers le nouveau chemin assembly

- [ ] Ajouter le lint de garde-fou (AC: 4)
  - [ ] Créer une fonction `validate_use_case_naming(use_case: str, output_schema: Optional[...]) -> list[str]` dans `backend/app/prompts/validators.py`
  - [ ] Appeler cette validation dans `PromptRegistryV2` au moment du publish
  - [ ] Logger l'avertissement structuré (ne pas bloquer)

- [ ] Mettre à jour la documentation (AC: 1)
  - [ ] Ajouter une section "Doctrine d'abonnement" dans `docs/llm-prompt-generation-by-feature.md` avec la règle canonique, les critères de décision et les exemples de chaque cas
  - [ ] Mettre à jour `_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md` pour refléter la doctrine

- [ ] Tests (toutes AC)
  - [ ] Tests unitaires du mapping de fallback deprecated use_case → assembly
  - [ ] Tests unitaires du lint de garde-fou (use_case `_free`/`_full` sans schéma distinct → warning)
  - [ ] Tests d'intégration : appel avec ancien use_case `horoscope_daily_free` → résolution correcte via assembly `plan: free`

## Dev Notes

- **Fichiers principaux à toucher :**
  - `backend/app/prompts/catalog.py` — ajout du mapping de compatibilité et du champ `deprecated`
  - `backend/app/llm_orchestration/gateway.py` — fallback use_case deprecated → assembly
  - `backend/app/llm_orchestration/assembly_resolver.py` — ajout des plan_rules free/full
  - `backend/app/prompts/validators.py` — nouveau fichier ou module existant pour le lint
  - `docs/llm-prompt-generation-by-feature.md` — doctrine canonique

- **Ne pas casser :** Les use_cases non migrés (ex: `natal_psy_profile`, `chat_astrologer`) ne doivent pas être touchés. Seuls les use_cases identifiés comme doublons de plan avec contrat de sortie identique sont dans le scope.

- **Attention :** La migration effective des prompts en base (`LlmPromptVersionModel`) n'est pas dans le scope de cette story. La story crée les configs assembly et le fallback de routage, mais les prompts en base existants restent intacts (ils continuent d'être servis via le fallback).

### Project Structure Notes

- Les `plan_rules` doivent suivre le pattern déjà établi dans `PLAN_RULES_REGISTRY` (story 66.8)
- Le fallback de compatibilité doit être transparent pour les appelants upstream (services métier)

### References

- [Source: docs/llm-prompt-generation-by-feature.md#Où intervient l'abonnement]
- [Source: _bmad-output/implementation-artifacts/66-8-catalogue-administrable-composition-llm.md]
- [Source: backend/app/llm_orchestration/gateway.py]
- [Source: backend/app/prompts/catalog.py]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

- `backend/app/prompts/catalog.py`
- `backend/app/llm_orchestration/gateway.py`
- `backend/app/llm_orchestration/services/assembly_resolver.py`
- `backend/app/llm_orchestration/services/prompt_registry_v2.py`
- `backend/app/prompts/validators.py`
- `docs/llm-prompt-generation-by-feature.md`
- `_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md`
- `backend/app/llm_orchestration/tests/test_story_66_9_unification.py`
