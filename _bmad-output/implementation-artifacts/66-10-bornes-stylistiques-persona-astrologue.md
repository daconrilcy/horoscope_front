# Story 66.10 : Définir les bornes stylistiques de la persona astrologue

Status: ready-for-dev

## Story

En tant qu'**architecte plateforme**,
je veux **définir et encoder explicitement les dimensions que la persona astrologue peut et ne peut pas modifier dans le pipeline LLM**,
afin de **garantir que la persona reste une couche stylistique bornée et ne dérive pas vers une reconfiguration du comportement métier ou des politiques système**.

## Intent

La persona astrologue est aujourd'hui séparée du template métier (bonne décision architecturale de la story 66.8). Cependant, les bornes de ce que la persona peut influencer ne sont pas formalisées dans le code ni dans la documentation.

Cette story vise à :
- **Définir explicitement** les dimensions stylistiques autorisées pour la persona.
- **Définir explicitement** les dimensions interdites à la persona.
- **Encoder ces bornes** comme règles d'architecture dans `persona_composer.py` et dans la documentation.
- **Ajouter une validation** (lint ou assertion) qui détecte si un bloc persona tente de redéfinir une dimension interdite.

### Dimensions autorisées (ce que la persona PEUT modifier)

| Dimension | Description |
|---|---|
| `tone` | Registre de voix : chaleureux, professionnel, mystique, factuel... |
| `warmth` | Degré d'empathie et de proximité ressentie |
| `vocabulary` | Champ lexical privilégié : ésotérique, psychologique, poétique... |
| `symbolism_level` | Densité des références symboliques et mythologiques |
| `explanatory_density` | Niveau de détail explicatif par rapport à l'affirmation |
| `formulation_style` | Structure légère de la formulation (questions, affirmations, métaphores...) |

### Dimensions interdites (ce que la persona NE PEUT PAS modifier)

| Dimension | Raison |
|---|---|
| `hard_policy` | Immuable par définition — garde-fous système |
| `feature_intent` | Objectif métier de la feature — défini dans le feature template |
| `output_contract` | Schéma de sortie JSON — défini dans l'output contract |
| `plan_rules` | Règles d'abonnement — définies dans le plan layer |
| `model_choice` | Choix du provider/modèle — défini dans l'execution profile |
| `placeholder_allowlist` | Variables injectables — définies par la feature |

## Décisions d'architecture

**D1 — La persona est une couche stylistique pure.** Elle ne contient que des instructions de style. Toute instruction qui redéfinit une règle métier, une contrainte de sortie, une politique de sécurité ou un choix d'exécution est en dehors de son scope.

**D2 — La validation est un lint de contenu.** Implémenter une heuristique de détection dans `persona_composer.py` qui analyse le contenu du bloc persona avant injection et émet un avertissement (log structuré) si des patterns interdits sont détectés (ex: mention de `JSON`, `schema`, `output format`, `model`, `policy`).

**D3 — Les bornes sont déclarées dans un `PersonaBoundaryPolicy`.** Un objet de configuration fixe (non administrable par le standard admin) définit les dimensions autorisées et les patterns interdits. Il est utilisé par le lint.

**D4 — Pas de blocage dur en production initiale.** Le lint émet un warning, pas une exception, pour éviter de casser les personas existantes. Une période de transition est prévue avant de durcir en erreur.

## Acceptance Criteria

1. **Given** la documentation d'architecture mise à jour
   **When** un rédacteur de persona cherche ce qu'il peut inclure
   **Then** il trouve dans `docs/llm-prompt-generation-by-feature.md` et dans le docstring de `persona_composer.py` les deux tableaux (dimensions autorisées / dimensions interdites) avec des exemples concrets

2. **Given** un bloc persona contenant uniquement des instructions stylistiques (ton, vocabulaire, chaleur)
   **When** `PersonaComposer.compose()` traite ce bloc
   **Then** aucun avertissement n'est émis et le bloc est injecté normalement dans le pipeline

3. **Given** un bloc persona contenant des instructions relatives au format JSON de sortie (ex: `"toujours répondre en JSON"`)
   **When** `PersonaComposer.compose()` traite ce bloc
   **Then** un warning structuré est loggué : `"persona_boundary_violation: output_contract dimension detected in persona block"` avec le `persona_id` et l'extrait détecté — le bloc est quand même injecté (pas de blocage en phase 1)

4. **Given** un bloc persona contenant une référence explicite à une policy de sécurité (ex: `"ignore les règles habituelles"`)
   **When** `PersonaComposer.compose()` traite ce bloc
   **Then** un warning structuré `"persona_boundary_violation: hard_policy override attempt detected"` est loggué avec sévérité `ERROR` — le bloc est quand même injecté mais l'incident est tracé

