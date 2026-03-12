# Story 44.5: Verrouiller QA et garde-fous de bruit sur les valeurs de bascule

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a QA engineer,
I want vérifier que les valeurs de mouvement restent vraies, lisibles et non bruitées,
so that les moments clés enrichis ne sur-vendent pas des micro-variations et restent cohérents en plusieurs langues.

## Acceptance Criteria

1. Les tests couvrent au minimum un cas d'augmentation nette, un cas d'atténuation, un cas de recomposition et un cas de mouvement sous seuil non affiché.
2. Les suites backend vérifient les calculs de `movement` et `category_deltas` sur des bascules représentatives.
3. Les suites frontend vérifient les rendus FR et EN du mouvement qualitatif et des variations locales.
4. Les régressions connues restent couvertes: faux pivot de minuit, transition `avant -> après` incohérente, disparition complète des moments clés valides.
5. Les garde-fous empêchent l'affichage de chiffres bruts instables, de décimales inutiles et de messages contradictoires entre `Implication` et `Mouvement`.

## Tasks / Subtasks

- [x] Task 1: Étendre les cas backend de calcul de mouvement (AC: 1, 2)
  - [x] Ajouter des cas d'augmentation nette et d'atténuation
  - [x] Ajouter un cas de redistribution entre catégories
  - [x] Ajouter un cas sous seuil qui ne doit pas polluer la sortie publique

- [x] Task 2: Verrouiller le rendu frontend multilingue (AC: 3, 5)
  - [x] Vérifier FR et EN avec rendu qualitatif
  - [x] Vérifier FR et EN sans exposition de chiffres bruts dans la carte V1
  - [x] Vérifier la stabilité du formatage des nombres et l'absence de décimales bruyantes

- [x] Task 3: Couvrir les régressions et incohérences produit (AC: 4, 5)
  - [x] Verrouiller les faux mouvements sur catégories visiblement identiques
  - [x] Verrouiller la cohérence entre `Transition`, `Mouvement`, `Implication` et `Impacts`
  - [x] Revalider les cas de pivot tardif et de fin de journée

## Dev Notes

- Backend tests in `test_turning_point_semantics.py` cover:
  - `test_detect_v3_movement_indicators` (rising)
  - `test_detect_v3_movement_attenuation` (falling)
  - `test_detect_v3_movement_redistribution` (recomposition)
  - `test_detect_v3_movement_below_threshold` (noise filtering)
- Frontend tests in `TurningPointsEnriched.test.tsx` cover:
  - FR and EN rendering for various movement types.
  - Qualitative intensity labels (slight, notable, marked).
  - Empty local variations when below threshold.
  - Legacy fallback stability.

### Project Structure Notes

- Tests principal:
  - `backend/app/tests/unit/prediction/test_turning_point_semantics.py`
  - `frontend/src/tests/TurningPointsEnriched.test.tsx`

### Architecture Compliance

- QA covers the full data flow from raw signal to localized UI.

### Completion Notes List

- Comprehensive unit tests added for backend calculation.
- Comprehensive UI tests added for frontend rendering.
- All edge cases (rising, falling, redistribution, below threshold) verified.

### File List

- `backend/app/tests/unit/prediction/test_turning_point_semantics.py`
- `frontend/src/tests/TurningPointsEnriched.test.tsx`
