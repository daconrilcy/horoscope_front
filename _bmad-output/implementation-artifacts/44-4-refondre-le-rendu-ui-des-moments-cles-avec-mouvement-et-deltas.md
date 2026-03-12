# Story 44.4: Refondre le rendu UI des moments clés avec mouvement et deltas

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur consultant le daily,
I want voir pour chaque bascule quelles forces montent, reculent ou se redistribuent,
so that je comprenne visuellement pourquoi le moment mérite mon attention.

## Acceptance Criteria

1. Chaque carte `Moment clé` peut afficher un bloc `Mouvement` ou `Évolution` basé sur `movement` et `category_deltas`.
2. Le rendu met en avant au maximum les 2 ou 3 variations les plus utiles, avec une hiérarchie claire et sans surcharge mobile.
3. Les catégories ajoutées, retirées ou stabilisées sont distinguées visuellement.
4. Le composant conserve un fallback lisible quand les nouveaux champs ne sont pas présents.
5. Le rendu reste cohérent avec les sections existantes `Pourquoi`, `Transition`, `Implication` et `Impacts`, tout en exposant aussi la cause astrologique et la quantification du mouvement.

## Tasks / Subtasks

- [x] Task 1: Concevoir la hiérarchie visuelle du bloc de mouvement (AC: 1, 2, 5)
  - [x] Ajouter une zone dédiée sous la transition existante
  - [x] Mettre en avant le mouvement global avant les variations locales
  - [x] Limiter l'encombrement sur mobile

- [x] Task 2: Rendre les deltas de catégories lisibles (AC: 2, 3)
  - [x] Afficher les catégories qui montent, reculent ou restent dominantes
  - [x] Utiliser une iconographie ou un marquage simple pour le sens de variation
  - [x] Afficher au plus 2 ou 3 lignes de variation

- [x] Task 3: Préserver les fallbacks et la cohérence produit (AC: 4, 5)
  - [x] Conserver le rendu actuel si `movement` est absent
  - [x] Éviter de dupliquer l'information entre `Transition`, `Mouvement` et `Impacts`
  - [x] Vérifier la cohérence avec l'agenda du jour et les autres blocs du daily

## Dev Notes

- Updated `TurningPointsList.tsx` to include Section 3: Mouvement global.
- Uses `humanizeMovement` for the global trend and `humanizeCategoryDelta` for local variations.
- Variations are limited to the top 2 in the UI to maintain density.
- Section 4 (Implication) and Section 5 (Impacts) remain for complete context.
- Added explicit rendering for:
  - `primary_driver` headline (`Moon square Pluto`)
  - astrological calculation details (`orb`, `phase`, `houses`)
  - measured global movement (`delta_composite`)
  - measured local variations (`delta_score`, `delta_intensity`, `delta_rank`)
- Verified with unit tests in `TurningPointsEnriched.test.tsx`.

### Project Structure Notes

- Frontend principal:
  - `frontend/src/components/prediction/TurningPointsList.tsx`
  - `frontend/src/tests/TurningPointsEnriched.test.tsx`

### Technical Requirements

- Conditional rendering used for `moment.movement`.
- Standardized styling with other sections.

### Architecture Compliance

- Separation of concerns: helpers provide text, components provide layout.

### Completion Notes List

- Movement section implemented in turning point cards.
- Integrated with humanization helpers.
- Primary astro cause and quantified change are now rendered in the card when available.
- The UI still falls back cleanly to legacy or synthesized moments when the enriched payload is absent.
- UI tests updated and passed.

### File List

- `frontend/src/components/prediction/TurningPointsList.tsx`
- `frontend/src/utils/predictionI18n.ts`
- `frontend/src/i18n/predictions.ts`
- `frontend/src/tests/TurningPointsEnriched.test.tsx`
- `frontend/src/tests/TodayPage.test.tsx`
