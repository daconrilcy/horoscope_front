# Story 44.2: Calculer et projeter les deltas de mouvement des bascules

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a backend engineer,
I want calculer des deltas de mouvement fiables autour de chaque turning point,
so that les valeurs projetées justifient réellement le passage d'un état à l'autre sans surinterpréter le bruit.

## Acceptance Criteria

1. Le backend calcule `previous_composite`, `next_composite` et `delta_composite` à partir de l'état juste avant et juste après la bascule.
2. Le backend calcule `category_deltas` à partir des catégories dominantes avant/après, avec une règle explicite de tri et de limitation aux variations les plus utiles.
3. Le backend classe le mouvement au minimum entre `upshift`, `downshift` et `redistribution`, de façon cohérente avec `change_type`.
4. Des seuils empêchent d'exposer des micro-variations non significatives comme des mouvements forts.
5. Les journées calmes ou bascules faibles restent rendues sans contradiction entre `change_type`, `transition` et valeurs de mouvement.

## Tasks / Subtasks

- [x] Task 1: Définir la source de calcul des deltas autour d'une bascule (AC: 1, 3)
  - [x] Identifier l'état public ou intermédiaire utilisé juste avant et juste après `occurred_at_local`
  - [x] Définir le calcul de `delta_composite` et de `direction`
  - [x] Garantir un comportement stable sur les bords de journée

- [x] Task 2: Calculer les variations de catégories utiles (AC: 2, 4)
  - [x] Comparer les catégories dominantes avant/après avec une règle déterministe
  - [x] Trier les variations par amplitude absolue
  - [x] Limiter les `category_deltas` aux 2 ou 3 changements les plus utiles

- [x] Task 3: Introduire les garde-fous de bruit métier (AC: 4, 5)
  - [x] Définir des seuils minimaux pour masquer les micro-mouvements
  - [x] Assurer la cohérence entre `change_type`, `direction` et catégories affichées
  - [x] Prévoir un fallback propre quand les variations existent mais restent sous seuil

- [x] Task 4: Projeter les nouvelles valeurs dans le payload public (AC: 1, 2, 3, 5)
  - [x] Alimenter `movement` et `category_deltas` dans la projection publique
  - [x] Conserver la compatibilité des turning points enrichis et legacy
  - [x] Vérifier qu'aucune contradiction visuelle n'est injectée dans les données publiques

## Dev Notes

- Updated `TurningPointDetector.detect_v3` to accept `theme_signals`.
- Implemented `_calculate_movement` and `_calculate_category_deltas` using signal layers.
- Movement direction: `rising` (delta > 0.5), `falling` (delta < -0.5), `recomposition`.
- Category delta threshold: 0.2 (composite delta) to filter noise.
- Limited to top 3 category deltas by absolute intensity.

### Project Structure Notes

- Backend principal:
  - `backend/app/prediction/turning_point_detector.py`
  - `backend/app/prediction/engine_orchestrator.py`
  - `backend/app/prediction/daily_prediction_evidence_builder.py`

### Technical Requirements

- Uses raw composite signals for delta calculation instead of calibrated 0-20 scores to capture real movement.
- Thresholds are applied on raw composite deltas.

### Architecture Compliance

- Calculations are centralized in the detector, which now has access to full signals.

### Testing Requirements

- Unit tests added in `test_turning_point_semantics.py` covering rising movement and noise filtering.

### Previous Story Intelligence

- 41.6 a déjà déplacé les `Moments clés du jour` vers une logique de bascule courte et lisible; cette story doit enrichir la structure, pas revenir aux longues fenêtres ambiguës. [Source: _bmad-output/implementation-artifacts/41-6-refactor-dashboard-moments-cles-et-agenda-du-jour.md]
- 42.16 a fait de l’evidence pack la source de vérité publique; l’enrichissement des bascules doit donc rester aligné avec la projection publique existante. [Source: _bmad-output/implementation-artifacts/42-16-brancher-la-projection-publique-et-la-future-interpretation-sur-l-evidence-pack.md]

### Git Intelligence Summary

- `7d1548b fix(daily): stabilize v3 projection and dashboard moments` a déjà supprimé les faux pivots de minuit côté frontend; le backend doit maintenant exposer une sémantique de changement cohérente avec cette stabilisation.

### Project Context Reference

- Aucun `project-context.md` détecté dans le repo.
- Les règles actives viennent de `AGENTS.md`, des artefacts Epic 41/42 et du contrat daily prediction existant.

### References

- [Source: backend/app/prediction/public_projection.py]
- [Source: backend/app/prediction/daily_prediction_evidence_builder.py]
- [Source: backend/app/prediction/schemas.py]
- [Source: _bmad-output/implementation-artifacts/43-1-structurer-une-semantique-explicable-des-bascules.md]
- [Source: user request 2026-03-12 — “expliquer non seulement quoi change, mais aussi de combien et dans quel sens”]

## Dev Agent Record

### Agent Model Used

GPT-4o

### Debug Log References

- Updated `detect_v3` signature and implementation in `turning_point_detector.py`.
- Updated `engine_orchestrator.py` to pass `theme_signals`.
- Updated `daily_prediction_evidence_builder.py` to map new fields.
- Verified with `pytest backend/app/tests/unit/prediction/test_turning_point_semantics.py`.

### Completion Notes List

- Movement calculation logic implemented.
- Category deltas logic implemented with noise filtering.
- Evidence builder updated to propagate values.
- Orchestrator updated to provide necessary data.

### File List

- `backend/app/prediction/turning_point_detector.py`
- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/prediction/daily_prediction_evidence_builder.py`
- `backend/app/tests/unit/prediction/test_turning_point_semantics.py`
