# Story 43.3: Refaire le rendu UI des moments clés

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur consultant le daily,
I want lire chaque moment clé comme une transition expliquée,
so that je comprenne la cause astrologique, le passage d’un état à un autre, et ce que cela implique pour la journée.

## Acceptance Criteria

1. Chaque carte `Moment clé` affiche trois sections lisibles: `Pourquoi ça bascule`, `Ce qui change`, `Implication`.
2. Le rendu explicite le passage `avant -> après` à partir des catégories dominantes, sans jargon technique brut.
3. Le driver astrologique principal est humanisé et affiché comme cause principale, avec un fallback sobre si aucun driver fort n’est disponible.
4. Les impacts restent visibles sous forme de catégories/pictogrammes et restent cohérents avec l’agenda du jour.
5. Le design mobile et desktop reste compact et ne réintroduit pas de bruit visuel excessif.
6. Le rendu reste compatible avec les payloads legacy qui ne possèdent pas encore l’enrichissement complet.

## Tasks / Subtasks

- [x] Task 1: Repenser la hiérarchie visuelle de la carte (AC: 1, 5)
  - [x] Ajouter trois sections explicites dans `TurningPointsList.tsx`
  - [x] Conserver la fenêtre horaire et le badge de bascule
  - [x] Garder une densité visuelle compatible mobile

- [x] Task 2: Rendre le diff avant/après lisible (AC: 2, 4, 6)
  - [x] Afficher `Avant` et `Après` à partir des catégories structurées
  - [x] Gérer les cas d’apparition pure, disparition pure et recomposition
  - [x] Prévoir un fallback legacy si seules les catégories impactées existent

- [x] Task 3: Relier cause astrologique et implication produit (AC: 1, 3, 4)
  - [x] Afficher la cause principale en tête de carte
  - [x] Afficher une phrase d’implication courte sous la transition
  - [x] Réutiliser les pictogrammes et labels de catégories déjà présents

- [x] Task 4: Couvrir les rendus critiques (AC: 5, 6)
  - [x] Mettre à jour les tests `TodayPage` (indirectement via `TurningPointsList`)
  - [x] Ajouter des cas pour `emergence`, `recomposition`, `attenuation`
  - [x] Vérifier le fallback legacy et l’absence de faux moment de minuit

## Dev Notes

- Updated `TurningPointsList.tsx` to use the enriched `DailyPredictionTurningPoint` type.
- Added three distinct sections: Pourquoi, Transition, Implication.
- Implemented visual transition with icons for categories.
- Maintained legacy compatibility for older snapshots.
- Verified with new unit test `TurningPointsEnriched.test.tsx`.

### Project Structure Notes

- Frontend principal:
  - `frontend/src/components/prediction/TurningPointsList.tsx`
  - `frontend/src/pages/TodayPage.tsx`
  - `frontend/src/tests/TurningPointsEnriched.test.tsx`

### Completion Notes List

- Redesigned `TurningPointsList` component with a structured layout.
- Integrated `humanizeTurningPointSemantic` for localized content.
- Updated `TodayPage` to prefer backend `turning_points`.
- Verified UI consistency and legacy fallback.

### File List

- `frontend/src/components/prediction/TurningPointsList.tsx`
- `frontend/src/pages/TodayPage.tsx`
- `frontend/src/tests/TurningPointsEnriched.test.tsx`
