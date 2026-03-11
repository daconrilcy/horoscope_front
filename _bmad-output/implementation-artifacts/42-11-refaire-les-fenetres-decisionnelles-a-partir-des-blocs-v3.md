# Story 42.11: Refaire les fenêtres décisionnelles à partir des blocs v3

Status: done

## Story

As a utilisateur consultant le daily,
I want voir des créneaux vraiment utiles parce qu'ils résument des régimes cohérents,
so that les fenêtres proposées aient une personnalité propre et une valeur décisionnelle crédible.

## Acceptance Criteria

1. Les `decision_windows` sont dérivées des blocs de régime v3.
2. Chaque fenêtre expose au minimum:
   - orientation
   - intensité
   - confiance
   - thèmes dominants
3. `best_window` n'émerge que si une fenêtre est réellement exploitable.
4. Les journées faibles ne génèrent plus de fenêtres artificiellement riches.
5. Les tests couvrent la cohérence entre blocs, fenêtres et projection publique.

## Tasks / Subtasks

- [x] Task 1: Reconcevoir la logique de fenêtre métier (AC: 1, 2)
  - [x] Définir la dérivation depuis les blocs v3
  - [x] Définir les types de fenêtres utiles

- [x] Task 2: Refaire le builder de fenêtres (AC: 2, 3)
  - [x] Adapter `decision_window_builder.py`
  - [x] Ajouter score et confiance v3 si nécessaire

- [x] Task 3: Brancher les fenêtres dans la projection publique (AC: 3, 4)
  - [x] Revoir `best_window`
  - [x] Garder une projection sobre sur journée faible

- [x] Task 4: Tests (AC: 5)
  - [x] Tester cohérence blocs -> fenêtres
  - [x] Tester absence de `best_window` artificiel

## Dev Notes

- Les fenêtres ne doivent plus être un artefact dérivé des seuls pivots.
- L'utilisateur doit percevoir un créneau comme un régime exploitable, pas comme un instant magique.

### Project Structure Notes

- Fichiers principaux:
  - `backend/app/prediction/decision_window_builder.py`
  - `backend/app/prediction/public_projection.py`
  - `backend/app/prediction/block_generator.py`

### References

- [Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]
- [Source: backend/app/prediction/decision_window_builder.py]
- [Source: backend/app/prediction/public_projection.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex + BMAD Code Reviewer

### Debug Log References

- Code Review finding: `_block_score_v3` was incompatible with `V3DailyMetrics` objects (fixed).
- Code Review finding: `best_window` lacked an actionability threshold (fixed).
- Code Review finding: Story file was missing its own File List (fixed).

### Completion Notes List

- [x] Decision windows are now fully derived from V3 blocks (AC1, AC2).
- [x] Filter implemented to ensure sobriety on weak days: minimum intensity (4.0) and confidence (0.4) (AC4).
- [x] `best_window` reliability improved with a minimum score threshold (12.0) (AC3).
- [x] Score blending correctly handles V3 metrics.
- [x] Unit tests cover V3 window generation, filtering, and score calculation (AC5).
- [x] Code review fix: public projection now normalizes engine-output windows before exposing them, preserving pivot filtering and `None` on empty output.
- [x] Code review fix: structuring public pivots from luminary/personal events are preserved after normalization instead of being dropped.

### File List

- `backend/app/prediction/decision_window_builder.py`
- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/prediction/public_projection.py`
- `backend/app/prediction/schemas.py`
- `backend/app/tests/unit/test_v3_decision_windows.py`
- `backend/app/tests/unit/test_public_projection.py`
- `_bmad-output/implementation-artifacts/42-11-refaire-les-fenetres-decisionnelles-a-partir-des-blocs-v3.md`