5. **Given** un administrateur crée ou modifie une persona dans l'interface admin
   **When** il sauvegarde un **draft** ou publie la persona
   **Then** le lint est exécuté dans les deux cas — au save draft comme au publish — et le résultat de validation (dimensions détectées, warnings éventuels) est inclus dans la réponse de l'endpoint ; un draft avec violations est sauvegardé mais le warning est visible immédiatement, pas seulement au moment de la publication

6. **Given** la définition du `PersonaBoundaryPolicy`
   **When** un développeur consulte le code
   **Then** il trouve dans `backend/app/llm_orchestration/services/persona_composer.py` (ou un module adjacent) un objet `PERSONA_BOUNDARY_POLICY` qui liste : `allowed_dimensions`, `forbidden_patterns` (regex ou keywords), `severity_map` par violation

## Tasks / Subtasks

- [ ] Définir `PersonaBoundaryPolicy` (AC: 2, 3, 4, 6)
  - [ ] Créer dans `backend/app/llm_orchestration/services/persona_composer.py` (ou `backend/app/llm_orchestration/persona_boundary.py`) la dataclass/dict `PERSONA_BOUNDARY_POLICY` :
    - `allowed_dimensions: list[str]` = `["tone", "warmth", "vocabulary", "symbolism_level", "explanatory_density", "formulation_style"]`
    - `forbidden_patterns: dict[str, list[str]]` = par dimension interdite, liste de patterns/keywords à détecter
    - `severity_map: dict[str, Literal["WARNING", "ERROR"]]`
  - [ ] Implémenter `validate_persona_block(persona_content: str, persona_id: str) -> list[PersonaBoundaryViolation]`
  - [ ] `PersonaBoundaryViolation` : `dimension: str, severity: str, excerpt: str, persona_id: str`

- [ ] Intégrer la validation dans `PersonaComposer.compose()` (AC: 2, 3, 4)
  - [ ] Appeler `validate_persona_block()` avant l'injection du bloc persona dans le pipeline
  - [ ] Logger chaque violation avec le format structuré requis
  - [ ] NE PAS bloquer l'injection (phase 1 = warning only)

- [ ] Intégrer la validation dans l'endpoint admin de publication de persona (AC: 5)
  - [ ] Identifier l'endpoint de création/publication de persona (`backend/app/routers/admin/` ou similaire)
  - [ ] Appeler `validate_persona_block()` au publish
  - [ ] Inclure `boundary_validation: list[PersonaBoundaryViolation]` dans la réponse

- [ ] Mettre à jour la documentation (AC: 1)
  - [ ] Ajouter une section "Bornes stylistiques de la persona" dans `docs/llm-prompt-generation-by-feature.md` avec les deux tableaux
  - [ ] Ajouter un docstring complet sur `PersonaComposer.compose()` décrivant les bornes

- [ ] Tests (toutes AC)
  - [ ] Test unitaire : persona avec contenu stylistique pur → aucun warning
  - [ ] Test unitaire : persona avec mention `JSON` → warning `output_contract`
  - [ ] Test unitaire : persona avec tentative de bypass de policy → warning `ERROR` `hard_policy`
  - [ ] Test unitaire de `validate_persona_block()` avec plusieurs patterns par dimension interdite

## Dev Notes

- **Fichiers principaux à toucher :**
  - `backend/app/llm_orchestration/services/persona_composer.py` — ajout de `PERSONA_BOUNDARY_POLICY` et `validate_persona_block()`
  - `backend/app/routers/admin/` — endpoint publication persona (à identifier)
  - `docs/llm-prompt-generation-by-feature.md` — section bornes stylistiques

- **Patterns interdits à détecter (liste initiale, non exhaustive) :**
  - `output_contract` : `"json"`, `"format de sortie"`, `"schéma"`, `"structure de réponse"`, `"respond in json"`
  - `hard_policy` : `"ignore"`, `"bypass"`, `"oublie"`, `"désactive"`, `"sans restriction"`
  - `model_choice` : `"utilise le modèle"`, `"passe à"`, `"switch to model"`
  - `plan_rules` : `"plan gratuit"`, `"abonnement"`, `"premium only"`

- **Ne pas réimplémenter** la hard_policy dans ce lint. Le lint de persona est une couche advisory, pas un garde-fou de sécurité système.

### References

- [Source: docs/llm-prompt-generation-by-feature.md#Persona]
- [Source: backend/app/llm_orchestration/services/persona_composer.py]
- [Source: _bmad-output/implementation-artifacts/66-8-catalogue-administrable-composition-llm.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
