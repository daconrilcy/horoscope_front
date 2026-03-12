# Story 44.3: Introduire un wording i18n des variations et de leur intensité

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a frontend architect,
I want traduire les variations de mouvement via i18n à partir des valeurs structurées,
so that les moments clés restent compréhensibles en plusieurs langues sans figer des phrases quantitatives dans le backend.

## Acceptance Criteria

1. Le frontend introduit des clés i18n dédiées pour `direction`, `strength`, `delta` et les formulations de montée, recul, stabilité ou recomposition.
2. Le wording sait produire une version qualitative sobre (`léger`, `net`, `marqué`) sans exposer de chiffres bruts dans la V1 des cartes.
3. Les helpers i18n gèrent FR et EN à partir du même payload structuré.
4. Si des valeurs numériques sont exposées plus tard, elles sont formatées côté frontend selon la locale et jamais concaténées en dur.
5. Les règles de formulation évitent les contradictions du type “ça change” alors que les catégories visibles restent identiques faute de contexte.

## Tasks / Subtasks

- [x] Task 1: Définir les nouvelles clés i18n des variations (AC: 1, 2)
  - [x] Ajouter les libellés de direction `rising`, `falling`, `recomposition`
  - [x] Ajouter les niveaux d'intensité qualitative
  - [x] Ajouter les labels des variations locales par catégorie

- [x] Task 2: Étendre les helpers de composition linguistique (AC: 2, 3, 4, 5)
  - [x] Introduire des helpers purs pour humaniser `movement` et `category_deltas`
  - [x] Supporter un rendu qualitatif sans chiffres et un rendu enrichi si des valeurs sont affichées
  - [x] Centraliser le formatage localisé des nombres

- [x] Task 3: Prévoir des fallbacks cohérents (AC: 3, 5)
  - [x] Gérer les payloads sans `movement`
  - [x] Gérer les payloads avec mouvement global mais sans `category_deltas`
  - [x] Éviter les formulations contradictoires ou redondantes avec la transition existante

## Dev Notes

- Extended `predictions.ts` with `MOVEMENT_DIRECTION_LABELS`, `INTENSITY_LEVEL_LABELS`, and `CATEGORY_VARIATION_LABELS`.
- Implemented `humanizeMovement` and `humanizeCategoryDelta` in `predictionI18n.ts`.
- Strength is mapped to qualitative labels: slight (0-3), notable (3-7), marked (7-10).
- The V1 card keeps movement rendering qualitative and does not expose raw numeric deltas.
- Verified with unit tests in `predictionI18n.test.ts`.

### Project Structure Notes

- Frontend principal:
  - `frontend/src/utils/predictionI18n.ts`
  - `frontend/src/i18n/predictions.ts`
  - `frontend/src/tests/predictionI18n.test.ts`

### Architecture Compliance

- No logic assembling phrases in components.
- Helpers provide localized strings ready for display.

### Testing Requirements

- Unit tests for FR and EN covering qualitative movement and category delta wording.

### Completion Notes List

- i18n keys added for movement and variations.
- Humanization helpers implemented.
- V1 rendering kept intentionally qualitative without raw numbers in the card.
- Unit tests for both French and English translations.

### File List

- `frontend/src/i18n/predictions.ts`
- `frontend/src/utils/predictionI18n.ts`
- `frontend/src/tests/predictionI18n.test.ts`
