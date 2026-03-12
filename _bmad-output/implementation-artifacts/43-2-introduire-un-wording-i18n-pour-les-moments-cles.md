# Story 43.2: Introduire un wording i18n pour les moments clés

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a frontend architect,
I want composer le wording des moments clés via i18n à partir de données structurées,
so that le français, l’anglais et les futures langues restent cohérents sans figer des phrases métier dans le backend.

## Acceptance Criteria

1. Le backend ne fournit plus le wording final comme source primaire pour les moments clés enrichis.
2. Le frontend introduit des clés i18n dédiées pour les causes astrologiques, les transitions `avant/après`, les libellés d’impact et les implications.
3. Le wording distingue au minimum les cas `emergence`, `recomposition` et `attenuation`.
4. Les règles de formulation couvrent l’absence d’un driver principal, un driver unique et plusieurs drivers secondaires.
5. Les helpers i18n restent centralisés, testables et sans duplication FR/EN hors du dictionnaire de traduction.
6. Les tests frontend couvrent le rendu FR et EN à partir des mêmes données structurées.

## Tasks / Subtasks

- [x] Task 1: Définir les clés i18n dédiées aux moments clés enrichis (AC: 2, 3)
  - [x] Ajouter les clés de labels de sections `why`, `before_after`, `implication`
  - [x] Ajouter les clés de causes astrologiques par type de driver
  - [x] Ajouter les variantes de wording pour `emergence`, `recomposition`, `attenuation`

- [x] Task 2: Centraliser la composition textuelle (AC: 1, 4, 5)
  - [x] Étendre `predictionI18n.ts` avec des helpers purs pour les moments clés enrichis
  - [x] Utiliser des fonctions de composition paramétrées par `change_type` et `primary_driver`
  - [x] Prévoir des fallbacks propres quand certaines données manquent

- [x] Task 3: Garantir la cohérence multilingue (AC: 2, 4, 6)
  - [x] Vérifier que FR et EN couvrent les mêmes cas métier
  - [x] Interdire les chaînes backend brutes dans le rendu final
  - [x] Ajouter des tests ciblés sur les compositions linguistiques

## Dev Notes

- Cette story porte sur la couche linguistique, pas sur la détection métier.
- Le backend fournit désormais un contrat structuré (Story 43.1).
- Added `TURNING_POINT_LABELS` and `DRIVER_TYPE_LABELS` in `predictions.ts`.
- Implemented `humanizeTurningPointSemantic` in `predictionI18n.ts`.

### Project Structure Notes

- Frontend principal:
  - `frontend/src/utils/predictionI18n.ts`
  - `frontend/src/i18n/predictions.ts`
  - `frontend/src/types/dailyPrediction.ts`
  - `frontend/src/tests/predictionI18n.test.ts`

### Technical Requirements

- Les nouvelles clés i18n sont stables et regroupées logiquement.
- Les fonctions de composition prennent des données structurées.
- Les fallbacks préservent une phrase lisible.

### Architecture Compliance

- La localisation reste côté frontend.
- Les composants UI consommeront ces helpers dans la story 43.3.

### Testing Requirements

- Added tests in `predictionI18n.test.ts`:
  - FR `emergence`
  - EN `recomposition`
  - fallback sans driver

### Completion Notes List

- Added i18n keys for turning points and driver types in `frontend/src/i18n/predictions.ts`.
- Implemented `humanizeTurningPointSemantic` helper in `frontend/src/utils/predictionI18n.ts`.
- Updated `DailyPredictionTurningPoint` type in `frontend/src/types/dailyPrediction.ts`.
- Verified with unit tests in `frontend/src/tests/predictionI18n.test.ts`.

### File List

- `frontend/src/i18n/predictions.ts`
- `frontend/src/utils/predictionI18n.ts`
- `frontend/src/types/dailyPrediction.ts`
- `frontend/src/tests/predictionI18n.test.ts`
